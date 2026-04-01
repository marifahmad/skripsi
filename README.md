# 🎓 Sistem Skripsi: Tanya Jawab Filsafat Islam (Hybrid RAG)

![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)  
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B)  
![Neo4j](https://img.shields.io/badge/Neo4j-Graph_Database-008CC1)  
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Database-FD4659)  
![OpenAI](https://img.shields.io/badge/OpenAI-GPT_4o_mini-412991)

---

Repositori ini berisi implementasi kode sumber untuk aplikasi web **Sistem Tanya Jawab berbasis Hybrid Retrieval-Augmented Generation (Hybrid RAG)**.

Penelitian skripsi ini berfokus pada ekstraksi informasi dan pemahaman teks klasik filsafat Islam, dengan studi kasus spesifik pada kitab **Tahāfut al-Falāsifah** karya Imam Al-Ghazali.

Tujuan utama sistem ini adalah untuk menguji, mengevaluasi, dan membandingkan performa arsitektur:
- **Standard RAG** (Hanya menggunakan Vector Database)
- **Hybrid RAG** (Kombinasi Vector Database + Knowledge Graph)

---

## 🏛️ Arsitektur Sistem

Sistem ini menjalankan dua *pipeline* secara paralel untuk tujuan perbandingan (A/B Testing):

### 1. Standard RAG (Vector-Only)
- **Penyimpanan:** ChromaDB  
- **Pencarian:** Semantic Search (Max Marginal Relevance)  
- **Embedding:** `text-embedding-3-large`

### 2. Hybrid RAG (Vector + Graph)
- **Vector Search (Mikro):** ChromaDB  
- **Graph Search (Makro):** Neo4j (Cypher Query) untuk mengekstrak relasi entitas.  
- **Sintesis:** LLM `gpt-4o-mini`

---

## 🌟 Fitur Aplikasi (Streamlit)

### 💬 Tab 1: Perbandingan & Evaluasi Pakar
- Perbandingan jawaban Standard RAG vs Hybrid RAG secara berdampingan.
- Menampilkan *raw context* (sitasi) yang menjadi acuan LLM.
- **Form Evaluasi Pakar:** Fitur bagi domain expert untuk menilai kualitas jawaban, yang langsung disimpan ke dalam file `hasil_evaluasi_human.csv`.

### 📊 Tab 2: Evaluasi Otomatis
Kalkulasi performa secara *real-time* menggunakan *Cosine Similarity*:
- **Faithfulness:** Keakuratan jawaban berdasarkan konteks.
- **Answer Relevance:** Relevansi jawaban dengan pertanyaan.
- **Context Precision:** Presisi konteks yang ditarik dari database.

### 🕸️ Tab 3: Knowledge Graph Explorer
- Visualisasi interaktif graf pengetahuan Neo4j menggunakan PyVis + NetworkX.
- Filter node dinamis (Argumen, Konsep, Tokoh, Masalah).

---

## 📂 Struktur Repositori

```text
📁 root_directory/
│
├── 📄 app.py                     # Skrip utama UI Streamlit & logika sistem RAG
├── 📄 requirements.txt           # Daftar dependensi pustaka Python
├── 📄 .env                       # File konfigurasi rahasia (API Keys & DB URI)
├── 📄 hasil_evaluasi_human.csv   # Log output dari evaluasi pakar
│
├── 📁 venv/                      # Lingkungan virtual Python (Virtual Environment)
└── 📁 chroma_db_tahafut/         # Direktori penyimpanan database vektor lokal
```

---

## ⚙️ Panduan Instalasi & Persiapan Lingkungan

Ikuti langkah-langkah di bawah ini untuk menjalankan sistem di komputer lokal Anda:

### 1. Kloning Repositori
```bash
git clone https://github.com/marifahmad/skripsi.git
cd skripsi
```

### 2. Buat & Aktifkan Virtual Environment
Sangat disarankan untuk mengisolasi dependensi proyek agar tidak bentrok dengan proyek Python lainnya.

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalasi Library (Requirements)
Buat file `requirements.txt` (jika belum ada) dan isi dengan daftar berikut:
```text
streamlit
numpy
pandas
networkx
pyvis
python-dotenv
langchain
langchain-openai
langchain-community
chromadb
neo4j
scikit-learn
```

Lalu, instal seluruh dependensi dengan perintah:
```bash
pip install -r requirements.txt
```

### 4. Konfigurasi Environment (`.env`)
Buat sebuah file bernama `.env` di direktori utama proyek. File ini mengatur koneksi ke OpenAI dan Database. Isi dengan kredensial Anda:
```env
# Kredensial OpenAI (Untuk LLM & Embeddings)
OPENAI_API_KEY=sk-kunci-rahasia-openai-anda

# Path ke direktori ChromaDB lokal
CHROMA_PATH=./chroma_db_tahafut

# Kredensial Database Neo4j (Sesuaikan dengan AuraDB atau Desktop)
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password-neo4j-anda
```

### 5. Persiapan Database
- **ChromaDB:** Pastikan folder `chroma_db_tahafut` sudah berada di direktori proyek dan berisi data vektor dari kitab Tahafut al-Falasifah.
- **Neo4j:** Pastikan server Neo4j Anda sedang berjalan dan graf pengetahuan (node & relasi) sudah dibuat/di-ingest ke dalam database tersebut.

---

## 🚀 Menjalankan Aplikasi

Setelah semua persiapan selesai, jalankan aplikasi Streamlit dengan perintah berikut di terminal:
```bash
streamlit run app.py
```

Terminal akan menampilkan *Network URL*. Buka browser web Anda dan akses:  
👉 **http://localhost:8501**
