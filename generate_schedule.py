#!/usr/bin/env python3
"""
Utility script (STANDALONE) to maintain a rolling three-day schedule.
Didesain untuk berjalan tanpa Flask app context, hanya menggunakan SQLAlchemy Core.
"""

from __future__ import annotations
from datetime import datetime, timedelta, time, timezone
import pytz
import os

from dotenv import load_dotenv
from sqlalchemy import select, update, insert, and_, between, func, Connection, text

# 1. Setup Lingkungan (WAJIB ADA)
# Pastikan kamu punya .env dan db/schema.py
try:
    from db.schema import engine, movies_table, showtimes_table
except ImportError:
    print("Error: File 'db/schema.py' tidak ditemukan.")
    print("Pastikan script ini berada di folder yang sama dengan 'run_tiketa.py'.")
    exit(1)

load_dotenv()

# --- Konfigurasi Zona Waktu dan Jadwal (Sama seperti file-mu) ---
JAKARTA_TZ = pytz.timezone('Asia/Jakarta')
UTC = pytz.UTC
START_HOUR = 6  # Jam 6 pagi WIB

EVEN_INTERVAL_HOURS = 3
ODD_INTERVAL_HOURS = 4
EVEN_SLOTS = 6
ODD_SLOTS = 5
# --- Akhir Konfigurasi ---

def _now_utc_naive() -> datetime:
    # Ganti .utcnow() dengan standar baru
    return datetime.now(timezone.utc).replace(tzinfo=None)


def purge_past_showtimes(conn: Connection) -> int:
    """
    Arsipkan jadwal terlewat menggunakan SQLAlchemy Core.
    conn: Objek koneksi SQLAlchemy yang aktif.
    """
    now_utc = _now_utc_naive()

    # Diterjemahkan dari ORM:
    # Showtime.query.filter(...).update(...)
    stmt = (
        update(showtimes_table)
        .where(
            and_(
                showtimes_table.c.time < now_utc,
                showtimes_table.c.is_archived.is_(False) # Gunakan .is_(False) untuk cek 'IS FALSE' di SQL
            )
        )
        .values(is_archived=True)
    )
    
    result = conn.execute(stmt)
    return result.rowcount # rowcount adalah jumlah baris yang di-update


def _generate_slots(studio_number: int) -> tuple[int, int]:
    is_even = studio_number % 2 == 0
    slots = EVEN_SLOTS if is_even else ODD_SLOTS
    interval = EVEN_INTERVAL_HOURS if is_even else ODD_INTERVAL_HOURS
    return slots, interval


def _to_local_naive(utc_dt: datetime) -> datetime:
    """Konversi Naive UTC (dari DB) ke Naive Jakarta (untuk logika)."""
    if utc_dt.tzinfo is not None:
        utc_dt = utc_dt.astimezone(UTC).replace(tzinfo=None)
        
    utc_aware = UTC.localize(utc_dt)
    return utc_aware.astimezone(JAKARTA_TZ).replace(tzinfo=None)


def _to_utc_naive(local_dt: datetime) -> datetime:
    """Konversi Naive Jakarta (dari logika) ke Naive UTC (untuk DB)."""
    if local_dt.tzinfo is not None:
        local_dt = local_dt.astimezone(JAKARTA_TZ).replace(tzinfo=None)

    local_aware = JAKARTA_TZ.localize(local_dt)
    return local_aware.astimezone(UTC).replace(tzinfo=None)


