import argparse

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from agent.config import get_engine, setup_environment


def _compute_output_to_show(final_state) -> str:
    agent_messages = final_state.get("messages", [])
    last_agent_message = agent_messages[-1] if agent_messages else None

    output_to_show = "(Agen tidak memberikan respons)"

    if isinstance(last_agent_message, AIMessage):
        if getattr(last_agent_message, "tool_calls", None):
            last_tool_call = last_agent_message.tool_calls[-1]
            if last_tool_call["name"] == "ask_user":
                output_to_show = last_tool_call["args"]["question"]
            else:
                output_to_show = "(Agen sedang memproses...)"
        elif getattr(last_agent_message, "content", None):
            output_to_show = str(last_agent_message.content)
    elif isinstance(last_agent_message, ToolMessage):
        output_to_show = str(last_agent_message.content)

    return output_to_show


def run_cli() -> None:
    setup_environment()
    get_engine()
    print("--- Agen Manajer Booking (CLI) ---")
    print("Ketik 'exit' untuk keluar.")
    # Import setelah env siap untuk menghindari ADC default credentials
    from agent.workflow import app, ensure_model_bound, get_initial_state
    ensure_model_bound()
    state = get_initial_state(force_refresh_movies=True)

    while True:
        user_text = input("\nAnda: ").strip()
        if not user_text:
            continue
        if user_text.lower() == "exit":
            print("Sampai jumpa!")
            break

        state["messages"].append(HumanMessage(content=user_text))
        print("\nAgen:")

        final_state = app.invoke(state, {"recursion_limit": 50})
        bot_text = _compute_output_to_show(final_state)
        print(bot_text)

        state = final_state  # lanjutan percakapan gunakan state terbaru


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Tiketa booking agent entrypoint")
    parser.add_argument(
        "--mode",
        choices=("gradio", "cli"),
        default="gradio",
        help="Pilih 'gradio' untuk UI web atau 'cli' untuk mode terminal.",
    )
    parser.add_argument(
        "--share",
        action="store_true",
        help="Gunakan opsi ini untuk membuat public link Gradio.",
    )
    parser.add_argument(
        "--inline",
        action="store_true",
        help="Tampilkan UI secara inline (berguna saat dipanggil dari notebook).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.mode == "cli":
        run_cli()
        return

    setup_environment()
    get_engine()
    from agent.workflow import ensure_model_bound
    ensure_model_bound()
    from ui.gradio_app import launch_demo
    print("--- Agen Manajer Booking (Gradio) ---")
    print("Mengaktifkan antarmuka web di http://127.0.0.1:7860 ...")
    launch_demo(inline=args.inline, share=args.share)


if __name__ == "__main__":
    main()