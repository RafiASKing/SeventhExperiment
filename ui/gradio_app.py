import traceback

# Gradio Chat UI
import sys  # Pastikan tersedia walau gradio sudah terinstall
from contextlib import redirect_stdout
from io import StringIO

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from agent.workflow import app, ensure_model_bound, get_initial_state

try:
    import gradio as gr
except ImportError as e:
    # Fail fast and rely on requirements.txt installation
    raise ImportError(
        "Gradio is not installed. Please install dependencies via 'pip install -r requirements.txt'."
    ) from e

# Kecil: tee stdout agar tetap tampil di console dan juga tertangkap ke buffer
class _TeeIO:
    def __init__(self, *streams):
        self._streams = streams
    def write(self, data):
        for s in self._streams:
            try:
                s.write(data)
            except Exception:
                pass
    def flush(self):
        for s in self._streams:
            try:
                s.flush()
            except Exception:
                pass

def _coerce_content_to_text(content) -> str:
    # Ekstrak hanya teks dari struktur konten (abaikan extras/signature, dll.)
    def _flatten(obj) -> list[str]:
        if obj is None:
            return []
        if isinstance(obj, str):
            return [obj]
        if isinstance(obj, dict):
            # Format umum penyedia: {"type":"text","text":"..."}
            if obj.get("type") == "text" and isinstance(obj.get("text"), str):
                return [obj["text"]]
            # Gemini/LangChain sering taruh teks langsung di "text"
            if isinstance(obj.get("text"), str):
                return [obj["text"]]
            # Beberapa provider menaruh list di "parts"
            parts = obj.get("parts")
            if isinstance(parts, list):
                out: list[str] = []
                for p in parts:
                    out += _flatten(p)
                return out
            # Abaikan metadata lain (extras, citations, dll.)
            return []
        if isinstance(obj, (list, tuple)):
            out: list[str] = []
            for item in obj:
                out += _flatten(item)
            return out
        return [str(obj)]

    parts = [p for p in _flatten(content) if isinstance(p, str) and p.strip()]
    return "\n".join(parts) if parts else "(tidak ada konten)"

# Catatan:
# - Menggunakan state per-sesi via gr.State (tanpa global session store), aman untuk 2–5 user.
# - Tetap mencetak input user dan output agen ke console, plus semua print log dari tools/nodes Anda akan tampil di output notebook/console.

def _compute_output_to_show(final_state) -> str:
    # Reuse logika penentuan output dari loop sebelumnya
    agent_messages = final_state.get("messages", [])
    last_agent_message = agent_messages[-1] if agent_messages else None

    output_to_show = "(Agen tidak memberikan respons)"

    if isinstance(last_agent_message, AIMessage):
        if getattr(last_agent_message, "tool_calls", None):
            # Cek apakah tool call terakhir adalah ask_user (defensif)
            try:
                tc = last_agent_message.tool_calls[-1]
                if tc.get("name") == "ask_user":
                    args = tc.get("args") or {}
                    q = args.get("question")
                    output_to_show = q if isinstance(q, str) and q.strip() else "(Agen sedang memproses...)"
                else:
                    output_to_show = "(Agen sedang memproses...)"
            except Exception:
                output_to_show = "(Agen sedang memproses...)"
        elif getattr(last_agent_message, "content", None):
            # Tampilkan content jika tidak ada tool call (jawaban/konfirmasi final)
            output_to_show = _coerce_content_to_text(last_agent_message.content)
    elif isinstance(last_agent_message, ToolMessage):
        # Jika berakhir di ToolMessage (fallback)
        output_to_show = _coerce_content_to_text(last_agent_message.content)

    return output_to_show


def _extract_tool_debug(messages_slice: list, last_error: str | None = None) -> dict:
    # Kumpulkan semua tool call (AIMessage.tool_calls) dan ToolMessage hasil eksekusi
    events = []
    for m in messages_slice:
        if isinstance(m, AIMessage) and getattr(m, "tool_calls", None):
            for tc in m.tool_calls:
                events.append({
                    "event": "call",
                    "id": tc.get("id"),
                    "name": tc.get("name"),
                    "args": tc.get("args", {}),
                })
        elif isinstance(m, ToolMessage):
            events.append({
                "event": "result",
                "tool_call_id": getattr(m, "tool_call_id", None),
                "content": _coerce_content_to_text(getattr(m, "content", None)),
            })
    return {
        "turn_tool_events": events,   # semua tool events pada turn ini (urut kronologis)
        "last_error": last_error,
    }


