from datetime import datetime
from typing import List, Optional, Set

from langchain_core.tools import tool
from pydantic import BaseModel, Field
from sqlalchemy import and_, insert, select

from agent.config import get_engine
from data.seats import ALL_VALID_SEATS
from data.timezone import (
    TARGET_TZ,
    UTC_TZ,
    from_db_utc_naive_to_local_display,
    get_current_local_date_str,
    to_utc_range_naive,
)
from db.schema import bookings_table, movies_table, showtimes_table


@tool
def get_showtimes(movie_id: int, date_local: str) -> List[dict]:
    """
    MENGAMBIL jadwal tayang untuk 1 film pada 1 tanggal LOKAL (WIB).
    Otomatis HANYA akan menampilkan jadwal yang akan datang (di atas jam sekarang).
    'date_local' HARUS dalam format 'YYYY-MM-DD'.
    """
    print(f"    > TOOL: get_showtimes(movie_id={movie_id}, date_local='{date_local}')")

    # 1. Cek apakah tanggal yang diminta adalah HARI INI (WIB)
    is_today = False
    try:
        # Panggil helper Anda untuk mendapatkan tanggal hari ini di WIB
        today_local_str = get_current_local_date_str() # -> "2025-11-03"
        if date_local == today_local_str:
            is_today = True
            print("    > INFO: Tanggal yang diminta adalah HARI INI. Menerapkan filter waktu...")
    except Exception as e:
        # Fallback jika helper error, anggap saja bukan hari ini
        print(f"    > WARNING: Gagal membandingkan tanggal hari ini: {e}")

    # 2. Dapatkan rentang UTC untuk tanggal yang diminta (Logika Lama, sudah benar)
    try:
        start_utc, end_utc = to_utc_range_naive(date_local)
    except ValueError as e:
        print(f"    > ERROR di get_showtimes: {e}")
        return [{"error": f"Format tanggal salah: {e}. Minta format YYYY-MM-DD."}]

    # 3. Bangun daftar kondisi query secara dinamis
    conditions = [
        showtimes_table.c.movie_id == movie_id,
        showtimes_table.c.time.between(start_utc, end_utc),
        showtimes_table.c.is_archived.is_(False),
    ]

    # 4. Tambahkan filter waktu jika 'is_today'
    if is_today:
        # Dapatkan waktu SEKARANG di WIB, konversi ke UTC, jadikan naive
        # Ini adalah format yang sama dengan yang disimpan di DB Anda
        now_utc_naive = datetime.now(TARGET_TZ).astimezone(UTC_TZ).replace(tzinfo=None)
        
        # Tambahkan kondisi 'WHERE time > [waktu_sekarang_di_utc]'
        conditions.append(showtimes_table.c.time > now_utc_naive)


    # 5. Buat statement query dengan SEMUA kondisi
    #    Kita menggunakan and_(*conditions) untuk "membuka" list kondisi
    stmt = (
        select(showtimes_table.c.id, showtimes_table.c.time)
        .where(and_(*conditions))  # <-- Perubahan di sini
        .order_by(showtimes_table.c.time)
    )

    # 6. Eksekusi DB
    try:
        engine = get_engine()
        with engine.connect() as conn:
            results = conn.execute(stmt).fetchall()
            
            if not results:
                # Beri pesan yang sedikit lebih baik jika ini hari ini
                if is_today:
                    return [
                        {"message": "Tidak ada jadwal tayang lagi untuk sisa hari ini."}
                    ]
                return [
                    {"message": "Tidak ada jadwal ditemukan untuk tanggal tersebut."}
                ]

            # Proses hasil
            showtimes_data = [
                {
                    "showtime_id": row.id,
                    "time_display": from_db_utc_naive_to_local_display(row.time),
                }
                for row in results
            ]
            print(f"    > TOOL get_showtimes: Menemukan {len(showtimes_data)} jadwal mendatang.")
            return showtimes_data
            
    except Exception as e:
        print(f"    > ERROR DB di get_showtimes: {e}")
        return [{"error": f"Gagal mengambil jadwal dari database: {e}"}]


