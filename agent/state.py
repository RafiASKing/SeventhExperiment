# Di agent/state.py (file baru)
from typing import TypedDict, List, Optional, Literal, Annotated, Any
import operator

class TicketAgentState(TypedDict):
    """
    Representasi 'Formulir Pemesanan'.
    Tugas agent adalah mengisi slot-slot ini.
    """
    messages: Annotated[List[AnyMessage], operator.add]

    # Cukup 'browsing' (Q&A) atau 'booking' (Transaksi) atau 'confirmation' (menunggu Y/N)
    intent: Literal["browsing", "booking", "confirmation", "other"]

    # --- SLOT FORMULIR YANG WAJIB DIISI ---
    movie_title_query: Optional[str] # Apa yang user minta, misal "AOT"
    current_movie_id: Optional[int]  # ID film yang sudah pasti
    
    date_query: Optional[str]        # Apa yang user minta, misal "besok" atau "2025-10-29"
    current_showtime_id: Optional[int] # ID jadwal yang sudah pasti

    selected_seats: Optional[List[str]] # Daftar kursi
    user: Optional[str]                 # Nama pemesan (ingat, 'user' bukan 'user_name')

    # --- KONTEKS UNTUK SELEKTOR (Pilihan yang tersedia) ---
    candidate_movies: Optional[List[dict]]
    available_showtimes: Optional[List[dict]]
    available_seats: Optional[List[str]]
    
    # --- META-DATA ---
    # Data yang disiapkan untuk konfirmasi akhir
    confirmation_data: Optional[dict] 
    # Untuk self-correction jika ada error
    last_error: Optional[str]