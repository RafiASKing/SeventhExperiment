from typing import List

from langchain_core.messages import AnyMessage, SystemMessage

from agent.state import TicketAgentState
from data.seats import SEAT_MAP
from data.timezone import get_current_local_date_str


def get_focus_instruction(state: TicketAgentState) -> str:
    """
    Menentukan instruksi fokus yang FLEKSIBEL, memberi LLM pilihan
    antara aksi (record) atau bertanya (ask_user).
    """

    # --- SLOT 1: current_movie_id ---
    if not state.get("current_movie_id"):
        return (
            "FOKUS SAAT INI: Selesaikan 'current_movie_id'. "
            "Jika user sudah jelas memilih film (dari 'DAFTAR FILM TERSEDIA'), panggil 'record_selected_movie'. "
            "Jika belum jelas atau perlu bantuan, WAJIB panggil 'ask_user' (tampilkan daftar & bertanya). DEFAULT -> ask_user."
        )

    # --- SLOT 2: current_showtime_id ---
    if not state.get("current_showtime_id"):
        context_showtimes = state.get("context_showtimes")

        if not context_showtimes:
            return (
                "FOKUS SAAT INI: Dapatkan jadwal. "
                "User HARUS menyebut TANGGAL pemutaran. Anda BOLEH menerima frasa relatif seperti 'hari ini', "
                "'besok', atau 'lusa' (termasuk hari dalam minggu, mis. 'Senin depan'). "
                "Hitung sendiri tanggal 'YYYY-MM-DD' berdasarkan 'KONTEKS WAKTU SAAT INI'. "
                "Jika tanggal belum jelas, WAJIB panggil 'ask_user' untuk meminta tanggal (boleh relatif) (DEFAULT). "
                "Jika tanggal sudah jelas, panggil 'get_showtimes(movie_id, date_local)'."
            )

        if (
            isinstance(context_showtimes, list)
            and len(context_showtimes) > 0
            and isinstance(context_showtimes[0], dict)
            and ("error" in context_showtimes[0] or "message" in context_showtimes[0])
        ):
            return (
                "FOKUS SAAT INI: Jadwal tidak ditemukan atau error. "
                "WAJIB panggil 'ask_user' untuk memberi tahu & minta tanggal lain (DEFAULT)."
            )

        return (
            "FOKUS SAAT INI: Tentukan 'current_showtime_id'. "
            "Jika user sudah jelas memilih, panggil 'record_selected_showtime'. "
            "Jika perlu klarifikasi, WAJIB panggil 'ask_user' (DEFAULT)."
        )

    # --- SLOT 3: selected_seats ---
    if not state.get("selected_seats"):
        context_seats_summary = state.get("context_seats_summary", "N/A")

        if context_seats_summary == "N/A":
            return (
                "FOKUS SAAT INI: Dapatkan info kursi. "
                "WAJIB panggil 'get_available_seats' untuk mengambil ringkasan kursi."
            )

        if (
            "Error:" in context_seats_summary
            or "0 kursi tersedia" in context_seats_summary
        ):
            return (
                "FOKUS SAAT INI: Kursi tidak tersedia atau error. "
                "WAJIB panggil 'ask_user' untuk memberi tahu & sarankan opsi (DEFAULT)."
            )

        return (
            "FOKUS SAAT INI: Tentukan 'selected_seats'. "
            "Perhatikan PETA KURSI: Format kursi yang valid adalah huruf KAPITAL diikuti angka (misal: 'A1', 'B2'). "
            "Lakukan kognisi: Jika user mengetik 'a1' atau 'kursi b2', Anda WAJIB menafsirkannya dan memanggil 'record_selected_seats' dengan format yang benar dan tervalidasi (misal: ['A1', 'B2']). "
            "Periksa juga 'Kursi Tersedia' di PETA KURSI untuk memastikan kursi yang dipilih user belum terisi. "
            "Jika user memilih kursi yang SUDAH TERISI, WAJIB panggil 'ask_user' untuk memberi tahu (misal: 'Maaf, kursi B2 sudah terisi. Silakan pilih kursi lain.'). "
            "Jika user deskriptif/tidak pasti (misal: 'kursi depan paling tengah!'), WAJIB panggil 'ask_user' untuk saran/klarifikasi (misal: 'apakah yang kamu maksud kursi pada baris M9 atau M10?') (DEFAULT)."
        )

    # --- SLOT 4: customer_name ---
    if not state.get('customer_name'):
        return (
            "FOKUS SAAT INI: Tentukan 'customer_name'. "
            "PERIKSA HISTORI CHAT DENGAN TELITI. "
            "1. Jika user SUDAH JELAS menyebutkan namanya (misal: 'atas nama Budi', 'nama saya Budi'), panggil tool `record_customer_name(extracted_customer_name='Budi')`. "
            "2. Jika user memberi petunjuk nama TAPI ANDA TIDAK 100% YAKIN (misal: 'Budi di sini'), WAJIB panggil 'ask_user' untuk KONFIRMASI (misal: 'Untuk konfirmasi, pemesanan ini atas nama Budi?'). "
            "3. Jika TIDAK ADA NAMA SAMA SEKALI, WAJIB panggil 'ask_user' untuk MINTA NAMA (misal: 'Baik, pemesanan ini atas nama siapa?') (DEFAULT)."
        )

    return "FOKUS SAAT INI: Semua formulir sudah terisi. WAJIB panggil 'signal_confirmation_ready'."

