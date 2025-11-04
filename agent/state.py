import operator
from typing import Annotated, List, Optional, TypedDict

from langchain_core.messages import AIMessage, AnyMessage, ToolMessage


class TicketAgentState(TypedDict):
    messages: Annotated[List[AnyMessage], operator.add]

    all_movies_list: List[dict]

    # --- SLOT FORMULIR ---
    current_movie_id: Optional[int]
    current_showtime_id: Optional[int]
    selected_seats: Optional[List[str]]
    customer_name: Optional[str]

    # --- KONTEKS SESAAT UNTUK SELEKTOR ---
    context_showtimes: Optional[List[dict]]
    context_seats: Optional[List[str]]

    # --- META-DATA ---
    confirmation_data: Optional[dict]
    last_error: Optional[str]
    
    
    
def get_stable_history_slice(
    messages: List[AnyMessage], max_messages: int = 72
) -> List[AnyMessage]:
    """Ambil potongan histori stabil tanpa memutus pasangan AI/tool."""
    if not messages or max_messages <= 0:
        return []

    buffer = max_messages + 8
    tail = messages[-buffer:]

    chunks: List[List[AnyMessage]] = []
    i = 0
    while i < len(tail):
        msg = tail[i]

        if isinstance(msg, ToolMessage):
            i += 1
            continue

        if isinstance(msg, AIMessage) and getattr(msg, "tool_calls", None):
            chunk: List[AnyMessage] = [msg]
            i += 1
            while i < len(tail) and isinstance(tail[i], ToolMessage):
                chunk.append(tail[i])
                i += 1
            chunks.append(chunk)
            continue

        chunks.append([msg])
        i += 1

    if not chunks:
        return []

    selected_chunks: List[List[AnyMessage]] = []
    total = 0
    for chunk in reversed(chunks):
        chunk_len = len(chunk)
        if total + chunk_len > max_messages:
            if not selected_chunks:
                if isinstance(chunk[0], AIMessage) and getattr(chunk[0], "tool_calls", None):
                    keep_tool = max_messages - 1
                    trimmed = [chunk[0]]
                    if keep_tool > 0:
                        trimmed.extend(chunk[-keep_tool:])
                    selected_chunks.append(trimmed)
                    total = len(trimmed)
                else:
                    trimmed = chunk[-max_messages:]
                    selected_chunks.append(trimmed)
                    total = len(trimmed)
            break

        selected_chunks.append(chunk)
        total += chunk_len
        if total >= max_messages:
            break

    selected_chunks.reverse()

    sliced: List[AnyMessage] = []
    for chunk in selected_chunks:
        sliced.extend(chunk)

    while sliced and isinstance(sliced[0], ToolMessage):
        sliced.pop(0)

    if (
        sliced
        and isinstance(sliced[0], AIMessage)
        and getattr(sliced[0], "tool_calls", None)
        and not (len(sliced) > 1 and isinstance(sliced[1], ToolMessage))
    ):
        sliced.pop(0)

    while (
        sliced
        and isinstance(sliced[-1], AIMessage)
        and getattr(sliced[-1], "tool_calls", None)
    ):
        sliced.pop()

    return sliced