class SeatAvailabilityInfo(BaseModel):
    count_available: int = Field(description="Jumlah kursi yang tersedia.")
    count_booked: int = Field(description="Jumlah kursi yang sudah terisi.")
    summary_for_llm: str = Field(
        description="Ringkasan tekstual kursi (tersedia & terisi) untuk prompt LLM."
    )
    available_list: List[str] = Field(description="Daftar lengkap kursi tersedia.")
    booked_list: List[str] = Field(
        description="Daftar lengkap kursi terisi."
    )


@tool
def get_available_seats(
    showtime_id: int,
) -> SeatAvailabilityInfo:
    """
    MENGAMBIL ringkasan (tersedia & terisi) dan daftar lengkap kursi tersedia
    untuk 1 jadwal.
    """
    print(f"    > TOOL: get_available_seats(showtime_id={showtime_id})")
    stmt = select(bookings_table.c.seat).where(
        bookings_table.c.showtime_id == showtime_id
    )

    try:
        engine = get_engine()
        booked_seats: Set[str]
        with engine.connect() as conn:
            booked_seats = {row.seat for row in conn.execute(stmt).fetchall()}

        available = sorted(
            [seat for seat in ALL_VALID_SEATS if seat not in booked_seats]
        )
        count_available = len(available)
        count_booked = len(booked_seats)
        booked_list_sorted = sorted(list(booked_seats))

        print(
            f"    > TOOL get_available_seats: dari 216 kursi, Menemukan {count_available} tersedia, {count_booked} sudah terisi."
        )

        summary_lines = []
        summary_lines.append(f"{count_available} kursi tersedia.")

        # Tampilkan info kursi yang sudah terisi (maks 10) saja
        if count_booked == 0:
            summary_lines.append("Belum ada kursi yang terisi.")
        else:
            booked_display_limit = 10
            booked_info = f"{count_booked} kursi terisi:"
            if count_booked <= booked_display_limit:
                booked_info += f" {', '.join(booked_list_sorted)}"
            else:
                booked_info += (
                    f" {', '.join(booked_list_sorted[:booked_display_limit])}..."
                )
            summary_lines.append(booked_info)

        # Tambahkan contoh kursi tersedia jika masih relevan
        if 0 < count_available <= 20:
            summary_lines.append(f"Kursi tersedia: {', '.join(available)}")
        elif count_available > 20:
            mid_index = count_available // 2
            examples = sorted(
                list(set([available[0], available[mid_index], available[-1]]))
            )
            summary_lines.append(
                f"Contoh kursi tersedia: {examples[0]} ... {examples[-1]}"
            )

        summary_str = " ".join(summary_lines)

        # Kembalikan dalam format dictionary/Pydantic
        return SeatAvailabilityInfo(
            count_available=count_available,
            count_booked=count_booked,
            summary_for_llm=summary_str,
            available_list=available,
            booked_list=booked_list_sorted,
        )

    except Exception as e:
        print(f"    > ERROR DB di get_available_seats: {e}")
        return SeatAvailabilityInfo(
            count_available=0,
            count_booked=0,
            summary_for_llm=f"Error: Gagal mengambil data kursi: {e}",
            available_list=[],
            booked_list=[],
        )


class AskUserSchema(BaseModel):
    question: str = Field(
        description="Pertanyaan yang jelas dan spesifik untuk diajukan ke user."
    ) # Perlu diubah ini nanti karena konflik instruksi


@tool(args_schema=AskUserSchema)
def ask_user(question: str) -> str:
    """
    Gunakan tool ini untuk MENGIRIM PESAN ke user.
    Bisa untuk BERTANYA (minta input) ATAU MEMBERI INFORMASI (misal daftar jadwal/kursi)
    sebelum bertanya.
    """
    print(f"    > TOOL: ask_user(question='{question}')")
    return question