def process_message(user_text: str, chat_history: list, state_dict: dict):
    # Pastikan ada state
    if not state_dict:
        state_dict = get_initial_state(force_refresh_movies=True)

    chat_history = chat_history or []

    # Tampilkan input user di console
    print(f"\nAnda: {user_text}")

    # Tambahkan pesan user ke state
    state_dict["messages"].append(HumanMessage(content=user_text))

    # Simpan index awal untuk membedakan pesan baru (turn ini)
    start_index = len(state_dict["messages"])

    # Tanda di console bahwa agen mulai
    print("\nAgen:")

    # Capture semua print dari nodes/tools/graph ke UI, tapi tetap tampil di console
    buf = StringIO()
    tee = _TeeIO(sys.stdout, buf)
    final_state = None
    error_display = None    
    with redirect_stdout(tee):
        try:
            ensure_model_bound()
            final_state = app.invoke(state_dict, {"recursion_limit": 50})
        except Exception as exc:
            traceback.print_exc()
            error_display = f"Maaf, terjadi kesalahan internal: {exc}"

    if error_display:
        print(error_display)
        chat_history.append({"role": "user", "content": user_text})
        chat_history.append({"role": "assistant", "content": error_display})
        logs_md_value = f"```text\n{(buf.getvalue() or '').strip()}\n```"
        return chat_history, state_dict, logs_md_value, {}

    if final_state is None:
        bot_text = "Error: Graph tidak menghasilkan state akhir."
        print(bot_text)
        chat_history.append({"role": "user", "content": user_text})
        chat_history.append({"role": "assistant", "content": bot_text})
        # Log panel juga ditampilkan
        logs_md_value = f"```text\n{(buf.getvalue() or '').strip()}\n```"
        return chat_history, state_dict, logs_md_value, {}

    # Tentukan output yang ditampilkan ke user (kompatibel dengan logika lama)
    bot_text = _compute_output_to_show(final_state)

    # Tampilkan output agen di console
    print(bot_text)

    # Tambahkan ke UI chat
    chat_history.append({"role": "user", "content": user_text})
    chat_history.append({"role": "assistant", "content": bot_text})

    # Ambil semua pesan baru pada turn ini (AIMessage + ToolMessage yang terjadi setelah user)
    messages_slice = (final_state.get("messages", []) or [])[start_index:]

    # Susun log panel dan tool-calls panel
    logs_captured = buf.getvalue()
    logs_md_value = f"```text\n{(logs_captured.strip() or '(tidak ada log)')}\n```"
    tool_debug = _extract_tool_debug(messages_slice, final_state.get("last_error"))

    return chat_history, final_state, logs_md_value, tool_debug

def reset_state():
    # Reset state sesi dan bersihkan riwayat chat
    new_state = get_initial_state(force_refresh_movies=True)
    print("\n[RESET] State direset.")
    return [], new_state


with gr.Blocks(title="Agen Manajer Booking") as demo:
    gr.Markdown("### Agen Manajer Booking\nKetik pesan di bawah untuk memulai.")
    with gr.Row():
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(label="Percakapan", height=420, type="messages")
            with gr.Row():
                txt = gr.Textbox(placeholder="Tulis pesan Anda...", scale=4)
                send = gr.Button("Kirim", variant="primary", scale=1)
                clear = gr.Button("Reset", variant="secondary")
        with gr.Column(scale=2):
            gr.Markdown("#### Agent Instrumentation")
            with gr.Accordion("Agent Logs (stdout dari nodes & tools)", open=False):
                logs_md = gr.Markdown(value="```text\n\n```")
            with gr.Accordion("LangChain / LangGraph - Sequenced Tool Calls", open=True):
                tool_json = gr.JSON(value={})

    # State gradio untuk membawa state graph antar pesan
    state_gr = gr.State(value=None)

    def on_submit(user_text, history, state):
        if not user_text or not user_text.strip():
            # Tidak kirim apa-apa jika kosong
            return history or [], state, gr.update(value=""), "```text\n\n```", {}
        history, state, logs_md_value, tool_debug = process_message(user_text.strip(), history or [], state)
        # Kosongkan textbox setelah kirim
        return history, state, gr.update(value=""), logs_md_value, tool_debug

    # Klik tombol Kirim
    send.click(
        on_submit,
        inputs=[txt, chatbot, state_gr],
        outputs=[chatbot, state_gr, txt, logs_md, tool_json],
    )
    # Tekan Enter di textbox
    txt.submit(
        on_submit,
        inputs=[txt, chatbot, state_gr],
        outputs=[chatbot, state_gr, txt, logs_md, tool_json],
    )

    def on_clear():
        history, state = reset_state()
        return history, state, "```text\n\n```", {}

    # Klik tombol Reset
    clear.click(on_clear, outputs=[chatbot, state_gr, logs_md, tool_json])

# Jalankan UI di notebook; jika di script, akan buka di http://127.0.0.1:7860

# Aktifkan antrian request; gunakan default konfigurasi agar kompatibel dengan versi Gradio terbaru
# Aktifkan antrian request; gunakan fallback agar aman lintas versi Gradio
try:
    demo.queue(default_concurrency_limit=8)
except TypeError:
    demo.queue()


def launch_demo(*, inline: bool = False, share: bool = False, **launch_kwargs):
    """Luncurkan aplikasi Gradio untuk agen manajer booking."""

    return demo.launch(
        inline=inline,
        share=share,
        show_error=True,
        **launch_kwargs,
    )


if __name__ == "__main__":
    launch_demo(inline=True)