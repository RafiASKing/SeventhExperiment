# Konteks Lengkap Proyek Agen Bioskop

## Bagian 1: Struktur File Proyek

```

### Path: data/seats.py

```python
SEAT_MAP: list[list[str | None]] = [
    # A
    [
        "A1",
        "A2",
        "A3",
        "A4",
        "A5",
        "A6",
        "A7",
        "A8",
        "A9",
        None,
        "A10",
        "A11",
        "A12",
        "A13",
        "A14",
        "A15",
        "A16",
        "A17",
        "A18",
    ],
    # B
    [
        "B1",
        "B2",
        "B3",
        "B4",
        "B5",
        "B6",
        "B7",
        "B8",
        "B9",
        None,
        "B10",
        "B11",
        "B12",
        "B13",
        "B14",
        "B15",
        "B16",
        "B17",
        "B18",
    ],
    # C
    [
        "C1",
        "C2",
        "C3",
        "C4",
        "C5",
        "C6",
        "C7",
        "C8",
        "C9",
        None,
        "C10",
        "C11",
        "C12",
        "C13",
        "C14",
        "C15",
        "C16",
        "C17",
        "C18",
    ],
    # D
    [
        "D1",
        "D2",
        "D3",
        "D4",
        "D5",
        "D6",
        "D7",
        "D8",
        "D9",
        None,
        "D10",
        "D11",
        "D12",
        "D13",
        "D14",
        "D15",
        "D16",
        "D17",
        "D18",
    ],
    # E
    [
        "E1",
        "E2",
        "E3",
        "E4",
        "E5",
        "E6",
        "E7",
        "E8",
        "E9",
        None,
        "E10",
        "E11",
        "E12",
        "E13",
        "E14",
        "E15",
        "E16",
        "E17",
        "E18",
    ],
    # F
    [
        "F1",
        "F2",
        "F3",
        "F4",
        "F5",
        "F6",
        "F7",
        "F8",
        "F9",
        None,
        "F10",
        "F11",
        "F12",
        "F13",
        "F14",
        "F15",
        "F16",
        "F17",
        "F18",
    ],
    # G
    [
        "G1",
        "G2",
        "G3",
        "G4",
        "G5",
        "G6",
        "G7",
        "G8",
        "G9",
        None,
        "G10",
        "G11",
        "G12",
        "G13",
        "G14",
        "G15",
        "G16",
        "G17",
        "G18",
    ],
    # H
    [
        "H1",
        "H2",
        "H3",
        "H4",
        "H5",
        "H6",
        "H7",
        "H8",
        "H9",
        None,
        "H10",
        "H11",
        "H12",
        "H13",
        "H14",
        "H15",
        "H16",
        "H17",
        "H18",
    ],
    # I
    [
        "I1",
        "I2",
        "I3",
        "I4",
        "I5",
        "I6",
        "I7",
        "I8",
        "I9",
        None,
        "I10",
        "I11",
        "I12",
        "I13",
        "I14",
        "I15",
        "I16",
        "I17",
        "I18",
    ],
    # J
    [
        "J1",
        "J2",
        "J3",
        "J4",
        "J5",
        "J6",
        "J7",
        "J8",
        "J9",
        None,
        "J10",
        "J11",
        "J12",
        "J13",
        "J14",
        "J15",
        "J16",
        "J17",
        "J18",
    ],
    # K (kosong lorong)
    [None] * 19,
    # L (lebih sempit)
    [
        "L1",
        "L2",
        "L3",
        "L4",
        "L5",
        "L6",
        "L7",
        "L8",
        "L9",
        None,
        "L10",
        "L11",
        "L12",
        "L13",
        "L14",
        "L15",
        "L16",
        "L17",
        "L18",
    ],
    # M (lebih sempit lagi)
    [
        "M1",
        "M2",
        "M3",
        "M4",
        "M5",
        "M6",
        "M7",
        "M8",
        "M9",
        None,
        "M10",
        "M11",
        "M12",
        "M13",
        "M14",
        "M15",
        "M16",
        "M17",
        "M18",
    ],
]
ALL_VALID_SEATS = {seat for row in SEAT_MAP for seat in row if seat}
```

### Path: data/timezone.py

```python
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
```

### Path: db/__init__.py

```python
"""Data package exposing schema and seed data."""

```

### Path: db/schema.py

```python
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
    Column("movie_id", Integer, ForeignKey("movies.id"), primary key=True),
    Column("genre_id", Integer, ForeignKey("genres.id"), primary key=True),
)
showtimes_table = Table(
    "showtimes",
    metadata,
    Column("id", Integer, primary key=True, autoincrement=True),
    Column("movie_id", Integer, ForeignKey("movies.id"), nullable=False),
    Column("time", DateTime, nullable=False),
    Column("is_archived", Boolean, nullable=False, default=False),
    Column("created_at", DateTime, default=func.now()),
)
bookings_table = Table(
    "bookings",
    metadata,
    Column("id", Integer, primary key=True, autoincrement=True),
    Column("user", String(255), nullable=False),
    Column("seat", String(10), nullable=False),
    Column("showtime_id", Integer, ForeignKey("showtimes.id"), nullable=False),
    Column("created_at", DateTime, default=func.now()),
    UniqueConstraint("showtime_id", "seat", name="uq_booking_showtime_seat"),
)
```

### Path: docs/available_models.md

```markdown
<!--
DOKUMENTASI MODEL (SINGKAT)

Tujuan:
- Tetapkan model embedding & LLM yang disetujui; hindari model deprecated.

Model disetujui:
- Embedding: models/gemini-embedding-001
- Base LLM: gemini-2.5-flash

Aturan perubahan:
1. Verifikasi model ada dan TIDAK deprecated di konsol/API.
2. Jika tidak tersedia: laporkan ke maintainer; jangan ganti spekulatif.
3. Catat perubahan (model, alasan, tanggal, referensi) dan sertakan tes singkat.

Runtime:
- Jika inisialisasi gagal: keluarkan error jelas yang menunjuk file ini. Jangan fallback otomatis.

Kontak:
- Maintainer: RafiWangsaSeniang (lihat repo/issue tracker).
-->

```

### Path: docs/langchain-cookbook.md

```markdown
Basis Pengetahuan LangChain & LangGraph untuk AI Copilot (Sintaks Terbaru)Dokumen ini adalah referensi sintaks yang padat dan akurat, dirancang khusus untuk AI Coding Assistants. Tujuannya adalah untuk menyediakan pola kode modern yang valid untuk LangChain dan LangGraph, dengan fokus utama pada LangChain Expression Language (LCEL) dan arsitektur stateful LangGraph.BAGIAN 1: LANGCHAIN CORE & LCELBagian ini mencakup paradigma fundamental dari LangChain modern: LangChain Expression Language (LCEL). Ini adalah dasar untuk membangun semua alur kerja.1.1. LCEL (LangChain Expression Language) - The Pipe |Operator | (pipe) adalah mekanisme deklaratif utama untuk merangkai komponen Runnable menjadi sebuah sekuens. Pendekatan ini memungkinkan LangChain untuk mengoptimalkan eksekusi runtime secara otomatis, termasuk dukungan untuk streaming, pemanggilan asinkron, dan paralelisasi.1SintaksPython# Operator `|` secara implisit membuat sebuah RunnableSequence.
# Output dari komponen di sebelah kiri menjadi input untuk komponen di sebelah kanan.
chain = runnable1 | runnable2 | runnable3
Contoh MinimalisPython# prompt (Runnable) -> model (Runnable) -> parser (Runnable)
chain = prompt | model | parser
1.2. Konfigurasi Runnable (.with_config)Metode .with_config() digunakan untuk melampirkan konfigurasi runtime ke pemanggilan Runnable (chain). Ini adalah cara standar untuk meneruskan parameter dinamis seperti ID sesi, metadata untuk pelacakan (tracing), atau callback kustom tanpa mengubah definisi chain itu sendiri.3SintaksPython# Memanggil chain dengan konfigurasi spesifik.
chain.invoke(input, config={"key": "value"})

