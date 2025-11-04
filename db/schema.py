# Define table db ke bahasa Python pakai SQLAlchemy
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
    func,
)

from agent.config import get_metadata


metadata = get_metadata()


genres_table = Table(
    "genres",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(120), nullable=False, unique=True),
    Column("created_at", DateTime, default=func.now()),
)
movies_table = Table(
    "movies",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("title", String(255), nullable=False),
    Column("description", Text),
    Column("studio_number", Integer, nullable=False, unique=True),
    Column("poster_path", String(255)),
    Column("backdrop_path", String(255)),
    Column("release_date", Date),
    Column("trailer_youtube_id", String(20)),
    Column("created_at", DateTime, default=func.now()),
)
movie_genres_table = Table(
    "movie_genres",
    metadata,
    Column("movie_id", Integer, ForeignKey("movies.id"), primary_key=True),
    Column("genre_id", Integer, ForeignKey("genres.id"), primary_key=True),
)
showtimes_table = Table(
    "showtimes",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("movie_id", Integer, ForeignKey("movies.id"), nullable=False),
    Column("time", DateTime, nullable=False),
    Column("is_archived", Boolean, nullable=False, default=False),
    Column("created_at", DateTime, default=func.now()),
)
bookings_table = Table(
    "bookings",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user", String(255), nullable=False),
    Column("seat", String(10), nullable=False),
    Column("showtime_id", Integer, ForeignKey("showtimes.id"), nullable=False),
    Column("created_at", DateTime, default=func.now()),
    UniqueConstraint("showtime_id", "seat", name="uq_booking_showtime_seat"),
)