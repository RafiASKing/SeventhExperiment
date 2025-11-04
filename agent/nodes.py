from typing import Literal

from langchain_core.messages import AIMessage, ToolMessage, SystemMessage, HumanMessage
from sqlalchemy import select

from agent.config import get_engine
from agent.prompts import get_simple_master_prompt
from agent.state import TicketAgentState, get_stable_history_slice
from data.timezone import from_db_utc_naive_to_local_display
from db.schema import movies_table, showtimes_table
from tools.bookings import (
    MovieDetails,
    SeatAvailabilityInfo,
    ask_user,
    book_tickets_tool,
    get_available_seats,
    get_movie_details,
    get_showtimes,
    signal_confirmation_ready,
)

model_with_tools = None


def assign_model(bound_model) -> None:
    global model_with_tools
    model_with_tools = bound_model


def _sanitize_messages_for_gemini(messages):
    """
    Pastikan urutan pesan valid untuk Gemini function calling:
    - Hapus AIMessage di bagian akhir yang tidak memiliki tool_calls,
      supaya turn berikutnya dimulai dari HumanMessage atau ToolMessage.
    """
    msgs = list(messages)
    # Buang semua ekor yang bukan Human/Tool agar turn berikutnya valid untuk function calling
    while msgs and isinstance(msgs[-1], (AIMessage, SystemMessage)):
        msgs.pop()
    return msgs