# Membuat instance chain baru dengan konfigurasi yang terikat secara permanen.
configured_chain = chain.with_config(callbacks=my_callbacks)
Contoh Minimalis (dengan Callbacks)Pythonfrom langchain_core.callbacks import BaseCallbackHandler

# Definisikan sebuah callback handler kustom
class MyCallbackHandler(BaseCallbackHandler):
    def on_chain_start(self, serialized, inputs, **kwargs):
        print(f"Chain started with inputs: {inputs}")

# Buat instance chain
# (Asumsikan 'prompt', 'model', dan 'parser' sudah didefinisikan)
chain = prompt | model | parser

# Buat instance chain baru dengan callback terikat
chain_with_callbacks = chain.with_config(callbacks=[MyCallbackHandler()])

# Panggil chain; callback akan otomatis terpicu
chain_with_callbacks.invoke({"input": "Tell me a fact."})
BAGIAN 2: KOMPONEN UTAMA (MODERN)Bagian ini merinci blok bangunan esensial untuk sebagian besar aplikasi LangChain, dengan penekanan pada path import modular yang modern.2.1. Models (Chat)Model bahasa diimpor dari paket integrasi spesifik (misalnya, langchain_google_genai, langchain_openai), bukan dari langchain atau langchain_community. Ini adalah bagian dari arsitektur modular LangChain.5Class: ChatGoogleGenerativeAIImport StatementPythonfrom langchain_google_genai import ChatGoogleGenerativeAI
Contoh InisialisasiPython# Pastikan environment variable GOOGLE_API_KEY sudah di-set
# gemini-2.5-flash adalah model yang cepat dan memiliki free tier.
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
2.2. Prompt TemplatesChatPromptTemplate adalah standar untuk membuat prompt untuk model berbasis chat. Metode from_messages menyediakan cara yang paling ringkas dan mudah dibaca untuk mendefinisikan peran dan konten pesan.7Class: ChatPromptTemplateImport StatementPythonfrom langchain_core.prompts import ChatPromptTemplate
Contoh InisialisasiPython# Menggunakan daftar tuple (role, content)
prompt = ChatPromptTemplate.from_messages()
2.3. Output ParsersOutput parser mengubah output mentah dari model menjadi format yang lebih dapat digunakan. StrOutputParser dan JsonOutputParser adalah dua parser yang paling umum digunakan dan bersifat model-agnostik.8Class: StrOutputParserDeskripsi: Mengurai output model (biasanya AIMessage) menjadi string sederhana.Import StatementPythonfrom langchain_core.output_parsers import StrOutputParser
Contoh InisialisasiPythonparser = StrOutputParser()
Class: JsonOutputParserDeskripsi: Mengurai output model menjadi objek JSON. Ini bekerja dengan menyuntikkan instruksi format ke dalam prompt, membuatnya kompatibel dengan model LLM manapun yang mampu menghasilkan JSON.10Import StatementPythonfrom langchain_core.output_parsers import JsonOutputParser
Contoh InisialisasiPythonparser = JsonOutputParser()
2.4. EmbeddingsEmbeddings adalah komponen krusial dalam RAG yang mengubah teks menjadi representasi vektor numerik untuk pencarian kesamaan.Class: GoogleGenerativeAIEmbeddingsImport StatementPythonfrom langchain_google_genai import GoogleGenerativeAIEmbeddings
Contoh InisialisasiPython# Model embedding-001 adalah model yang efisien dan serbaguna.
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
BAGIAN 3: CHAINS & MEMORY (MODERN)Bagian ini menunjukkan cara menggabungkan komponen-komponen di atas menjadi pola fungsional untuk interaksi stateless dan stateful.3.1. Membangun Chain SederhanaPola kanonis untuk chain sederhana adalah sekuens prompt | model | parser. Ini adalah fondasi dari hampir semua alur kerja LCEL.Pola Kode LengkapPythonfrom langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 1. Inisialisasi komponen
prompt = ChatPromptTemplate.from_messages()
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
parser = StrOutputParser()

# 2. Rangkai komponen menggunakan LCEL
chain = prompt | model | parser

# 3. Panggil chain dengan.invoke() untuk respons penuh
result = chain.invoke({"topic": "the moon"})
print(result)
Contoh Streaming dengan.stream()Salah satu keunggulan utama LCEL adalah dukungan streaming bawaan, yang memungkinkan output diterima secara bertahap.Python# Streaming response
for chunk in chain.stream({"topic": "the moon"}):
    print(chunk, end="", flush=True)
3.2. Chain dengan Memori PercakapanMemori percakapan diimplementasikan dengan membungkus chain stateless menggunakan RunnableWithMessageHistory. Pola ini memisahkan logika inti aplikasi dari manajemen state, memungkinkan backend memori (misalnya, in-memory, Redis, SQL) untuk ditukar dengan mudah.11Class Kunci: RunnableWithMessageHistoryImport StatementPythonfrom langchain_core.prompts import MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
Pola Kode LengkapPython# Asumsikan 'model' dan 'parser' sudah diinisialisasi dari contoh sebelumnya

# 1. Buat prompt yang menyertakan placeholder untuk riwayat pesan
prompt_with_history = ChatPromptTemplate.from_messages()

# 2. Buat chain inti
chain = prompt_with_history | model | parser

# 3. Buat penyimpanan memori (biasanya per sesi)
store = {}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# 4. Bungkus chain inti dengan RunnableWithMessageHistory
chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)

# 5. Panggil chain dengan config yang berisi session_id
config = {"configurable": {"session_id": "user123"}}
response = chain_with_history.invoke({"input": "Hi, I'm Bob!"}, config=config)
print(response)

# Panggil lagi, chain akan memiliki akses ke riwayat percakapan
response_2 = chain_with_history.invoke({"input": "What's my name?"}, config=config)
print(response_2)
BAGIAN 4: RAG (RETRIEVAL-AUGMENTED GENERATION)Bagian ini merinci pola LCEL paling penting untuk aplikasi RAG, yang menggabungkan pengambilan data dengan generasi bahasa.4.1. RetrieverSebuah retriever adalah Runnable yang mengambil dokumen sebagai respons terhadap sebuah query. Cara paling umum untuk membuatnya adalah dari instance vector store.SintaksPython# Asumsikan 'vectorstore' adalah instance yang sudah dikonfigurasi
# (misalnya, dari FAISS, Chroma, Pinecone)
retriever = vectorstore.as_retriever()
4.2. Merangkai Chain RAGPola RAG dalam LCEL memerlukan "percabangan" input awal (pertanyaan pengguna) ke dua jalur paralel: satu ke retriever untuk mendapatkan konteks, dan satu lagi untuk diteruskan ke prompt. RunnableParallel dan RunnablePassthrough adalah kunci untuk mencapai alur data ini.13Class Kunci: RunnablePassthrough, RunnableParallelImport StatementPythonfrom langchain_core.runnables import RunnablePassthrough, RunnableParallel
Pola Kode LengkapPython# Asumsikan 'retriever', 'model', dan 'parser' sudah diinisialisasi
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel

