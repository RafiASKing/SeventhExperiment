# Log Riset dan Experiment: Arsitekstur, Metode dan Approach yang dipilih

## 1. Arsitektur V1: Explicit State Machine (The Rigid Approach/cara kaku)

### Desain Awal
Awalnya, sistem dibangun menggunakan pendekatan seperti DAG yang ketat dengan banyak node spesifik:
`Classify_Intent` -> `Browsing_Node` / `Booking_Node` -> `Find_Movie` -> `Find_Showtime` -> ...

### Kegagalan Struktural (Architectural Failures)
Setelah pengujian, arsitektur ini memiliki cacat fundamental yang membuat UX menjadi buruk ("Robotic"):

1.  **The "Intent Classification" Trap:**
    *   **Masalah:** Memaksa klasifikasi biner di awal (`browsing` vs `booking`) adalah kesalahan fatal.
    *   **Kasus Nyata:** User bertanya "Jadwal Dune jam berapa?". Ini secara teknis adalah *browsing* (melihat data), tapi secara implisit adalah langkah awal *booking*. Memisahkan node ini membuat state sering bocor atau salah routing.
    *   **Dampak:** User terjebak di *loop* browsing dan sulit pindah ke booking tanpa mereset percakapan.

2.  **Linearity vs. One-Shot:**
    *   **Masalah:** Graph linear memaksa user menjawab satu per satu (Film -> Jadwal -> Kursi).
    *   **Kasus Nyata:** Jika user input "Pesan 2 tiket Dune jam 7 malam", sistem V1 gagal karena node `Find_Movie` belum melempar data ke node `Find_Showtime`.
    *   **Dampak:** Sistem tidak mampu menangani *compound instructions* (instruksi majemuk).

3.  **State vs. Chat History Disconnect:**
    *   Sistem terlalu bergantung pada variable `state` terisolasi, mengabaikan nuansa di `chat_history`. Akibatnya, Agen terasa "pelupa" atau tidak nyambung jika user mengubah konteks sedikit saja.

---

## 2. Arsitektur V2: Limited ReAct Loop (The Flexible Approach/cara flexible)

### Perubahan Cara
Saya membuang pendekatan linear dan beralih ke **Single Manager Loop** dengan **Tool-Use Pattern**. Tidak ada lagi node `Find_Movie` atau `Select_Seat`. Hanya ada satu node cerdas (`Booking Manager`) yang memutuskan alat apa yang dipakai berdasarkan konteks dinamis.

### Key Engineering Decisions

#### A. Penghapusan Node Klasifikasi (Classifier-Free Guidance)
*   **Keputusan:** Menghapus node `classify_intent`.
*   **Alasan:** Niat user itu fluid. "Lihat jadwal" bisa berubah jadi "booking" dalam waktu yang dekat.
*   **Solusi:** Biarkan LLM menentukan intensi secara implisit lewat pemilihan *tools*. Jika user tanya jadwal, LLM panggil `get_showtimes`. Jika user langsung pilih kursi, LLM panggil `record_seats`. State dikelola secara organik/lebih natural, bukan dipaksa oleh Router.

#### B. Context Injection vs. Retrieval Tool
*   **Masalah:** Bagaimana cara LLM tahu film apa yang tayang?
*   **Opsi A (Tool):** LLM memanggil `search_movie(query="batman")`.
*   **Opsi B (Context):** Inject semua film yang sedang tayang ke dalam System Prompt.
*   **Opsi C (Tool):** RAG.
*   **Keputusan:** **Opsi B (Context Injection).**
*   **Rasional:**
    *   Jumlah film aktif di bioskop jarang melebihi 20-30 judul (bukan jumlah token yang signifikan).
    *   **Analogi Resepsionis:** Kasir bioskop tidak mengetik "Batman" di search bar setiap kali ada pelanggan. Mereka melihat daftar di layar mereka. Ini juga mempercepat respon (mengurangi 1 round-trip tool call jika menggunakan Opsi A maupun C).

