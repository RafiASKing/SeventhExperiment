import os

from dotenv import load_dotenv
from sqlalchemy import MetaData, create_engine


_engine = None
_metadata = MetaData()
_environment_checked = False


def setup_environment() -> None:
    """Memuat semua environment variables, menyimpannya ke os.environ, dan menampilkan nilai TERMASKED."""

    global _environment_checked
    if _environment_checked:
        return

    load_dotenv()

    def mask_value(val: str, visible_fraction: float = 0.5) -> str:
        if val is None:
            return ""
        s = str(val)
        n = len(s)
        if n <= 4:
            return "*" * n
        visible = max(1, int(n * visible_fraction))
        return s[:visible] + "*" * (n - visible)

    required_vars = [
        "GOOGLE_API_KEY",
        "DATABASE_URL",
    ]
    optional_vars = [
        "LANGSMITH_API_KEY",
        "LANGSMITH_TRACING",
        "LANGSMITH_ENDPOINT",
        "LANGSMITH_PROJECT",
    ]

    for var in required_vars:
        value = os.getenv(var)
        if not value:
            raise RuntimeError(
                f"{var} not found in environment. Set it in .env atau export terlebih dahulu."
            )
        os.environ[var] = value
        print(f"{var} Terload! Value: {mask_value(value)}")

    for var in optional_vars:
        value = os.getenv(var)
        if value:
            os.environ[var] = value
            print(f"{var} Terload! Value: {mask_value(value)}")
        else:
            print(f"{var} tidak ditemukan. Lewati (opsional).")

    _environment_checked = True


def get_engine():
    global _engine
    if _engine is None:
        setup_environment()
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise RuntimeError("DATABASE_URL tidak ditemukan setelah setup_environment().")
        _engine = create_engine(database_url)
    return _engine


def get_metadata():
    return _metadata