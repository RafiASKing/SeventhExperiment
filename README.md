# Tiketa LLM Agent (V2) 🎬🍿

![Status](https://img.shields.io/badge/Status-Active-success) ![Architecture](https://img.shields.io/badge/Architecture-LangGraph_Guarded_Loop-blueviolet)

**Tiketa V2** adalah agen pemesanan tiket bioskop cerdas yang dibangun di atas **LangGraph**. Menggunakan arsitektur *Guarded Looping Agent*, sistem ini menggabungkan fleksibilitas penalaran LLM dengan ketangguhan manajemen *state* untuk menangani transaksi kompleks secara natural.

> 🚨 **ARCHITECTURAL DEEP DIVE:**
> Repo ini adalah **Re-write total** dari [SixthExperiment](https://github.com/RafiASKing/SixthExperiment) (V1) yang gagal karena pendekatan *State Machine* yang terlalu kaku.
>
> Kami mendokumentasikan transisi dari "Heuristic Hell" ke "Flexible ReAct Loop", tantangan *engineering*, dan keputusan desain kritis di sini:
>
> 👉 **[BACA: Evolusi Arsitektur & Log Riset (V1 vs V2)](./Catatan_Penting_Desain_Sistem.md)** 👈
>
> *(Sangat disarankan membaca dokumen di atas untuk memahami konteks "Why & How" di balik kode ini)*

---

## 💡 Mengapa V2? (The Problem Solved)

Sistem V1 (SixthExperiment) terjebak dalam *linear logic* yang rapuh. V2 hadir dengan pendekatan **LangGraph Cyclic Flow** yang menawarkan:

* **🛡️ Robustness via Guardrails:** Meskipun menggunakan loop ReAct yang fleksibel, agen tetap dijaga oleh *Contextual Tool Definitions* dan *Dynamic System Prompts* agar tidak halusinasi.
* **🧠 One-Shot Inference:** User bisa langsung perintah: *"Pesenin tiket Dune jam 7 malem buat 2 orang, kursi tengah"* dan agen langsung mengisi formulir internal tanpa bertanya satu per satu.
* **🔄 Non-Linear Navigation:** User bisa melompat dari langkah konfirmasi kembali ke pemilihan jadwal tanpa merusak *state* aplikasi.
* **🧩 Fuzzy & Contextual Matching:** Menangani *"film yang ada robotnya"*, *"jam 7 aja"*, atau typo *"betmen"* menggunakan kognisi LLM, bukan RegEx.

## 🛠️ Cara Install & Jalanin

```bash
# 1. Clone repo (V2)
git clone [https://github.com/RafiASKing/SeventhExperiment.git](https://github.com/RafiASKing/SeventhExperiment.git)

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup env
cp .env.example .env
# Masukkan API KEY (OpenAI/Groq/dll)

# 4. Run Agent
python main.py