def get_simple_master_prompt(state: TicketAgentState) -> List[AnyMessage]:
    """
    Merakit System Prompt LENGKAP dengan aturan, konteks, dan pengecualian.
    """

    # --- 1. Ambil Semua Data Konteks ---
    all_movies = state.get("all_movies_list", [])
    showtime_list = state.get("context_showtimes", [])
    movie_id = state.get("current_movie_id")
    showtime_id = state.get("current_showtime_id")
    seats = state.get("selected_seats")
    customer = state.get("customer_name")

    today_date_str = get_current_local_date_str()
    
    # 1. Movie Display
    movie_display = "BELUM ADA"
    if movie_id:
        movie_title = " (Judul Tidak Ditemukan)" # Fallback
        # Cari film di all_movies_list
        for movie in all_movies:
            if movie.get('id') == movie_id:
                movie_title = f" (Judul: {movie.get('title', 'N/A')})"
                break
        movie_display = f"{movie_id}{movie_title}"

    # 2. Showtime Display
    showtime_display = "BELUM ADA"
    if showtime_id:
        showtime_time = " (Waktu Tidak Ditemukan)" # Fallback
        # Cari jadwal di context_showtimes
        if showtime_list and isinstance(showtime_list[0], dict) and 'showtime_id' in showtime_list[0]:
            for st in showtime_list:
                if st.get('showtime_id') == showtime_id:
                    showtime_time = f" (Waktu: {st.get('time_display', 'N/A')})"
                    break
        showtime_display = f"{showtime_id}{showtime_time}"
        
    # 3. Seats Display
    seats_display = "BELUM ADA"
    if seats:
        # Ubah list ['A1', 'A2'] menjadi string "A1, A2"
        seats_display = ", ".join(seats)

    movie_list_str = "\n".join(
        [
            f"- ID: {m['id']}, Judul: {m['title']}"
            for m in state.get("all_movies_list", [])
        ]
    )
    if not movie_list_str:
        movie_list_str = "Error: Daftar film tidak ter-load."

    showtime_list = state.get("context_showtimes", [])
    showtime_context_str = "N/A (Panggil 'get_showtimes' dulu)"
    if showtime_list:
        if isinstance(showtime_list[0], dict) and "error" in showtime_list[0]:
            showtime_context_str = f"Error: {showtime_list[0]['error']}"
        elif isinstance(showtime_list[0], dict) and "message" in showtime_list[0]:
            showtime_context_str = showtime_list[0]["message"]
        else:
            showtime_context_str = "\n".join(
                [
                    f"- ID: {s['showtime_id']}, Waktu: {s['time_display']}"
                    for s in showtime_list
                ]
            )

    seat_context_str = state.get(
        "context_seats_summary", "N/A (Panggil 'get_available_seats' dulu)"
    )

    # --- 2. Dapatkan Instruksi Fokus ---
    focus_instruction = get_focus_instruction(state)

    # --- 3. Rakit Peta Kursi ---
    seat_map_str_lines = []
    for row_list in SEAT_MAP:
        row_str = " ".join([seat if seat else "____" for seat in row_list])
        seat_map_str_lines.append(row_str)
    seat_map_context_str = "\n".join(seat_map_str_lines)

    # --- 3. Rakit Prompt ---
    prompt_lines = [
        "Anda adalah Manajer Booking. Tugas Anda mengisi formulir.",
        "Prioritas UTAMA Anda adalah menyelesaikan `INSTRUKSI FOKUS`.",
        "Anda WAJIB memanggil TEPAT SATU tool yang paling relevan dengan fokus tersebut.",
        "\nKEWAJIBAN OUTPUT (PENTING):",
        "- Selalu kembalikan respons dalam BENTUK tool_calls. Dilarang keras menjawab teks biasa tanpa tool.",
        "- Jika ingin bertanya/menyampaikan informasi ke user, WAJIB gunakan tool `ask_user(question: str)`.",
        "- Jika ragu atau tidak ada tool lain yang pasti, DEFAULT-kan ke `ask_user`.",
        "- Jika Anda tidak memanggil tool, sistem akan menganggapnya error.",
        "\nCHECKLIST PEMILIHAN TOOL (DEFAULT -> ask_user):",
        "- Perlu klarifikasi/bertanya/menyajikan daftar ke user -> ask_user.",
        "- Sudah punya tanggal -> get_showtimes; belum punya tanggal -> ask_user (minta tanggal).",
        "- Sudah punya showtime_id dan perlu ketersediaan -> get_available_seats; ingin menyarankan/bertanya kursi -> ask_user.",
        "- Semua slot sudah terisi -> signal_confirmation_ready.",
        "- Jangan pernah panggil tool signal_confirmation_ready kecuali semua data di DATA FORMULIR lengkap, jika belum lengkap, selalu gunakan tool lain selain ini",
        "\nCONTOH SALAH (JANGAN):",
        "Assistant: Baik, Anda memilih kursi B2 dan C4. Atas nama siapa pemesanan ini?",
        "CONTOH BENAR (WAJIB tool):",
        'ask_user(question="Baik, Anda memilih kursi B2 dan C4. Atas nama siapa pemesanan ini?")',
        "\n**ATURAN PENGECUALIAN (MUNDUR):**",
        "Aturan ini MENGALAHKAN `INSTRUKSI FOKUS`:",
        "Jika pesan user terbaru **jelas-jelas** ingin MENGGANTI slot yang SUDAH TERISI (misal: 'ganti film', 'ganti jadwal'),",
        "ABAIKAN FOKUS UTAMA dan WAJIB panggil tool `record_...` yang sesuai (misal: `record_selected_movie`) untuk menimpa data lama.",
        "\n**ATURAN PENGECUALIAN (INFO FILM / DUA LANGKAH):**",
        "Aturan ini MENGALAHKAN `INSTRUKSI FOKUS` dan memiliki DUA langkah:",
        "LANGKAH 1 (Saat user bertanya 'film ini tentang apa'/'sinopsis'/'trailer'):",
        "  1. ABAIKAN FOKUS UTAMA Anda (misal: jangan minta tanggal).",
        "  2. Cocokkan nama film (jika perlu) ke 'DAFTAR FILM TERSEDIA' untuk dapat ID-nya.",
        "  3. Panggil tool `get_movie_details(movie_id)`.",
        "  4. **PENTING: JANGAN** panggil `record_selected_movie` (karena user hanya bertanya).",
        "LANGKAH 2 (Di giliran berikutnya, SETELAH Anda menerima hasil 'get_movie_details' via ToolMessage):",
        "  1. ABAIKAN FOKUS UTAMA Anda LAGI.",
        "  2. WAJIB rangkum dan sampaikan hasil yang Anda terima (sinopsis dan link trailer) ke user.",
        "  3. Gunakan tool `ask_user` untuk menyampaikan rangkuman ini.",
        "  4. Jika sudah disampaikan ke user, barulah KEMBALI ke `INSTRUKSI FOKUS` semula di giliran berikutnya (setelah user merespons).",
        "\n**ATURAN PENGECUALIAN (JADWAL UMUM):**",
        "Aturan ini juga MENGALAHKAN `INSTRUKSI FOKUS`:",
        "Jika user bertanya pertanyaan umum tentang hari tayang (misal: 'film X tayang hari apa saja?', 'mainnya kapan aja?'),",
        "1. ABAIKAN FOKUS UTAMA (misal: jangan minta film/kursi).",
        "2. JANGAN panggil `get_showtimes` (karena tool itu butuh tanggal spesifik).",
        "3. WAJIB panggil `ask_user` dengan jawaban ini: 'Film di sini tayang setiap hari, namun pemesanan tiket hanya bisa dilakukan untuk hari ini, besok, dan lusa. Anda ingin memesan untuk tanggal berapa? Hari ini atau besok?'",        
        "\nDILARANG KERAS menjawab langsung. Jika bingung, panggil 'ask_user'.",
        "- PERINGATAN MUTLAK: Tool 'signal_confirmation_ready' HANYA boleh dipanggil jika SEMUA 4 slot FORMULIR SAAT INI (movie_id, showtime_id, seats, customer_name) 100% TERISI. Jika SATU SAJA slot masih 'BELUM ADA', Anda GAGAL dan WAJIB memanggil tool lain (misal 'ask_user') untuk mengisi slot yang kosong itu. INGAT: Setelah booking, formulir akan KOSONG lagi; perlakukan sebagai pesanan BARU dari NOL.",
        "\n**KONTEKS WAKTU SAAT INI:**",
        f"Hari ini (WIB) adalah tanggal: **{today_date_str}**",
        "Gunakan tanggal ini sebagai referensi WAJIB Anda.",
        "Jika user bilang 'hari ini', gunakan tanggal ini.",
        "Jika user bilang 'besok', 'lusa', atau 'minggu depan', Anda WAJIB menghitung tanggal 'YYYY-MM-DD' yang benar berdasarkan tanggal hari ini.",
        f"\n**DAFTAR FILM TERSEDIA:**\n{movie_list_str}",
        f"\n**FORMULIR SAAT INI:**\n"
        f"- current_movie_id: {movie_display}\n"
        f"- current_showtime_id: {showtime_display}\n"
        f"- selected_seats: {seats_display}\n"
        f"- customer_name: {customer or 'BELUM ADA'}",
        f"\n**KONTEKS TAMBAHAN:**\n"
        f"- Jadwal Tersedia:\n{showtime_context_str}\n"
        f"- Kursi Tersedia: {seat_context_str}\n"
        f"- Error Terakhir: {state.get('last_error') or 'Tidak ada'}",
        f"\n**PETA KURSI (SEAT_MAP):**\n{seat_map_context_str}",
        f"\n**INSTRUKSI FOKUS:**\n{focus_instruction}",
    ]

    system_prompt_content = "\n".join(prompt_lines)
    return [SystemMessage(content=system_prompt_content)]