# Tiketa AI Agent (V2) 🎬🍿

![Status](https://img.shields.io/badge/Status-Active-success) ![Architecture](https://img.shields.io/badge/Architecture-ReAct_Loop-blue) ![Python](https://img.shields.io/badge/Python-3.10+-yellow)

Agen pemesanan tiket bioskop berbasis LLM yang dirancang untuk menangani percakapan kompleks, perubahan konteks, dan instruksi *one-shot*.

> ⚠️ **PENTING BUAT DEV/RESEARCHER:**
> Project ini adalah **Versi 2 (Re-write)** dari eksperimen sebelumnya (*SixthExperiment*). Kami melakukan perubahan arsitektur total dari *Explicit State Machine* yang kaku menjadi *Limited ReAct Loop*.
>
> Baca alasan teknis, kegagalan V1, dan keputusan desain lengkap di:
> 👉 **[Catatan_Penting_Desain_Sistem.md](./Catatan_Penting_Desain_Sistem.md)** 👈
> *(Sangat direkomendasikan baca ini dulu sebelum diving ke code)*

---

## ✨ Fitur Utama (V2)

Berbeda dengan V1 yang sering *stuck* di logic *if-else*, V2 ini mampu:

* **One-Shot Booking:** *"Pesenin tiket Dune jam 7 malem buat 2 orang dong."* (Langsung diproses tanpa tanya satu-satu).
* **Contextual Awareness:** Paham *"yang jam 7 aja deh"* merujuk ke film yang sedang dibicarakan.
* **Fuzzy Matching:** *"Betmen"* -> *The Batman*, *"Kartun robot"* -> *Transformers*.
* **Non-Linear Flow:** Bisa loncat dari pilih kursi kembali ke lihat jadwal tanpa error state.

## 🛠️ Cara Install & Jalanin

```bash
# 1. Clone repo
git clone [https://github.com/username/project-tiketa-v2.git](https://github.com/username/project-tiketa-v2.git)

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup env
cp .env.example .env
# Isi API KEY kamu di .env

# 4. Run Agent
python main.py
