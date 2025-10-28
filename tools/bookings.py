# Di tools/bookings.py (Revisi Total)

# (Impor helper timezone.py yang kita bahas sebelumnya)
# from app.timezone import to_utc_range_naive, ...

@tool
def search_movies(title_query: str) -> List[dict]:
    """
    MENCARI film berdasarkan kueri judul. 
    Wajib dipanggil jika 'current_movie_id' belum ada.
    """
    # ... Logika query (dengan alias "AOT" -> "Attack on Titan", "Kimi no Nawa" -> "Your Name")
    # ... Mengembalikan list, bisa kosong, bisa 1, bisa banyak.
    # Cth: [{'id': 5, 'title': 'Attack on Titan: Requiem', 'studio': 5}]
    pass

@tool
def get_showtimes(movie_id: int, date_local: str) -> List[dict]:
    """
    MENGAMBIL jadwal tayang untuk 1 film pada 1 tanggal LOKAL (WIB).
    'date_local' HARUS dalam format 'YYYY-MM-DD'.
    """
    # 1. Panggil helper `to_utc_range_naive(date_local)`
    #    (misal '2025-10-29' -> start: '2025-10-28 17:00', end: '2025-10-29 16:59' UTC)
    # 2. Query DB untuk showtimes di rentang UTC itu.
    # 3. Konversi balik tiap hasil ke string WIB untuk 'time_display'.
    # Cth: [{'id': 13, 'time_display': '19:00 WIB'}, {'id': 14, 'time_display': '21:30 WIB'}]
    pass

@tool
def get_available_seats(showtime_id: int) -> List[str]:
    """MENGAMBIL daftar kursi yang tersedia untuk 1 jadwal."""
    # ... Logika query DB
    # Cth: ['A1', 'A2', 'A3', ...]
    pass

# --- Tools "META" (Mengontrol Alur) ---

@tool
def ask_user(question: str) -> str:
    """
    Gunakan tool ini JIKA kamu butuh informasi dari user.
    Contoh: 'Mau nonton tanggal berapa (YYYY-MM-DD)?'
    """
    # Ini adalah "passthrough". Agent akan berhenti dan AIMessage
    # akan berisi 'question' ini.
    return question

@tool
def request_confirmation(
    movie_id: int, 
    showtime_id: int, 
    seats: List[str], 
    user: str
) -> dict:
    """
    Gunakan tool ini HANYA JIKA SEMUA 4 slot (movie_id, showtime_id, seats, user) 
    SUDAH TERISI LENGKAP. Ini adalah langkah terakhir sebelum booking.
    """
    # Tool ini hanya mengemas data. Ini adalah sinyal untuk 'node_show_confirmation'.
    return {
        "movie_id": movie_id,
        "showtime_id": showtime_id,
        "seats": seats,
        "user": user
    }

# Tool 'book_tickets' akan kita panggil secara manual di node 'handle_confirmation'
# jadi tidak perlu diekspos ke LLM.