# 1. Buat prompt RAG yang membutuhkan 'context' dan 'question'
template = """
Answer the question based only on the following context:
{context}

Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)

# 2. Buat setup untuk memproses input secara paralel
# - 'context' diisi oleh retriever
# - 'question' diteruskan dari input asli
setup = RunnableParallel(
    context=retriever,
    question=RunnablePassthrough()
)

# 3. Rangkai chain RAG lengkap
rag_chain = setup | prompt | model | parser

# 4. Panggil chain RAG
result = rag_chain.invoke("Where did Harrison work?")
print(result)
Catatan: setup juga dapat ditulis sebagai dictionary literal: {"context": retriever, "question": RunnablePassthrough()}.BAGIAN 5: LANGGRAPH - ALUR KERJA STATEFULLangGraph memperluas LCEL untuk membangun alur kerja yang stateful dan siklik (dengan loop), yang penting untuk agen. Konsep intinya adalah objek State yang eksplisit dan dapat dimodifikasi yang diedarkan di antara node-node dalam sebuah graf.155.1. StateState dari sebuah graf didefinisikan menggunakan TypedDict. Ini berfungsi sebagai skema untuk memori bersama dari graf, memastikan bahwa semua node membaca dan menulis ke struktur data yang konsisten.16Pola: Menggunakan TypedDictImport StatementPythonfrom typing import TypedDict, List
Contoh Definisi StatePythonfrom typing import TypedDict, List

# Mendefinisikan struktur state untuk graf.
# Setiap kunci adalah sebuah field dalam state bersama.
class MyGraphState(TypedDict):
    question: str
    documents: List[str]
    generation: str
5.2. Membangun GrafSetelah State didefinisikan, StateGraph digunakan untuk mendaftarkan node (fungsi) dan edge (transisi) untuk membangun alur kerja.Class Kunci: StateGraph, ENDImport StatementPythonfrom langgraph.graph import StateGraph, END
Pola Kode LengkapPythonfrom langgraph.graph import StateGraph, END

# Asumsikan ada fungsi 'retrieve' dan 'generate' yang menerima state
# dan mengembalikan pembaruan state dalam bentuk dictionary.
def retrieve(state):
    print("---NODE: RETRIEVE---")
    #... logika untuk mengambil dokumen
    return {"documents": ["doc1", "doc2"], "question": state["question"]}

def generate(state):
    print("---NODE: GENERATE---")
    #... logika untuk menghasilkan respons
    return {"generation": "This is the generated response."}

# 1. Definisikan alur kerja dengan StateGraph
workflow = StateGraph(MyGraphState)

# 2. Tambahkan node ke graf
workflow.add_node("retriever", retrieve)
workflow.add_node("generator", generate)

# 3. Tentukan titik masuk (entry point)
workflow.set_entry_point("retriever")

# 4. Tambahkan edge (penghubung antar node)
workflow.add_edge("retriever", "generator")
workflow.add_edge("generator", END) # Mengakhiri graf setelah generator

# 5. Kompilasi graf menjadi objek yang dapat dijalankan
app = workflow.compile()

# 6. Panggil graf dengan input awal
inputs = {"question": "What is LangGraph?"}
for output in app.stream(inputs):
    for key, value in output.items():
        print(f"Output dari node '{key}': {value}")

```

### Path: docs/LogRisetLama.md

```markdown
## Catatan Riset: Evolusi Desain Agen Booking Bioskop Tiketa

### Latar Belakang & Tujuan Awal
Proyek ini dimulai dengan tujuan membangun agen percakapan yang *robust* untuk menangani pemesanan tiket bioskop. Arsitektur awal yang dipilih adalah **State Machine** (via LangGraph) yang dikombinasikan dengan **Heuristic Matching**.

Pendekatan ini dipilih untuk memberikan "pagar pembatas" (guardrails) yang kaku pada LLM, memastikan alur transaksi (Film -> Jadwal -> Kursi -> Konfirmasi) diikuti dengan benar dan mencegah halusinasi.

### Metode Awal: Heuristic Matching (State Machine Kaku)

Arsitektur awal sangat bergantung pada logika Python yang eksplisit untuk memandu LLM:

1.  **`TicketAgentState` Kaku:** *State* melacak tidak hanya data (`movie_id`), tetapi juga alur percakapan (`current_question: "ask_movie"`).
2.  **Klasifikasi Generik:** Satu node `classify_intent` (dengan tool `extract_intent_and_entities`) digunakan untuk menebak niat dan entitas user secara umum.
3.  **Logika Heuristik Berat:** Fungsi-fungsi inti seperti `_match_movie_from_text` dan `_match_showtime_from_text` dibuat untuk mem-parsing input mentah user ("yang ketiga", "jam 7 malam", "aot") dan mencocokkannya dengan data yang ada di *state* (`candidate_movies`, `available_showtimes`) menggunakan `regex` dan logika `if-else`.

### Permasalahan yang Ditemukan ("Heuristic Hell")

Setelah implementasi dan pengujian, pendekatan Heuristic Matching terbukti sangat rapuh dan tidak skalabel. Masalah yang muncul bersifat fundamental:

1.  **Beban Kognitif yang Salah:** Arsitektur ini memaksa *developer* (kita) untuk mengantisipasi *setiap* variasi linguistik pengguna. Kita pada dasarnya membangun NLU (Natural Language Understanding) engine yang buruk dari nol, sementara kita memiliki LLM yang sangat mampu diabaikan.
2.  **Kode Rapuh & Kompleks:** Setiap *edge case* baru ("3" vs "jam 3", "anime" vs "animation", "kimi no nawa" vs "your name") membutuhkan penambalan `regex` atau `if-else` baru. Ini mengarah ke kode yang panjang, sulit dipelihara, dan penuh bug tersembunyi.
3.  **Kebocoran State (State Leaks):** Ketika heuristik gagal (misal, `_match_showtime_from_text` mengembalikan `None`), *state* tidak diperbarui. `main_router` kemudian bingung dan sering kali salah merutekan alur (misal, "bocor" ke `browsing_agent` di tengah alur booking), yang menyebabkan pengalaman pengguna yang rusak (amnesia, looping, halusinasi).
4.  **Kegagalan Fleksibilitas:** Pendekatan ini sangat buruk dalam menangani perubahan pikiran atau kueri "satu tembakan" (*one-shot*) di mana pengguna memberikan semua informasi sekaligus.

Singkatnya, kita berakhir di **"neraka heuristik" (heuristic hell)**, di mana kita lebih banyak menghabiskan waktu untuk menambal logika Python daripada memanfaatkan kekuatan kognitif LLM.

### Perubahan Pendekatan: Contextual Selector Pattern

Untuk mengatasi masalah ini, kami mempensiunkan pendekatan Heuristic Matching dan beralih ke **Contextual Selector Pattern**.

**Konsep Inti:**
Daripada menggunakan logika Python untuk *menebak* maksud user, kita **meminta LLM untuk memilih** dari daftar opsi yang valid.

**Implementasi Baru:**
1.  **Hapus Heuristik:** Fungsi `_match_movie_from_text` dan `_match_showtime_from_text` (dan regex kompleksnya) **dihapus seluruhnya**.
2.  **Node Klasifikasi Cerdas:** `node_classify_intent` menjadi jauh lebih cerdas dan sadar konteks.
    * Jika `current_question == "ask_movie"`, node ini **secara dinamis membangun prompt baru** yang berisi daftar `candidate_movies`.
    * LLM kemudian diinstruksikan: "Ini input user: 'yang ketiga'. Ini daftarnya: [1. Akira (ID: 1), 2. Gundam (ID: 6), 3. Your Name (ID: 2)]. Kembalikan HANYA ID yang benar."
    * LLM, dengan kemampuan kognitifnya, akan dengan mudah mencocokkan "yang ketiga" atau "your name" ke `ID: 2`.
3.  **Peran Dibalik:**
    * **Sebelumnya:** Python bekerja keras (regex), LLM menebak secara generik.
    * **Sekarang:** LLM bekerja keras (pencocokan kontekstual), Python hanya memvalidasi output (misal, `if result.isdigit()`).

### Keuntungan Pendekatan Baru

1.  **Memanfaatkan Kognisi LLM:** Kita menggunakan LLM untuk tugas yang paling cocok: pemahaman bahasa alami yang bernuansa.
2.  **Kode Lebih Bersih & Sederhana:** Menghapus ratusan baris kode heuristik yang rapuh.
3.  **Anti-Halusinasi:** LLM tetap terkendali. Ia *hanya bisa* memilih dari ID valid yang kita berikan di dalam *prompt* dinamis, tidak bisa mengarang ID atau judul film sendiri.
4.  **Lebih Robust:** Jauh lebih baik dalam menangani variasi linguistik ("yang rabu", "jam 4 sore", "no. 3") tanpa perlu kode tambahan.
5.  **Perbaikan State yang Jelas:** Karena LLM mengembalikan ID yang pasti, *state* (`current_movie_id`, `current_showtime_id`) diperbarui secara andal, mencegah "kebocoran" alur.
```

### Path: docs/schema.sql

```sql
-- Database Schema for Tiketa RDS:
-- This file is for reference and documentation purposes.

-- DBeaver DDL Script
-- Tables
-- public.genres definition

-- Drop table
-- DROP TABLE public.genres;

CREATE TABLE public.genres (
    id serial4 NOT NULL,
    "name" varchar(120) NOT NULL,
    created_at timestamp NULL,
    CONSTRAINT genres_name_key UNIQUE (name),
    CONSTRAINT genres_pkey PRIMARY KEY (id)
);


-- public.movies definition

-- Drop table
-- DROP TABLE public.movies;

CREATE TABLE public.movies (
    id serial4 NOT NULL,
    title varchar(255) NOT NULL,
    description text NULL,
    studio_number int4 NOT NULL,
    poster_path varchar(255) NULL,
    backdrop_path varchar(255) NULL,
    release_date date NULL,
    trailer_youtube_id varchar(20) NULL,
    created_at timestamp NULL,
    CONSTRAINT movies_pkey PRIMARY KEY (id),
    CONSTRAINT movies_studio_number_key UNIQUE (studio_number)
);


-- public.movie_genres definition

-- Drop table
-- DROP TABLE public.movie_genres;

CREATE TABLE public.movie_genres (
    movie_id int4 NOT NULL,
    genre_id int4 NOT NULL,
    CONSTRAINT movie_genres_pkey PRIMARY KEY (movie_id, genre_id),
    CONSTRAINT movie_genres_genre_id_fkey FOREIGN KEY (genre_id) REFERENCES public.genres(id),
    CONSTRAINT movie_genres_movie_id_fkey FOREIGN KEY (movie_id) REFERENCES public.movies(id)
);


-- public.showtimes definition

-- Drop table
-- DROP TABLE public.showtimes;

CREATE TABLE public.showtimes (
    id serial4 NOT NULL,
    movie_id int4 NOT NULL,
    "time" timestamp NOT NULL,
    is_archived bool NOT NULL,
    created_at timestamp NULL,
    CONSTRAINT showtimes_pkey PRIMARY KEY (id),
    CONSTRAINT showtimes_movie_id_fkey FOREIGN KEY (movie_id) REFERENCES public.movies(id)
);


-- public.bookings definition

-- Drop table
-- DROP TABLE public.bookings;

CREATE TABLE public.bookings (
    id serial4 NOT NULL,
    "user" varchar(255) NOT NULL,
    seat varchar(10) NOT NULL,
    showtime_id int4 NOT NULL,
    created_at timestamp NULL,
    CONSTRAINT bookings_pkey PRIMARY KEY (id),
    CONSTRAINT uq_booking_showtime_seat UNIQUE (showtime_id, seat),
    CONSTRAINT bookings_showtime_id_fkey FOREIGN KEY (showtime_id) REFERENCES public.showtimes(id)
);
```

### Path: tools/__init__.py

```python
"""Data package exposing booking tools."""

```

### Path: tools/bookings.py

```python
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
```
.
├── .env
├── .gitignore
├── requirements.txt
├── run_agent.py
├── agent/
│   ├── __init__.py
│   ├── config.py
│   ├── nodes.py
│   ├── prompts.py
│   ├── state.py
│   └── workflow.py
├── data/
│   ├── __init__.py
│   ├── movies.py
│   ├── seats.py
│   └── timezone.py
├── db/
│   ├── __init__.py
│   └── schema.py
├── docs/
│   ├── LogRisetLama.md
│   ├── available_models.md
│   ├── langchain-cookbook.md
│   ├── schema.sql
│   └── full_project_context.md  (berkas ini)
├── tools/
│   ├── __init__.py
│   └── bookings.py
└── ui/
    ├── gradio_app.py
    └── static/
        ├── favicon.ico  (binary asset, tidak diekstrak)
        └── favicon.png  (binary asset, tidak diekstrak)
```

## Bagian 2: Dependensi (requirements.txt)

```text
gradio==5.49.1
gradio_client==1.13.3
langgraph==1.0.1
langgraph-checkpoint==3.0.0
langgraph-prebuilt==1.0.1
langgraph-sdk==0.2.9
langchain-core==1.0.1
langchain-google-genai==3.0.0
google-ai-generativelanguage==0.9.0
langsmith==0.4.38
SQLAlchemy==2.0.44
python-dotenv==1.2.1
pydantic==2.11.10
psycopg2-binary
```

## Bagian 3: Konfigurasi Lingkungan (.env.example)

Tidak terdapat `.env.example`. Variabel lingkungan yang aktif saat ini (tanpa menampilkan nilai) adalah:

- DATABASE_URL
- GOOGLE_API_KEY
- LANGSMITH_TRACING
- LANGSMITH_ENDPOINT
- LANGSMITH_API_KEY
- LANGSMITH_PROJECT

## Bagian 4: Kode Lengkap per File

### Path: .gitignore

```gitignore
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[codz]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
#  Usually these files are written by a python script from a template
#  before PyInstaller builds the exe, so as to inject date/other infos into it.
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py.cover
.hypothesis/
.pytest_cache/
cover/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
.pybuilder/
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
#   For a library or package, you might want to ignore these files since the code is
#   intended to run in multiple environments; otherwise, check them in:
# .python-version

# pipenv
#   According to pypa/pipenv#598, it is recommended to include Pipfile.lock in version control.
#   However, in case of collaboration, if having platform-specific dependencies or dependencies
#   having no cross-platform support, pipenv may install dependencies that don't work, or not
#   install all needed dependencies.
#Pipfile.lock

# UV
#   Similar to Pipfile.lock, it is generally recommended to include uv.lock in version control.
#   This is especially recommended for binary packages to ensure reproducibility, and is more
#   commonly ignored for libraries.
#uv.lock

# poetry
#   Similar to Pipfile.lock, it is generally recommended to include poetry.lock in version control.
#   This is especially recommended for binary packages to ensure reproducibility, and is more
#   commonly ignored for libraries.
#   https://python-poetry.org/docs/basic-usage/#commit-your-poetrylock-file-to-version-control
#poetry.lock
#poetry.toml

# pdm
#   Similar to Pipfile.lock, it is generally recommended to include pdm.lock in version control.
#   pdm recommends including project-wide configuration in pdm.toml, but excluding .pdm-python.
#   https://pdm-project.org/en/latest/usage/project/#working-with-version-control
#pdm.lock
#pdm.toml
.pdm-python
.pdm-build/

# pixi
#   Similar to Pipfile.lock, it is generally recommended to include pixi.lock in version control.
#pixi.lock
#   Pixi creates a virtual environment in the .pixi directory, just like venv module creates one
#   in the .venv directory. It is recommended not to include this directory in version control.
.pixi

# PEP 582; used by e.g. github.com/David-OConnor/pyflow and github.com/pdm-project/pdm
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.envrc
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# pytype static type analyzer
.pytype/

# Cython debug symbols
cython_debug/

# PyCharm
#  JetBrains specific template is maintained in a separate JetBrains.gitignore that can
#  be found at https://github.com/github/gitignore/blob/main/Global/JetBrains.gitignore
#  and can be added to the global gitignore or merged into this file.  For a more nuclear
#  option (not recommended) you can uncomment the following to ignore the entire idea folder.
#.idea/

# Abstra
# Abstra is an AI-powered process automation framework.
# Ignore directories containing user credentials, local state, and settings.
# Learn more at https://abstra.io/docs
.abstra/

# Visual Studio Code
#  Visual Studio Code specific template is maintained in a separate VisualStudioCode.gitignore 
#  that can be found at https://github.com/github/gitignore/blob/main/Global/VisualStudioCode.gitignore
#  and can be added to the global gitignore or merged into this file. However, if you prefer, 
#  you could uncomment the following to ignore the entire vscode folder
# .vscode/

# Ruff stuff:
.ruff_cache/

# PyPI configuration file
.pypirc

# Cursor
#  Cursor is an AI-powered code editor. `.cursorignore` specifies files/directories to
#  exclude from AI features like autocomplete and code analysis. Recommended for sensitive data
#  refer to https://docs.cursor.com/context/ignore-files
.cursorignore
.cursorindexingignore

# Marimo
marimo/_static/
marimo/_lsp/
__marimo__/
```

### Path: requirements.txt

```text
gradio==5.49.1
gradio_client==1.13.3
langgraph==1.0.1
langgraph-checkpoint==3.0.0
langgraph-prebuilt==1.0.1
langgraph-sdk==0.2.9
langchain-core==1.0.1
langchain-google-genai==3.0.0
google-ai-generativelanguage==0.9.0
langsmith==0.4.38
SQLAlchemy==2.0.44
python-dotenv==1.2.1
pydantic==2.11.10
psycopg2-binary
```

### Path: run_agent.py

```python
import argparse
import os

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from agent.config import get_engine, setup_environment


def _compute_output_to_show(final_state) -> str:
    agent_messages = final_state.get("messages", [])
    last_agent_message = agent_messages[-1] if agent_messages else None

    output_to_show = "(Agen tidak memberikan respons)"

    if isinstance(last_agent_message, AIMessage):
        if getattr(last_agent_message, "tool_calls", None):
            last_tool_call = last_agent_message.tool_calls[-1]
            if last_tool_call["name"] == "ask_user":
                output_to_show = last_tool_call["args"]["question"]
            else:
                output_to_show = "(Agen sedang memproses...)"
        elif getattr(last_agent_message, "content", None):
            output_to_show = str(last_agent_message.content)
    elif isinstance(last_agent_message, ToolMessage):
        output_to_show = str(last_agent_message.content)

    return output_to_show


def run_cli() -> None:
    setup_environment()
    get_engine()
    print("--- Agen Manajer Booking (CLI) ---")
    print("Ketik 'exit' untuk keluar.")
    # Import setelah env siap untuk menghindari ADC default credentials
    from agent.workflow import app, ensure_model_bound, get_initial_state
    ensure_model_bound()
    state = get_initial_state(force_refresh_movies=True)

    while True:
        user_text = input("\nAnda: ").strip()
        if not user_text:
            continue
        if user_text.lower() == "exit":
            print("Sampai jumpa!")
            break

        state["messages"].append(HumanMessage(content=user_text))
        print("\nAgen:")

        final_state = app.invoke(state, {"recursion_limit": 50})
        bot_text = _compute_output_to_show(final_state)
        print(bot_text)

        state = final_state  # lanjutan percakapan gunakan state terbaru


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Tiketa booking agent entrypoint")
    parser.add_argument(
        "--mode",
        choices=("gradio", "cli"),
        default="gradio",
        help="Pilih 'gradio' untuk UI web atau 'cli' untuk mode terminal.",
    )
    parser.add_argument(
        "--share",
        action="store_true",
        help="Gunakan opsi ini untuk membuat public link Gradio.",
    )
    parser.add_argument(
        "--inline",
        action="store_true",
        help="Tampilkan UI secara inline (berguna saat dipanggil dari notebook).",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Alamat bind untuk server Gradio (default: 0.0.0.0).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=7860,
        help="Port untuk server Gradio (default: 7860).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.mode == "cli":
        run_cli()
        return

    setup_environment()
    get_engine()
    from agent.workflow import ensure_model_bound
    ensure_model_bound()
    from ui.gradio_app import launch_demo
    print("--- Agen Manajer Booking (Gradio) ---")
    print("Mengaktifkan antarmuka web di http://127.0.0.1:7860 ...")

    # Build launch kwargs and only pass favicon_path if the file exists to avoid
    # passing a non-existent path (which some environments may treat as an error).
    launch_kwargs = {
        "inline": args.inline,
        "share": args.share,
        "server_name": args.host,
        "server_port": args.port,
    }

    # Prefer an .ico file (better legacy browser support). Fall back to png if ico missing.
    default_favicon_ico = os.path.join("ui", "static", "favicon.ico")
    default_favicon_png = os.path.join("ui", "static", "favicon.png")
    try:
        if os.path.exists(default_favicon_ico):
            launch_kwargs["favicon_path"] = default_favicon_ico
        elif os.path.exists(default_favicon_png):
            launch_kwargs["favicon_path"] = default_favicon_png
    except Exception:
        # If anything goes wrong while checking the file system, skip favicon.
        pass

    launch_demo(**launch_kwargs)


if __name__ == "__main__":
    main()
```

### Path: agent/__init__.py

```python
"""Data package exposing agent"""

```

### Path: agent/config.py

```python
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
        # Enable pre_ping to automatically recycle stale/idle connections (e.g., on cloud envs)
        _engine = create_engine(database_url, pool_pre_ping=True)
    return _engine


def get_metadata():
    return _metadata
```

### Path: agent/nodes.py

```python
from typing import Literal

from langchain_core.messages import AIMessage, ToolMessage, SystemMessage, HumanMessage
from sqlalchemy import select

from agent.config import get_engine
from agent.prompts import get_simple_master_prompt
from agent.state import TicketAgentState, get_stable_history_slice
from data.timezone import from_db_utc_naive_to_local_display
from db.schema import movies_table, showtimes_table
from tools.bookings import (
    MovieDetails,
    SeatAvailabilityInfo,
    ask_user,
    book_tickets_tool,
    get_available_seats,
    get_movie_details,
    get_showtimes,
    signal_confirmation_ready,
)

model_with_tools = None


def assign_model(bound_model) -> None:
    global model_with_tools
    model_with_tools = bound_model


def _sanitize_messages_for_gemini(messages):
    """
    Pastikan urutan pesan valid untuk Gemini function calling:
    - Hapus AIMessage di bagian akhir yang tidak memiliki tool_calls,
      supaya turn berikutnya dimulai dari HumanMessage atau ToolMessage.
    """
    msgs = list(messages)
    # Buang semua ekor yang bukan Human/Tool agar turn berikutnya valid untuk function calling
    while msgs and isinstance(msgs[-1], (AIMessage, SystemMessage)):
        msgs.pop()
    return msgs


def node_booking_manager(state: TicketAgentState) -> dict:
    print("--- NODE: Booking Manager ---")

    # 1. Dapatkan HANYA system prompt
    system_prompt_list = get_simple_master_prompt(state)

    # 2. GABUNGKAN system prompt dengan histori chat dari state
    safe_history = get_stable_history_slice(state.get("messages", []), max_messages=72)
    safe_history = _sanitize_messages_for_gemini(safe_history)
    # Fallback guard: jika setelah sanitasi ekor bukan Human/Tool (atau kosong),
    # tambahkan satu pesan terakhir yang valid (Human atau Tool) dari state agar Gemini tidak error.
    if not safe_history or not isinstance(safe_history[-1], (HumanMessage, ToolMessage)):
        original_msgs = state.get("messages", []) or []
        for m in reversed(original_msgs):
            if isinstance(m, (HumanMessage, ToolMessage)):
                # Hindari duplikasi trivial jika sama persis sudah di ekor
                if not safe_history or safe_history[-1] is not m:
                    safe_history.append(m)
                break
    messages_for_llm = system_prompt_list + safe_history

    # Siapkan dictionary untuk update state
    current_summary = state.get("context_seats_summary", "N/A")
    updates = {
        "messages": [],
        "last_error": None, # Sementara gini dulu aja, penanganan error masih agak problem
        "context_seats_summary": current_summary, # Biar konteks kursi tetap terbawa
    }
    ai_response = None

    try:
        # 3. SELALU Panggil LLM untuk Tool Call
        print("     > Meminta Tool Call...")
        if model_with_tools is None:
            raise RuntimeError("model_with_tools belum diinisialisasi. Panggil assign_model() dari workflow terlebih dahulu.")

        ai_response = model_with_tools.invoke(messages_for_llm)
        print(f"     > Hasil LLM (Tool Call): {ai_response.tool_calls}")
        updates["messages"].append(ai_response)

        if not ai_response.tool_calls:
            print(
                "     > Peringatan: LLM tidak memanggil tool (atau mungkin memang tidak perlu)."
            )
            updates["last_error"] = "LLM gagal memanggil tool." # ini dimatikan saja dulu, tidak manggil tool itu normal! 

        # 4. Proses SEMUA tool call
        for tool_call in ai_response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_id = tool_call["id"]

            tool_result_content = "Aksi dicatat."  # Default untuk tool aksi

            if tool_name == "record_selected_movie":
                selected_id = tool_args.get("selected_movie_id")
                if selected_id is not None:
                    updates["current_movie_id"] = selected_id
                    # Reset konteks bawahan
                    updates["context_showtimes"] = None
                    updates["current_showtime_id"] = None
                    updates["context_seats"] = None
                    updates["selected_seats"] = None
                    updates["context_seats_summary"] = "N/A"

            elif tool_name == "record_selected_showtime":
                selected_id = tool_args.get("selected_showtime_id")
                if selected_id is not None:
                    updates["current_showtime_id"] = selected_id
                    updates["context_seats"] = None
                    updates["selected_seats"] = None
                    updates["context_seats_summary"] = "N/A"

            elif tool_name == "record_selected_seats":
                seats_list = tool_args.get("selected_seats_list")
                if seats_list:
                    updates["selected_seats"] = (
                        seats_list
                    )
                else:
                    updates["last_error"] = "Agent mencoba rekam kursi kosong."
                    tool_result_content = "Error: Daftar kursi kosong."

            elif tool_name == "record_customer_name":
                name = tool_args.get("extracted_customer_name")
                if name:
                    updates["customer_name"] = name


            elif tool_name == "get_showtimes":
                try:
                    # EKSEKUSI tool-nya SEKARANG
                    showtimes_result = get_showtimes.invoke(tool_args)
                    updates["context_showtimes"] = showtimes_result  # Simpan konteks
                    tool_result_content = str(showtimes_result)
                except Exception as e:
                    updates["last_error"] = f"Gagal fetch showtimes: {e}"
                    tool_result_content = f"Error: {e}"
                    updates["context_showtimes"] = [
                        {"error": str(e)}
                    ]

            elif tool_name == "get_available_seats":
                try:
                    # EKSEKUSI tool-nya SEKARANG
                    seat_info: SeatAvailabilityInfo = get_available_seats.invoke(
                        tool_args
                    )
                    updates["context_seats"] = seat_info.available_list
                    updates["context_seats_summary"] = seat_info.summary_for_llm
                    tool_result_content = str(seat_info.model_dump())
                except Exception as e:
                    updates["last_error"] = f"Gagal fetch seats: {e}"
                    updates["context_seats_summary"] = "Error ambil kursi."
                    tool_result_content = f"Error: {e}"

            elif tool_name == "get_movie_details":
                # Eksekusi tool dan kirim hasilnya ke LLM sebagai ToolMessage
                try:
                    details: MovieDetails = get_movie_details.invoke(tool_args)
                    # Kirim payload lengkap agar LLM bisa menyusun jawaban/ask_user berikutnya
                    tool_result_content = str(details.model_dump())
                except Exception as e:
                    updates["last_error"] = f"Gagal fetch movie details: {e}"
                    tool_result_content = f"Error: {e}"

            elif tool_name == "ask_user":
                # EKSEKUSI tool-nya SEKARANG
                tool_result_content = ask_user.invoke(tool_args)
                # Router akan menangani __end__

            elif tool_name == "signal_confirmation_ready":
                # EKSEKUSI tool-nya SEKARANG
                tool_result_content = signal_confirmation_ready.invoke(tool_args)
                # Router akan menangani 'confirm'

            updates["messages"].append(
                ToolMessage(content=tool_result_content, tool_call_id=tool_id)
            )

    except Exception as e:
        print(f"     > ERROR saat pemanggilan LLM: {e}")
        updates["last_error"] = f"Gagal memproses langkah: {e}"
        if ai_response is None:
            error_msg = AIMessage(content=f"Maaf, terjadi error internal: {e}")
            updates["messages"].append(error_msg)

    return updates

def node_confirmation(state: TicketAgentState) -> dict:
    """
    Mengambil data DARI STATE, menampilkan rangkuman, dan mengeksekusi booking.
    Dipicu HANYA setelah tool 'signal_confirmation_ready' dipanggil.
    """
    print("--- NODE: Confirmation ---")

    movie_id = state.get("current_movie_id")
    showtime_id = state.get("current_showtime_id")
    seats = state.get("selected_seats")
    customer_name = state.get("customer_name")

    final_data = {
        "movie_id": movie_id,
        "showtime_id": showtime_id,
        "seats": seats,
        "customer_name": customer_name,
    }

    if not all(final_data.values()):  # Cek jika salah satu masih None
        print(
            f"    > ERROR: Data konfirmasi tidak lengkap di state! Data: {final_data}"
        )
        return {
            "messages": [
                AIMessage(
                    content=f"Terjadi error: Data pemesanan tidak lengkap untuk konfirmasi. Data: {final_data}"
                )
            ],
            "last_error": "Data tidak lengkap saat konfirmasi.",
        }

    # 2. Ambil detail (Nama film, Waktu tampil) untuk rangkuman
    # (Ini butuh query kecil ke DB)
    movie_title = "(Judul tidak ditemukan)"
    showtime_display = "(Jadwal tidak ditemukan)"
    try:
        engine = get_engine()
        with engine.connect() as conn:
            # Ambil judul film
            movie_res = conn.execute(
                select(movies_table.c.title).where(
                    movies_table.c.id == final_data["movie_id"]
                )
            ).first()
            if movie_res:
                movie_title = movie_res.title

            # Ambil waktu jadwal (dan konversi ke WIB display)
            showtime_res = conn.execute(
                select(showtimes_table.c.time).where(
                    showtimes_table.c.id == final_data["showtime_id"]
                )
            ).first()
            if showtime_res:
                showtime_display = from_db_utc_naive_to_local_display(showtime_res.time)

    except Exception as e:
        print(f"    > ERROR saat mengambil detail untuk konfirmasi: {e}")

    # 3. Buat Rangkuman Teks
    summary = (
        f"✅ **Konfirmasi Pesanan Anda:**\n"
        f"---------------------------\n"
        f"🎬 **Film:** {movie_title} (ID: {final_data['movie_id']})\n"
        f"🗓️ **Jadwal:** {showtime_display} (ID: {final_data['showtime_id']})\n"
        f"💺 **Kursi:** {', '.join(final_data['seats'])}\n"
        f"👤 **Atas Nama:** {final_data['customer_name']}\n"
        f"---------------------------\n"
        f"\n⏳ Memproses pemesanan..."
    )
    # Tampilkan rangkuman ke konsol (opsional)
    print(f"    > Rangkuman:\n{summary}")

    # 4. Eksekusi Booking (Panggil fungsi Python biasa)
    result_message = book_tickets_tool(
        showtime_id=final_data["showtime_id"],
        seats=final_data["seats"],
        customer_name=final_data["customer_name"],
    )

    print(f"    > Hasil Eksekusi: {result_message}")

    # 5. Kembalikan Pesan Final ke User
    booking_url = f"https://tiketa-rafi.space/book/{final_data['showtime_id']}"
    final_response = (
        f"{summary}\n\n"
        f"**Status:** {result_message}\n\n"
        f"🔗 Buka halaman showtime: {booking_url}\n"
        f"[Klik di sini untuk membuka]({booking_url})"
    )

    # Reset state setelah booking
    updates = {
        "messages": [AIMessage(content=final_response)],
        "current_movie_id": None,
        "current_showtime_id": None,
        "selected_seats": None,
        # "customer_name": None,
        "context_showtimes": None,
        "context_seats": None,
        "confirmation_data": None,
        "last_error": None,
    }
    return updates

def booking_router(
    state: TicketAgentState,
) -> Literal["confirm", "continue", "__end__"]:
    print("--- ROUTER: Booking Router ---")

    if state.get("last_error"):
        print(f"    > Rute: __end__ (ERROR terdeteksi: {state.get('last_error')})")
        return "__end__"

    messages = state["messages"]
    last_ai_message = None
    for msg in reversed(messages):
        if isinstance(msg, AIMessage):
            last_ai_message = msg
            break

    if not last_ai_message or not last_ai_message.tool_calls:
        print("    > Rute: __end__ (NO_TOOL_CALL / LLM bandel)")
        return "__end__"

    # Ambil tool call *pertama* (atau terakhir, tergantung logikamu)
    tool_call = last_ai_message.tool_calls[0]
    tool_name = tool_call["name"]

    if tool_name == "signal_confirmation_ready":
        print("    > Rute: confirm (data lengkap)")
        return "confirm"
    elif tool_name == "ask_user":
        print("    > Rute: __end__ (menunggu input user)")
        return "__end__"
    else:
        # Ini adalah tool Aksi (record_...) ATAU tool Data (get_...)
        print(f"    > Rute: continue (Aksi/Tool '{tool_name}' dipanggil, lanjut loop)")
        return "continue"
```

### Path: agent/prompts.py

```python
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
        "ask_user(question=\"Baik, Anda memilih kursi B2 dan C4. Atas nama siapa pemesanan ini?\")",
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
        f"\n**PETA KURSI (SEAT_MAP):**\n{seat_map_context_str}\n\n**KONTEKS DENAH:**\nLayar ada di bagian DEPAN. Baris M adalah baris PALING DEPAN (terdekat layar), dan baris A adalah baris PALING BELAKANG.",
        f"\n**INSTRUKSI FOKUS:**\n{focus_instruction}",
    ]

    system_prompt_content = "\n".join(prompt_lines)
    return [SystemMessage(content=system_prompt_content)]

```

    ### Path: agent/state.py

    ```python
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
        context_seats_summary: Optional[str]

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
    ```

    ### Path: agent/workflow.py

    ```python
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
        # TypedDicts should be instantiated via a plain dict literal
        return {
            "messages": [],
            "all_movies_list": movies_context,
            "current_movie_id": None,
            "current_showtime_id": None,
            "selected_seats": None,
            "customer_name": None,
            "context_showtimes": None,
            "context_seats": None,
            "context_seats_summary": "N/A",
            "confirmation_data": None,
            "last_error": None,
        }


    # PENYIMPANAN STATE (PERLU DIIMPLEMENTASIKAN LEBIH NANTI)
    session_states = {}
    SESSION_ID = "user_session_123"

    print("\n--- Agen Manajer Booking Siap! ---")
    print("Ketik 'exit' untuk keluar.")
    print("Contoh: 'mau pesan tiket', 'kimi no nawa', '2025-10-30', 'A1', 'Rafi'")
    ```

    ### Path: data/__init__.py

    ```python
    """Data package exposing sample movie metadata."""

    ```

    ### Path: data/movies.py

    ```python
    from datetime import date

    SAMPLE_MOVIES = [
        {
            "studio_number": 1,
            "title": "Spirited Away",
            "description": "A young girl navigates a spirit world to free her parents from a mysterious curse.",
            "poster_path": "https://images.weserv.nl/?url=theposterdb.com/api/assets/111928/view",
            "backdrop_path": "/backdrops/spirited_away.jpg",
            "release_date": date(2001, 7, 20),
            "trailer_youtube_id": "GAp2_0JJskk",
            "genre_ids": [16, 10751, 12],
            "genres": ["Animation", "Fantasy", "Family"],
        },
        {
            "studio_number": 2,
            "title": "Your Name",
            "description": "Two teens mysteriously swap bodies and race against time to change their intertwined fate. A very romantic and memorable movie by Makoto Shinkai.",
            "poster_path": "https://images.weserv.nl/?url=theposterdb.com/api/assets/90914/view",
            "backdrop_path": "/backdrops/your_name.jpg",
            "release_date": date(2016, 8, 26),
            "trailer_youtube_id": "k4xGqY5IDBE",
            "genre_ids": [16, 18, 10749],
            "genres": ["Animation", "Drama", "Romance"],
        },
        {
            "studio_number": 3,
            "title": "Akira",
            "description": "Neo-Tokyo faces chaos when a teen biker unlocks a government secret with psychic power.",
            "poster_path": "https://image.tmdb.org/t/p/original/6pG3nVF7uWvFPCrNRBGwZqFhoQT.jpg",
            "backdrop_path": "/backdrops/akira.jpg",
            "release_date": date(1988, 7, 16),
            "trailer_youtube_id": "nA8KmHC2Z-g",
            "genre_ids": [16, 28, 878],
            "genres": ["Animation", "Action", "Science Fiction"],
        },
        {
            "studio_number": 4,
            "title": "Ghost in the Shell",
            "description": "A cyborg detective hunts a hacker in a world where the line between human and machine blurs.",
            "poster_path": "https://images.weserv.nl/?url=theposterdb.com/api/assets/98465/view",
            "backdrop_path": "/backdrops/ghost_in_the_shell.jpg",
            "release_date": date(1995, 11, 18),
            "trailer_youtube_id": "rU6Matng9MU",
            "genre_ids": [16, 878, 53],
            "genres": ["Animation", "Science Fiction", "Thriller"],
        },
        {
            "studio_number": 5,
            "title": "Attack on Titan: Requiem",
            "description": "Alternate ending of Attack on Titan, or is it?",
            "poster_path": "https://image.tmdb.org/t/p/original/l1IrdT6ou25RfUHUwBiZ4sCcVFk.jpg",
            "backdrop_path": "/backdrops/aot_chronicle.jpg",
            "release_date": date(2020, 7, 17),
            "trailer_youtube_id": "E7WytLM2KvY",
            "genre_ids": [16, 28, 12],
            "genres": ["Animation", "Action", "Adventure"],
        },
        {
            "studio_number": 6,
            "title": "Mobile Suit Gundam SEED Freedom",
            "description": "In C.E.75, the fighting still continues. There are independence movements, and aggression by Blue Cosmos... In order to calm the situation, a global peace monitoring agency called COMPASS is established, with Lacus as its first president. As members of COMPASS, Kira and his comrades intervene into various regional battles. Then a newly established nation called Foundation proposes a joint operation against a Blue Cosmos stronghold.",
            "poster_path": "https://image.tmdb.org/t/p/original/1EBnttleJaKnWWyyEqfiSn76ZjT.jpg",
            "backdrop_path": "/backdrops/gundam_seed_freedom.jpg",
            "release_date": date(2024, 1, 26),
            "trailer_youtube_id": "Gsj6ToFTGgc",
            "genre_ids": [16, 28, 878],
            "genres": ["Animation", "Action", "Science Fiction"],
        },
        {
            "studio_number": 7,
            "title": "Interstellar",
            "description": "The adventures of a group of explorers who make use of a newly discovered wormhole to surpass the limitations on human space travel and conquer the vast distances involved in an interstellar voyage.",
            "poster_path": "https://image.tmdb.org/t/p/original/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
            "backdrop_path": "/backdrops/interstellar.jpg",
            "release_date": date(2014, 11, 7),
            "trailer_youtube_id": "zSWdZVtXT7E",
            "genre_ids": [12, 18, 878],
            "genres": ["Adventure", "Drama", "Science Fiction"],
        },
        {
            "studio_number": 8,
            "title": "Blade Runner 2049",
            "description": "A replicant blade runner uncovers a secret that could shatter the balance between humans and androids.",
            "poster_path": "https://image.tmdb.org/t/p/original/gajva2L0rPYkEWjzgFlBXCAVBE5.jpg",
            "backdrop_path": "/backdrops/blade_runner_2049.jpg",
            "release_date": date(2017, 10, 6),
            "trailer_youtube_id": "gCcx85zbxz4",
            "genre_ids": [18, 878, 53],
            "genres": ["Drama", "Science Fiction", "Thriller"],
        },
        {
            "studio_number": 9,
            "title": "Dune: Part Two",
            "description": "ABSOLUTE CINEMA, THE BEST FILM EVER MADE, ~ Rafi",
            "poster_path": "https://image.tmdb.org/t/p/original/6izwz7rsy95ARzTR3poZ8H6c5pp.jpg",
            "backdrop_path": "/backdrops/dune.jpg",
            "release_date": date(2021, 10, 22),
            "trailer_youtube_id": "U2Qp5pL3ovA",
            "genre_ids": [12, 18, 878],
            "genres": ["Adventure", "Drama", "Science Fiction"],
        },
        {
            "studio_number": 10,
            "title": "The Matrix",
            "description": "A hacker discovers reality is a simulation and joins a rebellion to free humanity.",
            "poster_path": "https://image.tmdb.org/t/p/original/p96dm7sCMn4VYAStA6siNz30G1r.jpg",
            "backdrop_path": "/backdrops/the_matrix.jpg",
            "release_date": date(1999, 3, 31),
            "trailer_youtube_id": "vKQi3bBA1y8",
            "genre_ids": [28, 878],
            "genres": ["Action", "Science Fiction"],
        },
        {
            "studio_number": 11,
            "title": "Star Wars: A New Hope",
            "description": "A farm boy becomes a hero in the Rebel Alliance's mission to destroy the Death Star.",
            "poster_path": "https://image.tmdb.org/t/p/original/2Cm0oygiJpk7tzboSvX8F86v8PW.jpg",
            "backdrop_path": "/backdrops/star_wars_a_new_hope.jpg",
            "release_date": date(1977, 5, 25),
            "trailer_youtube_id": "vZ734NWnAHA",
            "genre_ids": [12, 28, 878],
            "genres": ["Adventure", "Action", "Science Fiction"],
        },
        {
            "studio_number": 12,
            "title": "Mad Max: Fury Road",
            "description": "Warrior Imperator Furiosa joins forces with Max to escape a tyrant in a post-apocalyptic desert.",
            "poster_path": "https://image.tmdb.org/t/p/original/hA2ple9q4qnwxp3hKVNhroipsir.jpg",
            "backdrop_path": "/backdrops/mad_max_fury_road.jpg",
            "release_date": date(2015, 5, 15),
            "trailer_youtube_id": "hEJnMQG9ev8",
            "genre_ids": [28, 12, 878],
            "genres": ["Action", "Adventure", "Science Fiction"],
        },
        {
            "studio_number": 13,
            "title": "Everything Everywhere All at Once",
            "description": "An overwhelmed mother taps into multiverse versions of herself to save existence.",
            "poster_path": "https://image.tmdb.org/t/p/original/u68AjlvlutfEIcpmbYpKcdi09ut.jpg",
            "backdrop_path": "/backdrops/everything_everywhere.jpg",
            "release_date": date(2022, 3, 25),
            "trailer_youtube_id": "wxN1T1uxQ2g",
            "genre_ids": [28, 35, 878],
            "genres": ["Action", "Comedy", "Science Fiction"],
        },
        {
            "studio_number": 14,
            "title": "Black Panther",
            "description": "T'Challa returns to Wakanda to defend his throne and share his nation's power with the world.",
            "poster_path": "https://image.tmdb.org/t/p/original/uxzzxijgPIY7slzFvMotPv8wjKA.jpg",
            "backdrop_path": "/backdrops/black_panther.jpg",
            "release_date": date(2018, 2, 16),
            "trailer_youtube_id": "xjDjIWPwcPU",
            "genre_ids": [28, 12, 878],
            "genres": ["Action", "Adventure", "Science Fiction"],
        },
        {
            "studio_number": 15,
            "title": "The Dark Knight",
            "description": "Batman faces the Joker in a battle for Gotham's soul.",
            "poster_path": "https://image.tmdb.org/t/p/original/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
            "backdrop_path": "/backdrops/the_dark_knight.jpg",
            "release_date": date(2008, 7, 18),
            "trailer_youtube_id": "EXeTwQWrcwY",
            "genre_ids": [28, 80, 18],
            "genres": ["Action", "Crime", "Drama"],
        },
        {
            "studio_number": 16,
            "title": "Inception",
            "description": "A thief enters people's dreams to implant an idea that could change the world.",
            "poster_path": "https://image.tmdb.org/t/p/original/ljsZTbVsrQSqZgWeep2B1QiDKuh.jpg",
            "backdrop_path": "/backdrops/inception.jpg",
            "release_date": date(2010, 7, 16),
            "trailer_youtube_id": "YoHD9XEInc0",
            "genre_ids": [28, 878, 53],
            "genres": ["Action", "Science Fiction", "Thriller"],
        },
        {
            "studio_number": 17,
            "title": "Pulp Fiction",
            "description": "Interwoven crime stories collide in Tarantino's darkly comic classic.",
            "poster_path": "https://image.tmdb.org/t/p/original/vQWk5YBFWF4bZaofAbv0tShwBvQ.jpg",
            "backdrop_path": "/backdrops/pulp_fiction.jpg",
            "release_date": date(1994, 10, 14),
            "trailer_youtube_id": "s7EdQ4FqbhY",
            "genre_ids": [80, 53],
            "genres": ["Crime", "Thriller"],
        },
        {
            "studio_number": 18,
            "title": "Parasite",
            "description": "A poor family infiltrates a wealthy household, triggering unexpected consequences.",
            "poster_path": "https://image.tmdb.org/t/p/original/nMF2GX9SriEMbixRvI23KZwCs0U.jpg",
            "backdrop_path": "/backdrops/parasite.jpg",
            "release_date": date(2019, 5, 30),
            "trailer_youtube_id": "SEUXfv87Wpk",
            "genre_ids": [35, 18, 53],
            "genres": ["Comedy", "Drama", "Thriller"],
        },
        {
            "studio_number": 19,
            "title": "The Lord of the Rings: The Fellowship of the Ring",
            "description": "A hobbit and his allies embark on a quest to destroy a ring of ultimate evil.",
            "poster_path": "https://image.tmdb.org/t/p/original/6oom5QYQ2yQTMJIbnvbkBL9cHo6.jpg",
            "backdrop_path": "/backdrops/lotr_fellowship.jpg",
            "release_date": date(2001, 12, 19),
            "trailer_youtube_id": "V75dMMIW2B4",
            "genre_ids": [12, 14, 28],
            "genres": ["Adventure", "Fantasy", "Action"],
        },
        {
            "studio_number": 20,
            "title": "Coco",
            "description": "Iori's Favorite movie",
            "poster_path": "https://image.tmdb.org/t/p/original/6Ryitt95xrO8KXuqRGm1fUuNwqF.jpg",
            "backdrop_path": "/backdrops/coco.jpg",
            "release_date": date(2017, 10, 20),
            "trailer_youtube_id": "Rvr68u6k5sI",
            "genre_ids": [16, 12, 10751],
            "genres": ["Animation", "Adventure", "Family"],
        },
        {
            "studio_number": 21,
            "title": "La La Land",
            "description": "The only Good romance movie according to Locos Tacos Hermanos",
            "poster_path": "https://image.tmdb.org/t/p/original/uDO8zWDhfWwoFdKS4fzkUJt0Rf0.jpg",
            "backdrop_path": "/backdrops/la_la_land.jpg",
            "release_date": date(2016, 12, 9),
            "trailer_youtube_id": "0pdqf4P9MB8",
            "genre_ids": [35, 18, 10749],
            "genres": ["Comedy", "Drama", "Romance"],
        },
    ]
```