def node_booking_manager(state: TicketAgentState) -> dict:
    print("--- NODE: Booking Manager ---")

    # 1. Dapatkan HANYA system prompt
    system_prompt_list = get_simple_master_prompt(state)

    # 2. GABUNGKAN system prompt dengan histori chat dari state
    safe_history = get_stable_history_slice(state.get("messages", []), max_messages=72)
    safe_history = _sanitize_messages_for_gemini(safe_history)
    # Fallback guard: jika setelah sanitasi ekor bukan Human/Tool (atau kosong),
    # tambahkan satu pesan terakhir yang valid (Human atau Tool) dari state agar Gemini tidak error.
    if not safe_history or not isinstance(safe_history[-1], (HumanMessage, ToolMessage)):
        original_msgs = state.get("messages", []) or []
        for m in reversed(original_msgs):
            if isinstance(m, (HumanMessage, ToolMessage)):
                # Hindari duplikasi trivial jika sama persis sudah di ekor
                if not safe_history or safe_history[-1] is not m:
                    safe_history.append(m)
                break
    messages_for_llm = system_prompt_list + safe_history

    # Siapkan dictionary untuk update state
    current_summary = state.get("context_seats_summary", "N/A")
    updates = {
        "messages": [],
        "last_error": None, # Sementara gini dulu aja, penanganan error masih agak problem
        "context_seats_summary": current_summary, # Biar konteks kursi tetap terbawa
    }
    ai_response = None

    try:
        # 3. SELALU Panggil LLM untuk Tool Call
        print("     > Meminta Tool Call...")
        if model_with_tools is None:
            raise RuntimeError("model_with_tools belum diinisialisasi. Panggil assign_model() dari workflow terlebih dahulu.")

        ai_response = model_with_tools.invoke(messages_for_llm)
        print(f"     > Hasil LLM (Tool Call): {ai_response.tool_calls}")
        updates["messages"].append(ai_response)

        if not ai_response.tool_calls:
            print(
                "     > Peringatan: LLM tidak memanggil tool (atau mungkin memang tidak perlu)."
            )
            updates["last_error"] = "LLM gagal memanggil tool." # ini dimatikan saja dulu, tidak manggil tool itu normal! 

        # 4. Proses SEMUA tool call
        for tool_call in ai_response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_id = tool_call["id"]

            tool_result_content = "Aksi dicatat."  # Default untuk tool aksi

            if tool_name == "record_selected_movie":
                selected_id = tool_args.get("selected_movie_id")
                if selected_id is not None:
                    updates["current_movie_id"] = selected_id
                    # Reset konteks bawahan
                    updates["context_showtimes"] = None
                    updates["current_showtime_id"] = None
                    updates["context_seats"] = None
                    updates["selected_seats"] = None
                    updates["context_seats_summary"] = "N/A"

            elif tool_name == "record_selected_showtime":
                selected_id = tool_args.get("selected_showtime_id")
                if selected_id is not None:
                    updates["current_showtime_id"] = selected_id
                    updates["context_seats"] = None
                    updates["selected_seats"] = None
                    updates["context_seats_summary"] = "N/A"

            elif tool_name == "record_selected_seats":
                seats_list = tool_args.get("selected_seats_list")
                if seats_list:
                    updates["selected_seats"] = (
                        seats_list
                    )
                else:
                    updates["last_error"] = "Agent mencoba rekam kursi kosong."
                    tool_result_content = "Error: Daftar kursi kosong."

            elif tool_name == "record_customer_name":
                name = tool_args.get("extracted_customer_name")
                if name:
                    updates["customer_name"] = name


            elif tool_name == "get_showtimes":
                try:
                    # EKSEKUSI tool-nya SEKARANG
                    showtimes_result = get_showtimes.invoke(tool_args)
                    updates["context_showtimes"] = showtimes_result  # Simpan konteks
                    tool_result_content = str(showtimes_result)
                except Exception as e:
                    updates["last_error"] = f"Gagal fetch showtimes: {e}"
                    tool_result_content = f"Error: {e}"
                    updates["context_showtimes"] = [
                        {"error": str(e)}
                    ]

            elif tool_name == "get_available_seats":
                try:
                    # EKSEKUSI tool-nya SEKARANG
                    seat_info: SeatAvailabilityInfo = get_available_seats.invoke(
                        tool_args
                    )
                    updates["context_seats"] = seat_info.available_list
                    updates["context_seats_summary"] = seat_info.summary_for_llm
                    tool_result_content = str(seat_info.model_dump())
                except Exception as e:
                    updates["last_error"] = f"Gagal fetch seats: {e}"
                    updates["context_seats_summary"] = "Error ambil kursi."
                    tool_result_content = f"Error: {e}"

            elif tool_name == "get_movie_details":
                # Eksekusi tool dan kirim hasilnya ke LLM sebagai ToolMessage
                try:
                    details: MovieDetails = get_movie_details.invoke(tool_args)
                    # Kirim payload lengkap agar LLM bisa menyusun jawaban/ask_user berikutnya
                    tool_result_content = str(details.model_dump())
                except Exception as e:
                    updates["last_error"] = f"Gagal fetch movie details: {e}"
                    tool_result_content = f"Error: {e}"

            elif tool_name == "ask_user":
                # EKSEKUSI tool-nya SEKARANG
                tool_result_content = ask_user.invoke(tool_args)
                # Router akan menangani __end__

            elif tool_name == "signal_confirmation_ready":
                # EKSEKUSI tool-nya SEKARANG
                tool_result_content = signal_confirmation_ready.invoke(tool_args)
                # Router akan menangani 'confirm'

            updates["messages"].append(
                ToolMessage(content=tool_result_content, tool_call_id=tool_id)
            )

    except Exception as e:
        print(f"     > ERROR saat pemanggilan LLM: {e}")
        updates["last_error"] = f"Gagal memproses langkah: {e}"
        if ai_response is None:
            error_msg = AIMessage(content=f"Maaf, terjadi error internal: {e}")
            updates["messages"].append(error_msg)

    return updates