#### C. Sequential Data Loading (Token Management)
*   **Tantangan:** Tidak mungkin meng-inject *seluruh* jadwal (Showtimes) untuk semua film ke dalam prompt (300+ kombinasi waktu).
*   **Solusi:** Penerapan filter bertahap (tapi tidak berlebihan sampai kaku)
    1.  Prompt awal hanya berisi **Daftar Film**.
    2.  Setelah Movie ID terpilih/terdeteksi -> Panggil Tool `get_showtimes(movie_id)`.
    3.  Hasil jadwal di-inject ke prompt putaran berikutnya.
    *   Ini meniru alur kerja nyata resepsionis/kasir bioskop: Pilih Film dulu, baru layar menampilkan Jam Tayang.

#### D. Separation of Concerns: "Read" vs "Write" Tools
*   **Masalah:** Di V1, mencari jadwal seringkali tidak sengaja "mengunci" film tersebut di state.
*   **Solusi:** Memisahkan tools menjadi dua jenis:
    1.  **Read Tools (Stateless):** `get_showtimes`, `get_available_seats`, `get_movie_details`. Tool ini hanya *mengambil* informasi untuk ditampilkan ke user. Tidak mengubah `booking_state`.
    2.  **Write Tools (Stateful):** `record_selected_movie`, `record_selected_seats`. Tool ini secara eksplisit dipanggil LLM hanya ketika user sudah *komit* dengan pilihannya, atau setidaknya sudah jelas memilih sehingga tetap bisa act untuk permintaan one shot (perintah lengkap).
*   **Hasil:** User bisa tanya-tanya jadwal 5 film berbeda tanpa merusak formulir pemesanan, karena `current_movie_id` hanya berubah jika `record_...` dipanggil.

#### E. Prompt Dinamis sebagai "State Monitor"
*   Alih-alih logika Python yang rumit ("Jika state A kosong, tanya B"), saya menggunakan **Dynamic System Prompt**.
*   Prompt secara *real-time* merefleksikan isi state:
    *   *"Formulir saat ini: Film=Terisi, Jadwal=Kosong -> FOKUS: Cari Jadwal."*
*   Ini memungkinkan LLM menangani perubahan mendadak (misal: user sudah pilih kursi, tiba-tiba bilang "eh ganti film deh"). LLM melihat state berubah, dan secara kognitif tahu harus mereset proses tanpa perlu kode `if-else` manual. Tapi tetap prompt ini secara dinamisnya ditentukan oleh state formilir actualnya dibelakang, contohnya dapat dilihat pada bagian [FOKUS INSTRUKSI] di prompt utama.

### Hasil Akhir
Sistem berubah dari "Formulir kaku berbasis Chatbot" menjadi "Agen Konsultan Bioskop" yang mampu menangani:
1.  **One-shot Prompting:** "Pesan 2 tiket posisi paling tengah dan baris paling dekat layar (aware denah), gundam jam 7 mlm besok (aware current time) atas nama rafi" (LLM langsung booking 2 slot sekaligus).
2.  **Non-Linear Flows:** User bisa loncat dari pilih jadwal kembali ke pilih film.
3.  **Ambiguity Handling:** Menggunakan penalaran LLM untuk mencocokkan "film yang robot-robotan itu" ke "Transformers", atau "betmen" ke "The Dark Knight", atau "kimi no nawa" ke "your name" (lewat Context Injection) tanpa search query manual.

### Kedepannya
1. Optimasi penggunaan token, dari sisi inject konteks, instruksi dan chat history
2. Penanganan async, dan jgua multi user (ubah cara penangannan state dan set up worker dll), lalu optimalkan cara connect ke db nya agar tidak perlu engine.connect() berkali-kali setiap tool calls.
3. Buat dataset dan metode evaluasi yang baik karena saat ini belum ada, baru hanya ditest dan coba manual langsung.