def generate_upcoming_showtimes(conn: Connection, days: int = 3) -> int:
    """
    Pastikan jadwal 3 hari ke depan ada, menggunakan SQLAlchemy Core.
    conn: Objek koneksi SQLAlchemy yang aktif.
    """
    # Ganti datetime.now(JAKARTA_TZ).replace(tzinfo=None)
    # dengan konversi yang lebih aman dari UTC
    now_utc_aware = datetime.now(UTC)
    now_local = now_utc_aware.astimezone(JAKARTA_TZ).replace(tzinfo=None)
    
    new_records = 0

    # Diterjemahkan dari ORM:
    # Movie.query.order_by(Movie.studio_number)
    movie_select_stmt = select(
                            movies_table.c.id, 
                            movies_table.c.studio_number
                        ).order_by(movies_table.c.studio_number)
    
    movies = conn.execute(movie_select_stmt).fetchall()

    for movie in movies:
        movie_id = movie.id
        studio_number = movie.studio_number
        
        slots, interval_hours = _generate_slots(studio_number)

        for i in range(days):
            target_date = (now_local + timedelta(days=i)).date()
            
            # Buat rentang hari dalam Naive UTC untuk query
            day_start_local = datetime.combine(target_date, time.min)
            day_end_local = datetime.combine(target_date, time.max)
            day_start_utc = _to_utc_naive(day_start_local)
            day_end_utc = _to_utc_naive(day_end_local)

            # Diterjemahkan dari ORM:
            # Showtime.query.filter(...)
            existing_stmt = (
                select(showtimes_table)
                .filter(
                    showtimes_table.c.movie_id == movie_id,
                    showtimes_table.c.time.between(day_start_utc, day_end_utc),
                    showtimes_table.c.is_archived.is_(False)
                )
                .order_by(showtimes_table.c.time)
            )
            existing_showtimes = conn.execute(existing_stmt).fetchall()

            normalized_existing = {_to_local_naive(st.time) for st in existing_showtimes}

            start_time_local = datetime.combine(target_date, time(hour=START_HOUR))
            expected_times_local = [
                start_time_local + timedelta(hours=interval_hours * slot_index)
                for slot_index in range(slots)
            ]
            expected_normalized = {et.replace(minute=0, second=0, microsecond=0) for et in expected_times_local}


            # Arsipkan jadwal yang tidak sesuai
            ids_to_archive = []
            for st in existing_showtimes:
                normalized = _to_local_naive(st.time).replace(minute=0, second=0, microsecond=0)
                if normalized not in expected_normalized:
                    ids_to_archive.append(st.id)
            
            if ids_to_archive:
                archive_stmt = (
                    update(showtimes_table)
                    .where(showtimes_table.c.id.in_(ids_to_archive))
                    .values(is_archived=True)
                )
                conn.execute(archive_stmt)

            # Tambahkan jadwal baru yang kurang
            new_showtimes_to_add = []
            for show_time_local in expected_times_local:
                normalized_show_time = show_time_local.replace(minute=0, second=0, microsecond=0)
                if normalized_show_time in normalized_existing:
                    continue

                show_time_utc = _to_utc_naive(show_time_local)
                new_showtimes_to_add.append({"movie_id": movie_id, "time": show_time_utc})
                normalized_existing.add(normalized_show_time) # Tambahkan agar tidak duplikat
            
            if new_showtimes_to_add:
                conn.execute(insert(showtimes_table), new_showtimes_to_add)
                new_records += len(new_showtimes_to_add)

    return new_records


def main() -> None:
    """
    Fungsi main baru yang tidak butuh 'app context'.
    Kita pakai 'engine' langsung untuk koneksi dan transaksi.
    """
    print("Menjalankan skrip jadwal standalone...")
    
    # Kita bungkus semua dalam satu transaksi
    # Jika 'generate' gagal, 'purge' juga akan di-rollback
    with engine.connect() as conn:
        with conn.begin(): # Memulai transaksi
            try:
                print("Membersihkan jadwal lama...")
                purged = purge_past_showtimes(conn) 
                print(f"Selesai. {purged} jadwal lama diarsipkan.")
                
                print("Membuat jadwal baru untuk 3 hari ke depan...")
                created = generate_upcoming_showtimes(conn)
                print(f"Selesai. {created} jadwal baru dibuat.")
                
                print("Sukses! Transaksi di-commit.")
                # Commit otomatis terjadi di sini jika tidak ada error
                
            except Exception as e:
                print(f"--- ERROR TERJADI! ---")
                print(f"Semua perubahan di-rollback. Error: {e}")
                # Rollback otomatis terjadi di sini
                raise # Tampilkan error-nya

if __name__ == "__main__":
    # Cek koneksi DB dulu
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Koneksi database (dari .env) sukses.")
    except Exception as e:
        print(f"FATAL: Gagal koneksi ke database. Cek DATABASE_URL di .env")
        print(f"Error: {e}")
        exit(1)
        
    main()