def node_confirmation(state: TicketAgentState) -> dict:
    """
    Mengambil data DARI STATE, menampilkan rangkuman, dan mengeksekusi booking.
    Dipicu HANYA setelah tool 'signal_confirmation_ready' dipanggil.
    """
    print("--- NODE: Confirmation ---")

    movie_id = state.get("current_movie_id")
    showtime_id = state.get("current_showtime_id")
    seats = state.get("selected_seats")
    customer_name = state.get("customer_name")

    final_data = {
        "movie_id": movie_id,
        "showtime_id": showtime_id,
        "seats": seats,
        "customer_name": customer_name,
    }

    if not all(final_data.values()):  # Cek jika salah satu masih None
        print(
            f"    > ERROR: Data konfirmasi tidak lengkap di state! Data: {final_data}"
        )
        return {
            "messages": [
                AIMessage(
                    content=f"Terjadi error: Data pemesanan tidak lengkap untuk konfirmasi. Data: {final_data}"
                )
            ],
            "last_error": "Data tidak lengkap saat konfirmasi.",
        }

    # 2. Ambil detail (Nama film, Waktu tampil) untuk rangkuman
    # (Ini butuh query kecil ke DB)
    movie_title = "(Judul tidak ditemukan)"
    showtime_display = "(Jadwal tidak ditemukan)"
    try:
        engine = get_engine()
        with engine.connect() as conn:
            # Ambil judul film
            movie_res = conn.execute(
                select(movies_table.c.title).where(
                    movies_table.c.id == final_data["movie_id"]
                )
            ).first()
            if movie_res:
                movie_title = movie_res.title

            # Ambil waktu jadwal (dan konversi ke WIB display)
            showtime_res = conn.execute(
                select(showtimes_table.c.time).where(
                    showtimes_table.c.id == final_data["showtime_id"]
                )
            ).first()
            if showtime_res:
                showtime_display = from_db_utc_naive_to_local_display(showtime_res.time)

    except Exception as e:
        print(f"    > ERROR saat mengambil detail untuk konfirmasi: {e}")

    # 3. Buat Rangkuman Teks
    summary = (
        f"✅ **Konfirmasi Pesanan Anda:**\n"
        f"---------------------------\n"
        f"🎬 **Film:** {movie_title} (ID: {final_data['movie_id']})\n"
        f"🗓️ **Jadwal:** {showtime_display} (ID: {final_data['showtime_id']})\n"
        f"💺 **Kursi:** {', '.join(final_data['seats'])}\n"
        f"👤 **Atas Nama:** {final_data['customer_name']}\n"
        f"---------------------------\n"
        f"\n⏳ Memproses pemesanan..."
    )
    # Tampilkan rangkuman ke konsol (opsional)
    print(f"    > Rangkuman:\n{summary}")

    # 4. Eksekusi Booking (Panggil fungsi Python biasa)
    result_message = book_tickets_tool(
        showtime_id=final_data["showtime_id"],
        seats=final_data["seats"],
        customer_name=final_data["customer_name"],
    )

    print(f"    > Hasil Eksekusi: {result_message}")

    # 5. Kembalikan Pesan Final ke User
    booking_url = f"https://tiketa-rafi.space/book/{final_data['showtime_id']}"
    final_response = (
        f"{summary}\n\n"
        f"**Status:** {result_message}\n\n"
        f"🔗 Buka halaman showtime: {booking_url}\n"
        f"[Klik di sini untuk membuka]({booking_url})"
    )

    # Reset state setelah booking
    updates = {
        "messages": [AIMessage(content=final_response)],
        "current_movie_id": None,
        "current_showtime_id": None,
        "selected_seats": None,
        # "customer_name": None,
        "context_showtimes": None,
        "context_seats": None,
        "confirmation_data": None,
        "last_error": None,
    }
    return updates

def booking_router(
    state: TicketAgentState,
) -> Literal["confirm", "continue", "__end__"]:
    print("--- ROUTER: Booking Router ---")

    if state.get("last_error"):
        print(f"    > Rute: __end__ (ERROR terdeteksi: {state.get('last_error')})")
        return "__end__"

    messages = state["messages"]
    last_ai_message = None
    for msg in reversed(messages):
        if isinstance(msg, AIMessage):
            last_ai_message = msg
            break

    if not last_ai_message or not last_ai_message.tool_calls:
        print("    > Rute: __end__ (NO_TOOL_CALL / LLM bandel)")
        return "__end__"

    # Ambil tool call *pertama* (atau terakhir, tergantung logikamu)
    tool_call = last_ai_message.tool_calls[0]
    tool_name = tool_call["name"]

    if tool_name == "signal_confirmation_ready":
        print("    > Rute: confirm (data lengkap)")
        return "confirm"
    elif tool_name == "ask_user":
        print("    > Rute: __end__ (menunggu input user)")
        return "__end__"
    else:
        # Ini adalah tool Aksi (record_...) ATAU tool Data (get_...)
        print(f"    > Rute: continue (Aksi/Tool '{tool_name}' dipanggil, lanjut loop)")
        return "continue"