@tool
def signal_confirmation_ready():
    """
    PANGGIL HANYA JIKA SEMUA DATA FORMULIR TERISI LENGKAP, CONTOHNYA:
    - current_movie_id: 21 (Judul: La La Land)
    - current_showtime_id: 774 (Waktu: 22:00 WIB)
    - selected_seats: A1, A2, A3
    - customer_name: Budi

    JANGAN DAN DILARANG panggil jika salah satu masih kosong/missing/invalid.
    JIKA MASIH ADA SLOT KOSONG, MAKA PANGGIL TOOL LAIN UNTUK MENGISI SLOT TERSEBUT.

    Catatan:
    - Setelah booking sukses, state biasanya direset kembali; jika kosong lagi, anggap pesanan baru dan isi ulang dari awal.
    - Jangan mengandalkan ingatan percakapan lama untuk konfirmasi; isi kembali slot yang kosong jika memang masih kurang.
    - Hanya panggil tool ini bila yakin keempat slot ini sudah terisi.

    Contoh salah: signal_confirmation_ready() ketika current_showtime_id=BELUM ADA.
    Contoh benar: signal_confirmation_ready() setelah movie/showtime/seats/nama lengkap.
    """
    print("    > TOOL: signal_confirmation_ready() dipanggil.")
    return "Sinyal konfirmasi diterima."


# --- TOOL MANUAL ---
def book_tickets_tool(showtime_id: int, seats: List[str], customer_name: str) -> str:
    """Fungsi Python murni untuk eksekusi booking."""
    print(
        f"    > EKSEKUSI: Mencoba booking {seats} untuk {customer_name} di showtime {showtime_id}"
    )
    insert_data = [
        {"showtime_id": showtime_id, "seat": s, "user": customer_name} for s in seats
    ]
    try:
        engine = get_engine()
        with engine.connect() as conn:
            with conn.begin():
                # Validasi kursi sebelum insert (Defensive)
                invalid_seats = [s for s in seats if s not in ALL_VALID_SEATS]
                if invalid_seats:
                    raise ValueError(
                        f"Kursi tidak valid ditemukan: {', '.join(invalid_seats)}"
                    )

                # Cek ketersediaan lagi (Defensive, race condition)
                stmt_check = select(bookings_table.c.seat).where(
                    and_(
                        bookings_table.c.showtime_id == showtime_id,
                        bookings_table.c.seat.in_(seats),
                    )
                )
                already_booked = conn.execute(stmt_check).fetchall()
                if already_booked:
                    booked_list = [r.seat for r in already_booked]
                    raise ValueError(
                        f"Kursi {', '.join(booked_list)} sudah terisi saat mencoba booking."
                    )

                # Insert jika aman
                conn.execute(insert(bookings_table), insert_data)

        return f"Sukses! Tiket untuk {customer_name} di kursi {', '.join(seats)} telah dikonfirmasi."
    except ValueError as ve:
        print(f"    > EKSEKUSI GAGAL (Validasi): {ve}")
        return f"Maaf, terjadi masalah: {ve}"
    except Exception as e:
        print(f"    > EKSEKUSI GAGAL (DB): {e}")
        if "uq_booking_showtime_seat" in str(e):
            return f"Maaf, terjadi error saat booking. Salah satu kursi ({', '.join(seats)}) mungkin sudah terisi oleh orang lain."
        return "Maaf, terjadi error tak terduga saat booking."


class MovieDetails(BaseModel):
    title: str
    synopsis: str
    trailer_url: Optional[str] = Field(
        default=None, description="URL YouTube lengkap jika tersedia."
    )
    error: Optional[str] = Field(default=None)

@tool
def get_movie_details(movie_id: int) -> MovieDetails:
    """
    MENGAMBIL detail (sinopsis, trailer) untuk 1 film.
    Gunakan ini JIKA user bertanya 'filmnya tentang apa'. atau 'trailer filmnya dong!'.
    Tool ini HANYA mengambil info, TIDAK mencatat pilihan film.
    """
    print(f"     > TOOL: get_movie_details(movie_id={movie_id})")
    try:
        engine = get_engine()
        with engine.connect() as conn:
            stmt = select(
                movies_table.c.title,
                movies_table.c.description,
                movies_table.c.trailer_youtube_id,
            ).where(movies_table.c.id == movie_id)
            result = conn.execute(stmt).first()

            if result:
                trailer_id = result.trailer_youtube_id
                full_trailer_url = None
                
                if trailer_id:
                    full_trailer_url = f"https://www.youtube.com/watch?v={trailer_id}"

                return MovieDetails(
                    title=result.title,
                    synopsis=result.description or "Sinopsis tidak tersedia.",
                    trailer_url=full_trailer_url,
                )
            else:
                return MovieDetails(
                    title="Film tidak ditemukan",
                    synopsis="Sinopsis tidak tersedia.",
                    error="Film tidak ditemukan.",
                )
    except Exception as e:
        print(f"     > ERROR di get_movie_details: {e}")
        return MovieDetails(
            title="Error",
            synopsis="Tidak dapat mengambil detail film.",
            error=f"Error database: {e}",
        )
    
    
