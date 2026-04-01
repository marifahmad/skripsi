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
- **Embedding:** `text-embedding-3-large`

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

## ⚙️ Panduan Instalasi & Persiapan Lingkungan

### 1. Kloning Repositori
```bash
git clone https://github.com/marifahmad/skripsi.git
cd skripsi
