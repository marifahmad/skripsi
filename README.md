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

- **Standard RAG** (Vector Database saja)
- **Hybrid RAG** (Vector + Knowledge Graph)

---

## 🏛️ Arsitektur Sistem

Sistem ini menjalankan dua pipeline secara paralel:

### 1. Standard RAG (Vector-Only)

- **Penyimpanan:** ChromaDB  
- **Pencarian:** Semantic Search (MMR)  
- Embedding: `text-embedding-3-large`

---

### 2. Hybrid RAG (Vector + Graph)

- **Vector Search (Mikro):** ChromaDB  
- **Graph Search (Makro):** Neo4j (Cypher Query)  
- **Sintesis:** LLM `gpt-4o-mini`

---

## 🌟 Fitur Aplikasi (Streamlit)

### 💬 Tab 1: Perbandingan & Evaluasi Pakar
- Perbandingan jawaban RAG vs Hybrid
- Menampilkan konteks sumber
- Form evaluasi pakar → `hasil_evaluasi_human.csv`

---

### 📊 Tab 2: Evaluasi Otomatis
Menggunakan Cosine Similarity:

- **Faithfulness**
- **Answer Relevance**
- **Context Precision**

---

### 🕸️ Tab 3: Knowledge Graph Explorer
- Visualisasi Neo4j (PyVis + NetworkX)
- Filter node (Argumen, Konsep, Tokoh, dll)


---

### ⚙️ Panduan Instalasi & Persiapan Lingkungan
1. Kloning Repositori
  git clone https://github.com/marifahmad/skripsi.git
  cd skripsi
2. Buat & Aktifkan Virtual Environment
  Sangat disarankan untuk mengisolasi dependensi proyek agar tidak bentrok dengan proyek Python lainnya.
  
  Windows:
  python -m venv venv
  venv\Scripts\activate

3. Buat File requirements.txt & Instal Library
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

Kemudian, instal seluruh dependensi dengan perintah:
pip install -r requirements.txt

4. Konfigurasi Environment (.env)

   Buat sebuah file bernama .env di direktori utama proyek. File ini mengatur koneksi ke OpenAI dan Database. Isi dengan kredensial Anda yang sah:
   ```text
  # Kredensial OpenAI (Untuk LLM & Embeddings)
  OPENAI_API_KEY=sk-kunci-rahasia-openai-anda
  
  # Path ke direktori ChromaDB lokal
  CHROMA_PATH=./chroma_db_tahafut
  
  # Kredensial Database Neo4j (Sesuaikan dengan AuraDB atau Desktop)
  NEO4J_URI=bolt://localhost:7687
  NEO4J_USERNAME=neo4j
  NEO4J_PASSWORD=password-neo4j-anda

5. Persiapan Database

   ChromaDB: Pastikan folder chroma_db_tahafut sudah berada di direktori proyek dan berisi data vektor dari kitab Tahafut al-Falasifah.
   Neo4j: Pastikan server Neo4j Anda sedang berjalan dan graf pengetahuan (node & relasi) sudah dibuat/di-ingest ke dalam database tersebut.
  
  6. 🚀 Menjalankan Aplikasi
     streamlit run app.py
     
Terminal akan menampilkan Network URL. Buka browser web Anda dan akses:
👉 http://localhost:8501
    
   
---

## 📂 Struktur Repositori

```text
📁 root_directory/
│
├── 📄 app.py
├── 📄 requirements.txt
├── 📄 .env
├── 📄 hasil_evaluasi_human.csv
│
├── 📁 venv/
└── 📁 chroma_db_tahafut/