class SelectMovieAction(BaseModel):
    """
    Aksi untuk MENGISI slot 'current_movie_id'.
    Pilih ini HANYA jika kamu sudah 100% yakin ID filmnya.
    """

    selected_movie_id: int = Field(
        description="ID film yang sudah pasti (dari 'all_movies_list')."
    )


class SelectShowtimeAction(BaseModel):
    """
    Aksi untuk MENGISI slot 'current_showtime_id'.
    Pilih ini HANYA jika kamu sudah 100% yakin ID jadwalnya.
    """

    selected_showtime_id: int = Field(
        description="ID jadwal yang sudah pasti (dari 'context_showtimes')."
    )


class SelectSeatsAction(BaseModel):
    """
    Aksi untuk MENGISI slot 'selected_seats'.
    Pilih ini HANYA jika kamu sudah 100% yakin kursinya.
    """

    selected_seats_list: List[str] = Field(description="Daftar kursi yang sudah pasti. Format WAJIB: huruf kapital dan angka (contoh: 'A1', 'B5').")


class ExtractNameAction(BaseModel):
    """
    Aksi untuk MENGISI slot 'customer_name'.
    Pilih ini HANYA jika kamu sudah 100% yakin namanya.
    """

    extracted_customer_name: str = Field(description="Nama pemesan yang sudah pasti.")


@tool(args_schema=SelectMovieAction)
def record_selected_movie(selected_movie_id: Optional[int]) -> str:
    """
    Gunakan ini untuk MENCATAT ID film yang sudah dipilih user.
    Panggil ini SETELAH kamu mencocokkan input user ('Kimi no Nawa')
    ke ID film dari 'DAFTAR FILM TERSEDIA'.
    Jika user tidak memilih/tidak relevan, panggil dengan 'selected_movie_id: null'.
    """
    if selected_movie_id is None:
        return "OK. Tidak ada film yang dipilih."
    return f"OK. Film ID {selected_movie_id} dicatat."


@tool(args_schema=SelectShowtimeAction)
def record_selected_showtime(selected_showtime_id: Optional[int]) -> str:
    """
    Gunakan ini untuk MENCATAT ID jadwal yang sudah dipilih user.
    Panggil ini SETELAH kamu mencocokkan input user ('jam 7 malam')
    ke ID jadwal dari 'Jadwal Tersedia'.
    Jika user tidak memilih/tidak relevan, panggil dengan 'selected_showtime_id: null'.
    """
    if selected_showtime_id is None:
        return "OK. Tidak ada jadwal yang dipilih."
    return f"OK. Jadwal ID {selected_showtime_id} dicatat."


@tool(args_schema=SelectSeatsAction)
def record_selected_seats(selected_seats_list: Optional[List[str]]) -> str:
    """
    Gunakan ini untuk MENCATAT daftar kursi yang sudah dipilih user.
    Panggil ini SETELAH kamu mengekstrak kursi dari input user.
    CONTOH: ['A1', 'A2'].
    Format kursi WAJIB HURUF KAPITAL diikuti angka (misal: ['A1', 'B5']), sesuai PETA KURSI.
    """
    if not selected_seats_list:
        return "OK. Tidak ada kursi yang dipilih."
    return f"OK. Kursi {', '.join(selected_seats_list)} dicatat."


@tool(args_schema=ExtractNameAction)
def record_customer_name(extracted_customer_name: Optional[str]) -> str:
    """
    Gunakan ini untuk MENCATAT nama pemesan yang sudah diekstrak.
    Panggil ini SETELAH kamu mengekstrak nama (misal 'Rafi') dari input user.
    Jika user tidak menyebut nama, panggil dengan 'extracted_customer_name: null'.
    """
    if not extracted_customer_name:
        return "OK. Tidak ada nama yang diekstrak."
    return f"OK. Nama {extracted_customer_name} dicatat."