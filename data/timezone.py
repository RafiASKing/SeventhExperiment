from datetime import datetime
from zoneinfo import ZoneInfo


TARGET_TZ = ZoneInfo("Asia/Jakarta")
UTC_TZ = ZoneInfo("UTC")


def to_utc_range_naive(date_local_str: str) -> tuple[datetime, datetime]:
    """Mengambil string 'YYYY-MM-DD' WIB, mengembalikan rentang Naive UTC."""
    try:
        local_date = datetime.strptime(date_local_str, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Format tanggal salah. Gunakan YYYY-MM-DD.")

    start_local_aware = datetime(
        local_date.year, local_date.month, local_date.day, 0, 0, 0, tzinfo=TARGET_TZ
    )
    end_local_aware = datetime(
        local_date.year, local_date.month, local_date.day, 23, 59, 59, tzinfo=TARGET_TZ
    )
    
    start_utc_aware = start_local_aware.astimezone(UTC_TZ)
    end_utc_aware = end_local_aware.astimezone(UTC_TZ)
    
    return start_utc_aware.replace(tzinfo=None), end_utc_aware.replace(tzinfo=None)


def from_db_utc_naive_to_local_display(utc_dt_naive: datetime) -> str:
    """Mengambil Naive UTC dari DB, mengembalikan string 'HH:MM WIB'."""
    
    utc_aware = utc_dt_naive.replace(tzinfo=UTC_TZ)
    local_aware = utc_aware.astimezone(TARGET_TZ)
    
    return local_aware.strftime("%H:%M WIB")


def get_current_local_date_str() -> str:
    """Mengembalikan string 'YYYY-MM-DD' untuk hari ini di timezone LOKAL (WIB)."""
    
    return datetime.now(TARGET_TZ).strftime("%Y-%m-%d")