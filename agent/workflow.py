from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, StateGraph
from sqlalchemy import select

from agent.config import get_engine
from agent.state import TicketAgentState
from db.schema import movies_table
from tools.bookings import (
    ask_user,
    get_available_seats,
    get_movie_details,
    get_showtimes,
    record_customer_name,
    record_selected_movie,
    record_selected_seats,
    record_selected_showtime,
    signal_confirmation_ready,
)


booking_manager_tools = [
    get_showtimes,
    get_available_seats,
    ask_user,
    get_movie_details,
    signal_confirmation_ready,
    record_selected_movie,
    record_selected_showtime,
    record_selected_seats,
    record_customer_name,
]

_llm_instance = None
model_with_tools = None

from agent import nodes as agent_nodes
from agent.nodes import assign_model, booking_router, node_booking_manager, node_confirmation

def ensure_model_bound():
    """Lazy init LLM and bind tools once, then assign to nodes."""
    global _llm_instance, model_with_tools
    if model_with_tools is None:
        if _llm_instance is None:
            _llm_instance = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
        model_with_tools = _llm_instance.bind_tools(booking_manager_tools)
        assign_model(model_with_tools)
    return model_with_tools

print("Merakit Graph...")

workflow = StateGraph(TicketAgentState)

workflow.add_node("booking_manager", node_booking_manager)
workflow.add_node("confirmation", node_confirmation)

workflow.set_entry_point("booking_manager")

workflow.add_conditional_edges(
    "booking_manager",  # asal
    booking_router,
    {
        "confirm": "confirmation",
        "continue": "booking_manager",  # Looping
        "__end__": END,  # Jika router bilang '__end__', graph berhenti
    },
)

# Untuk node konfirmasi selalu END
workflow.add_edge("confirmation", END)

app = workflow.compile()
print("Graph berhasil di-compile.")


_FALLBACK_MOVIES = [
    {"id": 1, "title": "Spirited Away"},
    {"id": 2, "title": "Your Name"},
    {"id": 3, "title": "Attack on Titan: Requiem"},
]
_movies_context: list[dict] = list(_FALLBACK_MOVIES)


def _load_movies_from_db() -> list[dict]:
    print("Memuat daftar film dari DB...")
    try:
        engine = get_engine()
        with engine.connect() as conn:
            if "title" not in movies_table.c:
                raise KeyError("Kolom 'title' tidak ditemukan di movies_table.")
            rows = conn.execute(
                select(movies_table.c.id, movies_table.c.title)
            ).fetchall()
            if not rows:
                print("PERINGATAN: Tidak ada film ditemukan di database.")
            return [{"id": row.id, "title": row.title} for row in rows]
    except Exception as e:
        print(f"ERROR saat memuat daftar film: {e}")
        print("Menggunakan daftar film contoh sebagai fallback.")
        return list(_FALLBACK_MOVIES)


def get_movies_context(*, force_refresh: bool = False) -> list[dict]:
    global _movies_context
    if force_refresh or not _movies_context:
        _movies_context = _load_movies_from_db()
    return list(_movies_context)


def get_initial_state(*, force_refresh_movies: bool = False) -> TicketAgentState:
    movies_context = get_movies_context(force_refresh=force_refresh_movies)
    return TicketAgentState(
        messages=[],
        all_movies_list=movies_context,
        current_movie_id=None,
        current_showtime_id=None,
        selected_seats=None,
        customer_name=None,
        context_showtimes=None,
        context_seats=None,
        context_seats_summary="N/A",
        confirmation_data=None,
        last_error=None,
    )


# PENYIMPANAN STATE (PERLU DIIMPLEMENTASIKAN LEBIH NANTI)
session_states = {}
SESSION_ID = "user_session_123"

print("\n--- Agen Manajer Booking Siap! ---")
print("Ketik 'exit' untuk keluar.")
print("Contoh: 'mau pesan tiket', 'kimi no nawa', '2025-10-30', 'A1', 'Rafi'")