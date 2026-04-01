# import streamlit as st
# import streamlit.components.v1 as components
# import numpy as np
# import pandas as pd
# import re
# import os
# import networkx as nx
# import textwrap
# from pyvis.network import Network
# from dotenv import load_dotenv

# # Langchain & Neo4j Imports
# from langchain_openai import OpenAIEmbeddings, ChatOpenAI
# from langchain_community.vectorstores import Chroma
# from neo4j import GraphDatabase
# from sklearn.metrics.pairwise import cosine_similarity

# # =========================================================
# # 1. KONFIGURASI HALAMAN
# # =========================================================
# st.set_page_config(
#     page_title="Sistem Skripsi Hybrid RAG",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # Load environment variables
# load_dotenv()

# # =========================================================
# # 2. DEFINISI WARNA (GLOBAL)
# # =========================================================
# COLOR_MAP = {
#     "Argumen": "#f375d6",
#     "Konsep":  "#c5b568",
#     "Masalah": "#ffad7a",
#     "Tokoh":   "#b6ecd9",
#     "Default": "#94A3B8"
# }   

# # =========================================================
# # 3. INISIALISASI RESOURCE (CACHED)
# # =========================================================
# def save_human_evaluation(data):
#     """Menyimpan hasil evaluasi manusia ke file CSV secara permanen."""
#     file_name = "hasil_evaluasi_human.csv"
#     df_new = pd.DataFrame([data])
    
#     if not os.path.isfile(file_name):
#         df_new.to_csv(file_name, index=False)
#     else:
#         df_new.to_csv(file_name, mode='a', header=False, index=False)

# @st.cache_resource
# def init_resources():
#     """
#     Menginisialisasi koneksi DB & Model sekali saja.
#     """
#     # A. Embeddings
#     embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    
#     # B. Vector DB
#     vectordb = Chroma(
#         persist_directory=os.getenv("CHROMA_PATH"),
#         embedding_function=embeddings
#     )
    
#     # C. LLM
#     llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
#     # D. Neo4j Driver
#     driver = GraphDatabase.driver(
#         os.getenv("NEO4J_URI"),
#         auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
#     )
    
#     return embeddings, vectordb, llm, driver

# try:
#     embeddings, vectordb, llm, driver = init_resources()
# except Exception as e:
#     st.error(f"⚠️ Gagal terhubung ke Database: {e}")
#     st.stop()

# # =========================================================
# # 4. HELPER: TOOLTIP TEXT-ONLY (STABIL & RAPI)
# # =========================================================
# def format_node_tooltip(node):
#     """
#     Menggunakan format text biasa dengan baris baru (\n) 
#     agar DIJAMIN AMAN dari error rendering HTML.
#     """
#     labels = list(node.labels)
#     node_type = labels[0] if labels else "INFO"
    
#     tooltip_text = f"[{node_type.upper()}]\n"
#     tooltip_text += "=" * 25 + "\n"
    
#     blacklisted_keys = ["embedding", "vector", "element_id", "id", "label"]
#     sorted_keys = sorted(node.keys())
    
#     for key in sorted_keys:
#         if key in blacklisted_keys:
#             continue
            
#         val = node[key]
#         val_str = str(val)
        
#         if len(val_str) > 50:
#             wrapped_lines = textwrap.wrap(val_str, width=50)
#             if len(wrapped_lines) > 5:
#                 val_str = "\n".join(wrapped_lines[:5]) + "\n... (baca selengkapnya)"
#             else:
#                 val_str = "\n".join(wrapped_lines)
        
#         pretty_key = key.replace("_", " ").title()
#         tooltip_text += f"{pretty_key} :\n{val_str}\n"
#         tooltip_text += "-" * 15 + "\n" 
        
#     return tooltip_text

# # =========================================================
# # 5. LOGIC: GRAPH VISUALIZATION (PYVIS + FILTER)
# # =========================================================
# def get_pyvis_html(limit=40, selected_types=None):
#     G = nx.Graph()
    
#     if not selected_types:
#         query = f"""
#         MATCH (a)-[r]->(b) 
#         RETURN a, type(r) AS rel, b 
#         ORDER BY rand() LIMIT {limit}
#         """
#         params = {}
#     else:
#         query = f"""
#         MATCH (a)-[r]->(b) 
#         WHERE any(label IN labels(a) WHERE label IN $types) 
#            OR any(label IN labels(b) WHERE label IN $types)
#         RETURN a, type(r) AS rel, b 
#         ORDER BY rand() LIMIT {limit}
#         """
#         params = {"types": selected_types}

#     with driver.session() as session:
#         result = list(session.run(query, **params))
        
#         if not result:
#             return "<div style='padding:20px; color:red; font-family:sans-serif;'>Tidak ada data graph untuk kategori ini. Coba pilih kategori lain atau naikkan limit.</div>"

#         for rec in result:
#             a = rec["a"]
#             b = rec["b"]
#             rel = rec["rel"]
            
#             la = list(a.labels)[0] if a.labels else "Default"
#             tooltip_a = format_node_tooltip(a)
#             color_a = COLOR_MAP.get(la, COLOR_MAP["Default"])
            
#             lb = list(b.labels)[0] if b.labels else "Default"
#             tooltip_b = format_node_tooltip(b)
#             color_b = COLOR_MAP.get(lb, COLOR_MAP["Default"])
            
#             G.add_node(a.element_id, label=a.get("nama", la), title=tooltip_a, color=color_a)
#             G.add_node(b.element_id, label=b.get("nama", lb), title=tooltip_b, color=color_b)
#             G.add_edge(a.element_id, b.element_id, title=rel, label=rel, color="#CBD5E1")

#     net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="black")
#     net.from_nx(G)
    
#     net.set_options("""
#     var options = {
#       "nodes": {
#         "font": { "size": 16, "strokeWidth": 2, "color": "white" }, 
#         "borderWidth": 2,
#         "shadow": { "enabled": true }
#       },
#       "edges": {
#         "color": { "inherit": false }, 
#         "smooth": false,
#         "font": { "size": 10, "align": "middle" },
#         "arrows": { "to": { "enabled": true, "scaleFactor": 0.5 } }
#       },
#       "physics": {
#         "forceAtlas2Based": {
#           "gravitationalConstant": -50,
#           "springLength": 100
#         },
#         "solver": "forceAtlas2Based",
#         "stabilization": { "enabled": true }
#       },
#       "interaction": {
#         "hover": true, 
#         "tooltipDelay": 50
#       }
#     }
#     """)
    
#     try:
#         path = "tmp_graph.html"
#         net.save_graph(path)
#         with open(path, 'r', encoding='utf-8') as f:
#             return f.read()
#     except Exception as e:
#         return f"<div>Error generating graph: {e}</div>"

# # =========================================================
# # 6. HELPER: LEGENDA WARNA
# # =========================================================
# def render_legend():
#     html_content = '<div style="display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; font-family: sans-serif;">'
#     for label, color in COLOR_MAP.items():
#         if label == "Default": continue
#         html_content += f'<div style="display: flex; align-items: center; background-color: {color}; color: white; padding: 5px 12px; border-radius: 20px; font-size: 13px; font-weight: bold; box-shadow: 0 2px 4px rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.3);"><span style="margin-right: 6px; font-size: 16px;">●</span> {label}</div>'
#     html_content += '</div>'
#     st.markdown(html_content, unsafe_allow_html=True)

# # =========================================================
# # 7. LOGIC: RAG & METRICS
# # =========================================================
# def calculate_metrics(query, answer, context):
#     if not answer or not context:
#         return 0.0, 0.0, 0.0

#     try:
#         v_q = np.array(embeddings.embed_query(query)).reshape(1, -1)
#         v_a = np.array(embeddings.embed_query(answer)).reshape(1, -1)
        
#         relevance = cosine_similarity(v_q, v_a)[0][0]

#         context_blocks = [c.strip() for c in context.split("\n\n") if len(c.strip()) > 50]
#         if not context_blocks:
#             context_blocks = [context]
            
#         v_c_list = np.array(embeddings.embed_documents(context_blocks))
        
#         faithfulness_scores = cosine_similarity(v_a, v_c_list)
#         faithfulness = np.max(faithfulness_scores) 

#         precision_scores = cosine_similarity(v_q, v_c_list)
#         precision = np.mean(precision_scores) 
        
#         if "tidak ditemukan" in answer.lower() or "maaf" in answer.lower():
#             faithfulness = 0.0
#             relevance = 0.0

#         return round(faithfulness, 3), round(relevance, 3), round(precision, 3)
#     except Exception as e:
#         print(f"Error perhitungan metrik: {e}")
#         return 0.0, 0.0, 0.0

# def standard_rag(query):
#     docs = vectordb.max_marginal_relevance_search(query, k=4, fetch_k=10)
    
#     context_parts = []
#     for i, d in enumerate(docs):
#         meta = (
#             f"[{i+1}]\n"
#             f"Masalah       : {d.metadata.get('masalah', '-')}\n"
#             f"Judul Masalah : {d.metadata.get('judul_masalah', '-')}\n"
#             f"Topik         : {d.metadata.get('topik', '-')}\n"
#             f"Label         : {d.metadata.get('label', '-')}\n"
#             f"Tokoh         : {d.metadata.get('tokoh', '-')}\n"
#             f"Sumber        : {d.metadata.get('sumber', '-')}\n"
#             f"Page          : {d.metadata.get('page', '-')}\n"
#             f"Chunk ID      : {d.metadata.get('chunk_id', '-')}\n"
#         )
#         context_parts.append(meta + f"Teks          :\n{d.page_content}")
        
#     ctx = "\n\n".join(context_parts)
    
#     prompt = f"""
#     Anda adalah asisten akademik filsafat Islam.

#     Gunakan konteks berikut untuk menjawab pertanyaan secara ilmiah,
#     sistematis, dan berbasis teks Tahafut al-Falasifah.

#     Struktur jawaban WAJIB sebagai berikut:
#     1. Penjelasan Konsep
#     2. Argumen Filsuf
#     3. Bantahan Al-Ghazali
#     4. Referensi (Masalah & Halaman PDF)

#     Jika informasi untuk menjawab tidak ditemukan di dalam konteks,
#     tuliskan "Tidak ditemukan dalam Tahafut al-Falasifah". JANGAN mengarang jawaban.

#     Konteks:
#     {ctx}

#     Pertanyaan:
#     {query}

#     Jawaban:
#     """
#     ans = llm.invoke(prompt).content
#     return ans, ctx

# def hybrid_rag_final(query):
#     vektor_docs = vectordb.max_marginal_relevance_search(query, k=4, fetch_k=10)

#     ext_prompt = f"""Ekstrak maksimal 3 kata kunci utama (nama tokoh atau konsep filosofis) dari pertanyaan berikut. 
#     Kembalikan HANYA kata kuncinya, pisahkan dengan koma. JANGAN beri penjelasan.
#     Pertanyaan: {query}"""
    
#     raw_kws = llm.invoke(ext_prompt).content.strip()
#     keyword_list = [k.strip() for k in raw_kws.split(',') if k.strip()]
    
#     graph_docs = []
#     with driver.session() as session:
#         cypher_query = """
#         UNWIND $kws AS kw
#         MATCH (t:Topik)-[:BAGIAN_DARI_TOPIK]-(m:Masalah)-[:BAGIAN_DARI_TEKS]-(c:Chunk)
#         WHERE toLower(t.nama) CONTAINS toLower(kw)
#            OR toLower(m.id) CONTAINS toLower(kw)
#            OR toLower(m.judul) CONTAINS toLower(kw)
#         RETURN DISTINCT
#             m.id AS masalah_id,
#             m.judul AS judul,
#             t.nama AS topik,
#             c.text AS teks,
#             c.page AS halaman,
#             c.label AS label,
#             c.tokoh AS tokoh
#         ORDER BY masalah_id ASC, halaman ASC
#         LIMIT 10
#         """
#         result = session.run(cypher_query, kws=keyword_list)
#         graph_docs = [dict(record) for record in result]

#     if not graph_docs:
#         with driver.session() as session:
#             fallback_query = """
#             MATCH (t:Topik)-[:BAGIAN_DARI_TOPIK]-(m:Masalah)-[:BAGIAN_DARI_TEKS]-(c:Chunk)
#             WHERE toLower(t.nama) CONTAINS toLower($search)
#                OR toLower(m.id) CONTAINS toLower($search)
#                OR toLower(m.judul) CONTAINS toLower($search)
#             RETURN 
#                 m.id AS masalah_id, m.judul AS judul, t.nama AS topik, 
#                 c.text AS teks, c.page AS halaman, c.label AS label, c.tokoh AS tokoh
#             ORDER BY masalah_id ASC, halaman ASC
#             LIMIT 10
#             """
#             result = session.run(fallback_query, search=query)
#             graph_docs = [dict(record) for record in result]
            
#     context_parts = []
#     for i, d in enumerate(vektor_docs):
#         meta = (
#             f"[KONTEKS VEKTOR {i+1}]\n"
#             f"Masalah       : {d.metadata.get('masalah', '-')}\n"
#             f"Judul Masalah : {d.metadata.get('judul_masalah', '-')}\n"
#             f"Topik         : {d.metadata.get('topik', '-')}\n"
#             f"Label         : {d.metadata.get('label', '-')}\n"
#             f"Tokoh         : {d.metadata.get('tokoh', '-')}\n"
#             f"Halaman       : {d.metadata.get('page', '-')}\n"
#         )
#         context_parts.append(meta + f"Teks          : {d.page_content}")

#     for i, g in enumerate(graph_docs):
#         meta = (
#             f"[KONTEKS GRAPH {i+1}]\n"
#             f"ID Masalah    : {g['masalah_id']}\n"
#             f"Judul Masalah : {g['judul']}\n"
#             f"Topik         : {g['topik']}\n"
#             f"Label         : {g['label']}\n"
#             f"Halaman       : {g['halaman']}\n"
#         )
#         context_parts.append(meta + f"Teks          : {g['teks']}")

#     full_ctx = "\n\n".join(context_parts)
#     if not full_ctx.strip():
#         full_ctx = "Tidak ada data relevan yang ditemukan dalam database."

#     prompt = f"""
#     Anda adalah asisten akademik filsafat Islam yang pakar dalam kitab "Tahafut al-Falasifah" karya Imam Al-Ghazali.

#     Tugas Anda adalah menjawab pertanyaan berdasarkan dua sumber konteks:
#     1. KONTEKS VEKTOR: Berisi potongan teks detail (mikro).
#     2. KONTEKS GRAPH: Berisi struktur masalah dan daftar topik terkait (makro).

#     STRUKTUR JAWABAN (WAJIB):
#     1. Penjelasan Konsep: Terangkan definisi atau latar belakang masalah.
#     2. Argumen Filsuf: Jelaskan posisi filsuf (Aristoteles/Ibnu Sina/Al-Farabi) berdasarkan teks.
#     3. Bantahan Al-Ghazali: Jelaskan secara sistematis bagaimana Al-Ghazali meruntuhkan argumen tersebut.
#     4. Referensi Akademik: WAJIB sebutkan "ID Masalah" (Contoh: MASALAH PERTAMA) dan "Halaman PDF" untuk setiap poin penting.

#     ATURAN KETAT:
#     - Jika informasi TIDAK ADA dalam konteks, jawablah: "Maaf, informasi tersebut tidak ditemukan dalam database kitab Tahafut al-Falasifah."
#     - DILARANG menggunakan pengetahuan umum Anda sendiri di luar isi kitab.
#     - Sertakan sitasi secara konsisten.

#     === KONTEKS ===
#     {full_ctx}

#     Pertanyaan: {query}
#     Jawaban:
#     """
#     ans = llm.invoke(prompt).content
#     return ans, full_ctx

# # =========================================================
# # 8. UI UTAMA (STREAMLIT)
# # =========================================================
# st.title("🎓 Sistem Tanya Jawab Filsafat Islam Hybrid RAG")
# st.markdown("---")

# # --- SIDEBAR ---
# with st.sidebar:
#     st.header("⚙️ Input Pertanyaan")
#     query_input = st.text_area("Pertanyaan:", height=150, placeholder="Contoh: Apa pendapat Al-Ghazali tentang kausalitas?")
    
#     process_btn = st.button("🚀 PROSES ANALISIS", type="primary")
#     st.info("Sistem ini membandingkan Standard RAG vs Hybrid RAG (Neo4j).")

# # --- MAIN TABS ---
# tab1, tab2, tab3, tab4 = st.tabs([
#     "💬 Perbandingan", 
#     "📊 Metriks Evaluasi", 
#     "🕸️ Knowledge Graph Explorer",
#     "📈 Evaluasi Massal (Skripsi)"
# ])

# # Logic Process (Single Query)
# if process_btn and query_input:
#     with st.spinner("Sedang memproses (Standard vs Hybrid)..."):
#         std_ans, std_ctx = standard_rag(query_input)
#         m_std = calculate_metrics(query_input, std_ans, std_ctx)
        
#         hyb_ans, hyb_ctx = hybrid_rag_final(query_input)
#         m_hyb = calculate_metrics(query_input, hyb_ans, hyb_ctx)
        
#         st.session_state['results'] = {
#             'std': (std_ans, std_ctx, m_std),
#             'hyb': (hyb_ans, hyb_ctx, m_hyb),
#             'query': query_input
#         }

# if 'results' in st.session_state:
#     res = st.session_state['results']
    
#     # --- TAB 1: HASIL ---
#     with tab1:
#         col1, col2 = st.columns(2)
#         with col1:
#             st.subheader("Standard RAG")
#             st.info(res['std'][0])
#             with st.expander("Lihat Konteks"):
#                 st.text(res['std'][1])
#         with col2:
#             st.subheader("Hybrid RAG")
#             st.success(res['hyb'][0])
#             with st.expander("Lihat Konteks"):
#                 st.text(res['hyb'][1])

#         st.markdown("---")
#         st.subheader("📝 Evaluasi Ahli (Human)")
        
#         with st.form("human_eval_form"):
#             st.write("Berikan penilaian komparatif Anda terhadap kedua jawaban sistem:")
#             col_eval_std, col_eval_hyb = st.columns(2)
            
#             with col_eval_std:
#                 st.markdown("**Penilaian Standard RAG**")
#                 score_std = st.select_slider("Skor Kualitas (Standard):", options=[1, 2, 3, 4], value=3, key="score_std")
#                 is_accurate_std = st.checkbox("Data Sesuai Kitab (Standard)", key="acc_std")
#                 is_natural_std = st.checkbox("Bahasa Natural/Akademik (Standard)", key="nat_std")

#             with col_eval_hyb:
#                 st.markdown("**Penilaian Hybrid RAG**")
#                 score_hyb = st.select_slider("Skor Kualitas (Hybrid):", options=[1, 2, 3, 4], value=3, key="score_hyb")
#                 is_accurate_hyb = st.checkbox("Data Sesuai Kitab (Hybrid)", key="acc_hyb")
#                 is_natural_hyb = st.checkbox("Bahasa Natural/Akademik (Hybrid)", key="nat_hyb")
            
#             st.markdown("---")
#             feedback = st.text_area("Catatan/Kritik Ahli (Perbandingan):", placeholder="Contoh: Hybrid RAG lebih komprehensif menjelaskan argumen Al-Ghazali...")
#             submit_eval = st.form_submit_button("Simpan Evaluasi Komparatif")
            
#             if submit_eval:
#                 m_faith_s, m_relev_s, m_prec_s = res['std'][2]
#                 m_faith_h, m_relev_h, m_prec_h = res['hyb'][2]

#                 eval_data = {
#                     "Tanggal": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
#                     "Pertanyaan": res['query'],
#                     "Jawaban_Standard": res['std'][0],
#                     "Skor_Human_Std": score_std,
#                     "Cek_Akurasi_Std": 1 if is_accurate_std else 0,
#                     "Cek_Bahasa_Std": 1 if is_natural_std else 0,
#                     "Faith_AI_Std": m_faith_s,
#                     "Relev_AI_Std": m_relev_s,
#                     "Prec_AI_Std": m_prec_s,
#                     "Jawaban_Hybrid": res['hyb'][0],
#                     "Skor_Human_Hyb": score_hyb,
#                     "Cek_Akurasi_Hyb": 1 if is_accurate_hyb else 0,
#                     "Cek_Bahasa_Hyb": 1 if is_natural_hyb else 0,
#                     "Faith_AI_Hyb": m_faith_h,
#                     "Relev_AI_Hyb": m_relev_h,
#                     "Prec_AI_Hyb": m_prec_h,
#                     "Komentar_Ahli": feedback
#                 }
                
#                 save_human_evaluation(eval_data)
#                 st.success("✅ Data perbandingan berhasil dicatat ke CSV!")
#                 st.balloons()

#     # --- TAB 2: METRIKS ---
#     with tab2:
#         m_faith_s, m_relev_s, m_prec_s = res['std'][2]
#         m_faith_h, m_relev_h, m_prec_h = res['hyb'][2]
        
#         df = pd.DataFrame({
#             "Metrik": ["Faithfulness", "Relevance", "Precision"],
#             "Standard RAG": [m_faith_s, m_relev_s, m_prec_s],
#             "Hybrid RAG": [m_faith_h, m_relev_h, m_prec_h]
#         })
        
#         st.dataframe(df, use_container_width=True)
#         st.bar_chart(df.set_index("Metrik"), color=["#2563EB", "#16A34A"])
        
#         st.markdown("---")
#         st.subheader("📋 Log Evaluasi Manusia (Data Skripsi)")
        
#         if os.path.isfile("hasil_evaluasi_human.csv"):
#             df_human = pd.read_csv("hasil_evaluasi_human.csv")
#             st.dataframe(df_human, use_container_width=True)
            
#             csv_data = df_human.to_csv(index=False).encode('utf-8')
#             st.download_button(
#                 label="📥 Download Hasil Evaluasi (.CSV)",
#                 data=csv_data,
#                 file_name="evaluasi_skripsi_hybrid_rag.csv",
#                 mime="text/csv"
#             )
#         else:
#             st.info("Belum ada data evaluasi manusia yang disimpan.")

# # --- TAB 3: GRAPH EXPLORER ---
# with tab3:
#     st.subheader("Visualisasi Graph Neo4j")
    
#     col_f1, col_f2, col_f3 = st.columns([2, 1, 1])
#     with col_f1:
#         filter_options = ["Argumen", "Konsep", "Masalah", "Tokoh"]
#         selected_nodes = st.multiselect("Filter Tipe Node (Kosongkan = Tampilkan Semua):", options=filter_options, default=filter_options)
#     with col_f2:
#         limit_nodes = st.number_input("Limit Node:", min_value=10, max_value=200, value=50)
#     with col_f3:
#         st.write("") 
#         st.write("") 
#         refresh = st.button("🔄 Refresh Graph", use_container_width=True)

#     st.caption("Keterangan Warna Node:")
#     render_legend()
    
#     graph_state_key = f"graph_{selected_nodes}_{limit_nodes}"
    
#     if refresh or graph_state_key not in st.session_state:
#         with st.spinner("Mengambil data graph..."):
#             filters = selected_nodes if selected_nodes else None
#             st.session_state[graph_state_key] = get_pyvis_html(limit_nodes, filters)
#             st.session_state['active_key'] = graph_state_key
            
#     active_key = st.session_state.get('active_key', graph_state_key)
#     if active_key in st.session_state:
#         components.html(st.session_state[active_key], height=650)

# # --- TAB 4: BULK EVALUATION (SKRIPSI) ---
# with tab4:
#     st.subheader("📈 Evaluasi Otomatis (30 Pertanyaan Skripsi)")
#     st.info("Fitur ini akan menjalankan Standard RAG dan Hybrid RAG untuk seluruh pertanyaan, menghitung metrik, dan mencari rata-ratanya. Proses ini mungkin memakan waktu beberapa menit karena memanggil LLM berulang kali.")
    
#     DAFTAR_PERTANYAAN_SKRIPSI = [
#         "Mengapa para filsuf menyatakan bahwa sesuatu yang berawal, mustahil lahir dari yang kekal secara mutlak?",
#         "Secara umum, jika kondisi zat yang kekal tetap serupa dan tidak berubah, maka terdapat dua hal yang bisa terjadi. Sebutkan!",
#         "Dari mana alam itu berawal?",
#         "Apa yang dimaksud dengan tajaddud?",
#         "Apa yang di maksud dengan murad?",
#         "Apa yang di maksud dengan iradah?",
#         "Bagaimana pendapat al-ghazali mengenai awal mulanya alam diciptakan?",
#         "Bagaimana para filsuf berasumsi bahwa orang yang mengatakan alam adalah lebih akhir dari allah?",
#         "Bagaimana bantahan al-ghazali mengenai alam adalah mengatakan alam adalah lebih akhir dari allah?",
#         "Apa yang dimaksud dengan keterdahuluan Tuhan?",
#         "Apa yang dimaksud dengan kata kana (telah ada) dan yakunu (akan ada) dalam zat?",
#         "Jelaskan alam itu tidak mempunyai atas dan bawah!",
#         "Jelaskan apa yang di katakan oleh para filsuf bahwa tak diragukan lagi bahwa allah adalah zat yang kuasa!",
#         "Bagaimana pendapat al-ghazali mengenai allah itu adalah zat yang kuasa?",
#         "Mengapa para filsuf berpegang teguh dengan pandangan bahwa eksistensi alam kemungkinan sebelum ia benar benar ada?",
#         "Bagaimana pandangan al-ghazali mengenai eksistensi alam?",
#         "Jelaskan setiap temporal pasti didahului oleh materi sebagai tempat yang mendahuluinya!",
#         "Apa saja kemungkinan yang di bahas menurut pandangan filsuf?",
#         "Apa yang dimaksud dengan jiwa adalah kekal?",
#         "Apa saja ketidakmungkinan yang terjadi menurut pandangan al-ghazali?",
#         "Mengapa para filsuf mengatakan alam adalah azali?",
#         "Argumen pertama adalah yang di pegang oleh galen dia mengatakan apabila matahari dapat lenyap, tanda tanda kerusakan mesti melalui penyusutan. tetapi pengamatan astronomis mengenai ukurannya selama beribu-ribu tahun hanya menunjukkan kuantitas seperti adanya(tanpa ada gejala penyusutan), jadi bagaimana pendapat al-ghazali?",
#         "Apa yang dimaksud dengan silogisme konjungtif-hipotesis?",
#         "Apa pendapat muktaziah mengenai pemecahan masalah kemustahilan?",
#         "Siapa saja ahli kalam yang berusaha memecahkan masalah kemustahilan?",
#         "Apa yang di maksud dengan seorang pelaku fail?",
#         "Bagaimana pendapat para filsuf mengenai allah adalah pencipta?",
#         "Apa sanggahan al-ghazali mengenai allah adalah pencipta?",
#         "Apa yang dimaksud dengan qadim?",
#         "Apa yang dimaksud dengan akal?"
#     ]

#     if st.button("🚀 Mulai Evaluasi Massal", type="primary", use_container_width=True):
#         progress_bar = st.progress(0)
#         status_text = st.empty()
        
#         hasil_evaluasi_massal = []
#         total_q = len(DAFTAR_PERTANYAAN_SKRIPSI)
        
#         for i, q in enumerate(DAFTAR_PERTANYAAN_SKRIPSI):
#             status_text.text(f"Memproses Pertanyaan {i+1} dari {total_q}: {q[:50]}...")
            
#             std_ans, std_ctx = standard_rag(q)
#             f_std, r_std, p_std = calculate_metrics(q, std_ans, std_ctx)
            
#             hyb_ans, hyb_ctx = hybrid_rag_final(q)
#             f_hyb, r_hyb, p_hyb = calculate_metrics(q, hyb_ans, hyb_ctx)
            
#             hasil_evaluasi_massal.append({
#                 "No": i + 1,
#                 "Pertanyaan": q,
#                 "Std_Faithfulness": f_std,
#                 "Std_Relevance": r_std,
#                 "Std_Precision": p_std,
#                 "Hyb_Faithfulness": f_hyb,
#                 "Hyb_Relevance": r_hyb,
#                 "Hyb_Precision": p_hyb,
#                 "Jawaban_Standard": std_ans,
#                 "Jawaban_Hybrid": hyb_ans
#             })
            
#             progress_bar.progress((i + 1) / total_q)
        
#         status_text.text("✅ Evaluasi Selesai!")
#         df_bulk = pd.DataFrame(hasil_evaluasi_massal)
#         st.session_state['df_bulk'] = df_bulk

#     if 'df_bulk' in st.session_state:
#         df_bulk = st.session_state['df_bulk']
        
#         avg_std_f = df_bulk["Std_Faithfulness"].mean()
#         avg_std_r = df_bulk["Std_Relevance"].mean()
#         avg_std_p = df_bulk["Std_Precision"].mean()
        
#         avg_hyb_f = df_bulk["Hyb_Faithfulness"].mean()
#         avg_hyb_r = df_bulk["Hyb_Relevance"].mean()
#         avg_hyb_p = df_bulk["Hyb_Precision"].mean()
        
#         st.markdown("### 🏆 Hasil Rata-Rata (Average Scores)")
#         col_avg1, col_avg2 = st.columns(2)
        
#         with col_avg1:
#             st.markdown("**Standard RAG (Average)**")
#             st.metric("Faithfulness", f"{avg_std_f:.3f}")
#             st.metric("Answer Relevance", f"{avg_std_r:.3f}")
#             st.metric("Context Precision", f"{avg_std_p:.3f}")
            
#         with col_avg2:
#             st.markdown("**Hybrid RAG (Average)**")
#             st.metric("Faithfulness", f"{avg_hyb_f:.3f}", delta=f"{(avg_hyb_f - avg_std_f):.3f}")
#             st.metric("Answer Relevance", f"{avg_hyb_r:.3f}", delta=f"{(avg_hyb_r - avg_std_r):.3f}")
#             st.metric("Context Precision", f"{avg_hyb_p:.3f}", delta=f"{(avg_hyb_p - avg_std_p):.3f}")

#         st.markdown("---")
#         st.markdown("### 📋 Detail Evaluasi per Pertanyaan")
        
#         df_display = df_bulk.drop(columns=["Jawaban_Standard", "Jawaban_Hybrid"])
#         st.dataframe(df_display, use_container_width=True)
        
#         csv_bulk = df_bulk.to_csv(index=False).encode('utf-8')
#         st.download_button(
#             label="📥 Download Hasil Evaluasi Lengkap (.CSV)",
#             data=csv_bulk,
#             file_name="hasil_evaluasi_skripsi_30_pertanyaan.csv",
#             mime="text/csv",
#             use_container_width=True
#         )
import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import pandas as pd
import re
import os
import networkx as nx
import textwrap
from pyvis.network import Network
from dotenv import load_dotenv

# Langchain & Neo4j Imports
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from neo4j import GraphDatabase
from sklearn.metrics.pairwise import cosine_similarity

# =========================================================
# 1. KONFIGURASI HALAMAN
# =========================================================
st.set_page_config(
    page_title="Sistem Skripsi Hybrid RAG",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables
load_dotenv()

# =========================================================
# 2. DEFINISI WARNA (GLOBAL) - SESUAI GAMBAR ANDA
# =========================================================
COLOR_MAP = {
    "Argumen": "#f375d6",
    "Konsep":  "#c5b568",
    "Masalah": "#ffad7a",
    "Tokoh":   "#b6ecd9",
    "Default": "#94A3B8"
}   

# =========================================================
# 3. INISIALISASI RESOURCE (CACHED)
# =========================================================
def save_human_evaluation(data):
    """Menyimpan hasil evaluasi manusia ke file CSV secara permanen."""
    file_name = "hasil_evaluasi_human.csv"
    df_new = pd.DataFrame([data])
    
    if not os.path.isfile(file_name):
        df_new.to_csv(file_name, index=False)
    else:
        df_new.to_csv(file_name, mode='a', header=False, index=False)

@st.cache_resource
def init_resources():
    """
    Menginisialisasi koneksi DB & Model sekali saja.
    """
    # A. Embeddings
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    
    # B. Vector DB
    vectordb = Chroma(
        persist_directory=os.getenv("CHROMA_PATH"),
        embedding_function=embeddings
    )
    
    # C. LLM
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    # D. Neo4j Driver
    driver = GraphDatabase.driver(
        os.getenv("NEO4J_URI"),
        auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
    )
    
    return embeddings, vectordb, llm, driver

try:
    embeddings, vectordb, llm, driver = init_resources()
except Exception as e:
    st.error(f"⚠️ Gagal terhubung ke Database: {e}")
    st.stop()

# =========================================================
# 4. HELPER: TOOLTIP TEXT-ONLY (STABIL & RAPI)
# =========================================================
def format_node_tooltip(node):
    """
    Menggunakan format text biasa dengan baris baru (\n) 
    agar DIJAMIN AMAN dari error rendering HTML.
    """
    # 1. Ambil Tipe Node
    labels = list(node.labels)
    node_type = labels[0] if labels else "INFO"
    
    # 2. Header
    tooltip_text = f"[{node_type.upper()}]\n"
    tooltip_text += "=" * 25 + "\n"
    
    # 3. Filter Properti
    blacklisted_keys = ["embedding", "vector", "element_id", "id", "label"]
    sorted_keys = sorted(node.keys())
    
    for key in sorted_keys:
        if key in blacklisted_keys:
            continue
            
        val = node[key]
        val_str = str(val)
        
        # 4. Rapikan Teks Panjang (Word Wrap)
        if len(val_str) > 50:
            # Bungkus teks setiap 50 karakter agar tidak melebar
            wrapped_lines = textwrap.wrap(val_str, width=50)
            if len(wrapped_lines) > 5:
                val_str = "\n".join(wrapped_lines[:5]) + "\n... (baca selengkapnya)"
            else:
                val_str = "\n".join(wrapped_lines)
        
        pretty_key = key.replace("_", " ").title()
        
        # 5. Susun: Key : Value
        tooltip_text += f"{pretty_key} :\n{val_str}\n"
        tooltip_text += "-" * 15 + "\n" 
        
    return tooltip_text

# =========================================================
# 5. LOGIC: GRAPH VISUALIZATION (PYVIS + FILTER)
# =========================================================
def get_pyvis_html(limit=40, selected_types=None):
    G = nx.Graph()
    
    # Logic Query Dinamis (Filter vs Semua)
    if not selected_types:
        # Ambil Semua (Diacak agar variatif)
        query = f"""
        MATCH (a)-[r]->(b) 
        RETURN a, type(r) AS rel, b 
        ORDER BY rand() LIMIT {limit}
        """
        params = {}
    else:
        # Filter berdasarkan tipe yang dipilih user
        query = f"""
        MATCH (a)-[r]->(b) 
        WHERE any(label IN labels(a) WHERE label IN $types) 
           OR any(label IN labels(b) WHERE label IN $types)
        RETURN a, type(r) AS rel, b 
        ORDER BY rand() LIMIT {limit}
        """
        params = {"types": selected_types}

    with driver.session() as session:
        result = list(session.run(query, **params))
        
        if not result:
            return "<div style='padding:20px; color:red; font-family:sans-serif;'>Tidak ada data graph untuk kategori ini. Coba pilih kategori lain atau naikkan limit.</div>"

        for rec in result:
            a = rec["a"]
            b = rec["b"]
            rel = rec["rel"]
            
            # --- NODE A ---
            la = list(a.labels)[0] if a.labels else "Default"
            tooltip_a = format_node_tooltip(a)
            # Ambil warna dari GLOBAL MAP
            color_a = COLOR_MAP.get(la, COLOR_MAP["Default"])
            
            # --- NODE B ---
            lb = list(b.labels)[0] if b.labels else "Default"
            tooltip_b = format_node_tooltip(b)
            color_b = COLOR_MAP.get(lb, COLOR_MAP["Default"])
            
            # Add Nodes dengan WARNA SPESIFIK
            G.add_node(a.element_id, label=a.get("nama", la), title=tooltip_a, color=color_a)
            G.add_node(b.element_id, label=b.get("nama", lb), title=tooltip_b, color=color_b)
            
            # Add Edge
            G.add_edge(a.element_id, b.element_id, title=rel, label=rel, color="#CBD5E1")

    # Konfigurasi PyVis
    net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="black")
    net.from_nx(G)
    
    # Physics Settings (Stabil & Teks Putih agar kontras dengan warna node)
    net.set_options("""
    var options = {
      "nodes": {
        "font": { "size": 16, "strokeWidth": 2, "color": "white" }, 
        "borderWidth": 2,
        "shadow": { "enabled": true }
      },
      "edges": {
        "color": { "inherit": false }, 
        "smooth": false,
        "font": { "size": 10, "align": "middle" },
        "arrows": { "to": { "enabled": true, "scaleFactor": 0.5 } }
      },
      "physics": {
        "forceAtlas2Based": {
          "gravitationalConstant": -50,
          "springLength": 100
        },
        "solver": "forceAtlas2Based",
        "stabilization": { "enabled": true }
      },
      "interaction": {
        "hover": true, 
        "tooltipDelay": 50
      }
    }
    """)
    
    try:
        path = "tmp_graph.html"
        net.save_graph(path)
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"<div>Error generating graph: {e}</div>"

# =========================================================
# 6. HELPER: LEGENDA WARNA
# =========================================================
def render_legend():
    """
    Menampilkan Bar Legenda Warna.
    Dibuat satu baris (compact) agar tidak dianggap sebagai 'Code Block' oleh Markdown.
    """
    # Container Flexbox
    html_content = '<div style="display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; font-family: sans-serif;">'
    
    for label, color in COLOR_MAP.items():
        if label == "Default": continue
        
        # Item Legenda (Pill Shape) - Dibuat satu baris string agar aman
        html_content += f'<div style="display: flex; align-items: center; background-color: {color}; color: white; padding: 5px 12px; border-radius: 20px; font-size: 13px; font-weight: bold; box-shadow: 0 2px 4px rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.3);"><span style="margin-right: 6px; font-size: 16px;">●</span> {label}</div>'
        
    html_content += '</div>'
    
    # Render dengan unsafe_allow_html=True
    st.markdown(html_content, unsafe_allow_html=True)

# =========================================================
# 7. LOGIC: RAG & METRICS
# =========================================================
def calculate_metrics(query, answer, context):
    """
    Menghitung 3 metrik utama evaluasi RAG menggunakan Cosine Similarity.
    Disesuaikan untuk memproses konteks panjang ber-metadata dari Hybrid RAG.
    """
    if not answer or not context:
        return 0.0, 0.0, 0.0

    try:
        # 1. Embed Query dan Answer
        v_q = np.array(embeddings.embed_query(query)).reshape(1, -1)
        v_a = np.array(embeddings.embed_query(answer)).reshape(1, -1)
        
        # --- ANSWER RELEVANCE ---
        relevance = cosine_similarity(v_q, v_a)[0][0]

        # 2. Pecah Konteks Menjadi Blok-Blok (Chunks)
        context_blocks = [c.strip() for c in context.split("\n\n") if len(c.strip()) > 50]
        if not context_blocks:
            context_blocks = [context]
            
        # Embed semua blok konteks sekaligus
        v_c_list = np.array(embeddings.embed_documents(context_blocks))
        
        # --- FAITHFULNESS ---
        faithfulness_scores = cosine_similarity(v_a, v_c_list)
        faithfulness = np.max(faithfulness_scores) 

        # --- CONTEXT PRECISION ---
        precision_scores = cosine_similarity(v_q, v_c_list)
        precision = np.mean(precision_scores) 
        
        # Penalti Keras: Jika AI menjawab "Maaf/Tidak ditemukan"
        if "tidak ditemukan" in answer.lower() or "maaf" in answer.lower():
            faithfulness = 0.0
            relevance = 0.0

        # Hanya mengembalikan 3 nilai sesuai UI Streamlit Anda
        return round(faithfulness, 3), round(relevance, 3), round(precision, 3)

    except Exception as e:
        print(f"Error perhitungan metrik: {e}")
        return 0.0, 0.0, 0.0
def standard_rag(query):
    # 1. Menggunakan MMR (Max Marginal Relevance) seperti di Colab
    # fetch_k ditarik lebih banyak untuk variasi, k diatur ke 4 agar pas di prompt
    docs = vectordb.max_marginal_relevance_search(query, k=4, fetch_k=10)
    
    # 2. Build Context dengan Metadata Super Lengkap
    context_parts = []
    for i, d in enumerate(docs):
        meta = (
            f"[{i+1}]\n"
            f"Masalah       : {d.metadata.get('masalah', '-')}\n"
            f"Judul Masalah : {d.metadata.get('judul_masalah', '-')}\n"
            f"Topik         : {d.metadata.get('topik', '-')}\n"
            f"Label         : {d.metadata.get('label', '-')}\n"
            f"Tokoh         : {d.metadata.get('tokoh', '-')}\n"
            f"Sumber        : {d.metadata.get('sumber', '-')}\n"
            f"Page          : {d.metadata.get('page', '-')}\n"
            f"Chunk ID      : {d.metadata.get('chunk_id', '-')}\n"
        )
        context_parts.append(meta + f"Teks          :\n{d.page_content}")
        
    ctx = "\n\n".join(context_parts)
    
    # 3. Prompt Akademik persis seperti Colab
    prompt = f"""
    Anda adalah asisten akademik filsafat Islam.

    Gunakan konteks berikut untuk menjawab pertanyaan secara ilmiah,
    sistematis, dan berbasis teks Tahafut al-Falasifah.

    Struktur jawaban WAJIB sebagai berikut:
    1. Penjelasan Konsep
    2. Argumen Filsuf
    3. Bantahan Al-Ghazali
    4. Referensi (Masalah & Halaman PDF)

    Jika informasi untuk menjawab tidak ditemukan di dalam konteks,
    tuliskan "Tidak ditemukan dalam Tahafut al-Falasifah". JANGAN mengarang jawaban.

    Konteks:
    {ctx}

    Pertanyaan:
    {query}

    Jawaban:
    """
    
    # 4. Eksekusi LLM
    ans = llm.invoke(prompt).content
    
    return ans, ctx
def hybrid_rag_final(query):
    # --- 1. Vector Search (Menggunakan MMR ChromaDB) ---
    vektor_docs = vectordb.max_marginal_relevance_search(query, k=4, fetch_k=10)

    # --- 2. Ekstraksi Multi-Keyword (Dipertahankan dari Streamlit) ---
    ext_prompt = f"""Ekstrak maksimal 3 kata kunci utama (nama tokoh atau konsep filosofis) dari pertanyaan berikut. 
    Kembalikan HANYA kata kuncinya, pisahkan dengan koma. JANGAN beri penjelasan.
    Pertanyaan: {query}"""
    
    raw_kws = llm.invoke(ext_prompt).content.strip()
    keyword_list = [k.strip() for k in raw_kws.split(',') if k.strip()]
    
    # --- 3. Graph Search (Menggunakan Schema Akurat dari Colab) ---
    graph_docs = []
    with driver.session() as session:
        # Menggunakan UNWIND untuk melooping keyword yang diekstrak LLM
        cypher_query = """
        UNWIND $kws AS kw
        MATCH (t:Topik)-[:BAGIAN_DARI_TOPIK]-(m:Masalah)-[:BAGIAN_DARI_TEKS]-(c:Chunk)
        WHERE toLower(t.nama) CONTAINS toLower(kw)
           OR toLower(m.id) CONTAINS toLower(kw)
           OR toLower(m.judul) CONTAINS toLower(kw)
        RETURN DISTINCT
            m.id AS masalah_id,
            m.judul AS judul,
            t.nama AS topik,
            c.text AS teks,
            c.page AS halaman,
            c.label AS label,
            c.tokoh AS tokoh
        ORDER BY masalah_id ASC, halaman ASC
        LIMIT 10
        """
        result = session.run(cypher_query, kws=keyword_list)
        graph_docs = [dict(record) for record in result]

    # Fallback: Jika keyword dari LLM gagal menangkap hasil di Graph, pakai query utuh
    if not graph_docs:
        with driver.session() as session:
            fallback_query = """
            MATCH (t:Topik)-[:BAGIAN_DARI_TOPIK]-(m:Masalah)-[:BAGIAN_DARI_TEKS]-(c:Chunk)
            WHERE toLower(t.nama) CONTAINS toLower($search)
               OR toLower(m.id) CONTAINS toLower($search)
               OR toLower(m.judul) CONTAINS toLower($search)
            RETURN 
                m.id AS masalah_id, m.judul AS judul, t.nama AS topik, 
                c.text AS teks, c.page AS halaman, c.label AS label, c.tokoh AS tokoh
            ORDER BY masalah_id ASC, halaman ASC
            LIMIT 10
            """
            result = session.run(fallback_query, search=query)
            graph_docs = [dict(record) for record in result]
            
    # --- 4. Build Context (Pemformatan Rapi) ---
    context_parts = []

    # Inject data Vector
    for i, d in enumerate(vektor_docs):
        meta = (
            f"[KONTEKS VEKTOR {i+1}]\n"
            f"Masalah       : {d.metadata.get('masalah', '-')}\n"
            f"Judul Masalah : {d.metadata.get('judul_masalah', '-')}\n"
            f"Topik         : {d.metadata.get('topik', '-')}\n"
            f"Label         : {d.metadata.get('label', '-')}\n"
            f"Tokoh         : {d.metadata.get('tokoh', '-')}\n"
            f"Halaman       : {d.metadata.get('page', '-')}\n"
        )
        context_parts.append(meta + f"Teks          : {d.page_content}")

    # Inject data Graph
    for i, g in enumerate(graph_docs):
        meta = (
            f"[KONTEKS GRAPH {i+1}]\n"
            f"ID Masalah    : {g['masalah_id']}\n"
            f"Judul Masalah : {g['judul']}\n"
            f"Topik         : {g['topik']}\n"
            f"Label         : {g['label']}\n"
            f"Halaman       : {g['halaman']}\n"
        )
        context_parts.append(meta + f"Teks          : {g['teks']}")

    full_ctx = "\n\n".join(context_parts)
    if not full_ctx.strip():
        full_ctx = "Tidak ada data relevan yang ditemukan dalam database."

    # --- 5. Prompt Synthesis ---
    prompt = f"""
    Anda adalah asisten akademik filsafat Islam yang pakar dalam kitab "Tahafut al-Falasifah" karya Imam Al-Ghazali.

    Tugas Anda adalah menjawab pertanyaan berdasarkan dua sumber konteks:
    1. KONTEKS VEKTOR: Berisi potongan teks detail (mikro).
    2. KONTEKS GRAPH: Berisi struktur masalah dan daftar topik terkait (makro).

    STRUKTUR JAWABAN (WAJIB):
    1. Penjelasan Konsep: Terangkan definisi atau latar belakang masalah.
    2. Argumen Filsuf: Jelaskan posisi filsuf (Aristoteles/Ibnu Sina/Al-Farabi) berdasarkan teks.
    3. Bantahan Al-Ghazali: Jelaskan secara sistematis bagaimana Al-Ghazali meruntuhkan argumen tersebut.
    4. Referensi Akademik: WAJIB sebutkan "ID Masalah" (Contoh: MASALAH PERTAMA) dan "Halaman PDF" untuk setiap poin penting.

    ATURAN KETAT:
    - Jika informasi TIDAK ADA dalam konteks, jawablah: "Maaf, informasi tersebut tidak ditemukan dalam database kitab Tahafut al-Falasifah."
    - DILARANG menggunakan pengetahuan umum Anda sendiri di luar isi kitab.
    - Sertakan sitasi secara konsisten.

    === KONTEKS ===
    {full_ctx}

    Pertanyaan: {query}
    Jawaban:
    """
    
    ans = llm.invoke(prompt).content
    
    return ans, full_ctx

# =========================================================
# 8. UI UTAMA (STREAMLIT)
# =========================================================
st.title("🎓 Sistem Tanya Jawab Filsafat Islam Hybrid RAG")
st.markdown("---")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Input Pertanyaan")
    query_input = st.text_area("Pertanyaan:", height=150, placeholder="Contoh: Apa pendapat Al-Ghazali tentang kausalitas?")
    
    process_btn = st.button("🚀 PROSES ANALISIS", type="primary")
    st.info("Sistem ini membandingkan Standard RAG vs Hybrid RAG (Neo4j).")

# --- MAIN TABS ---
tab1, tab2, tab3 = st.tabs(["💬 Perbandingan", "📊 Metriks Evaluasi", "🕸️ Knowledge Graph Explorer"])

# Logic Process
if process_btn and query_input:
    with st.spinner("Sedang memproses (Standard vs Hybrid)..."):
        # Run Standard
        std_ans, std_ctx = standard_rag(query_input)
        m_std = calculate_metrics(query_input, std_ans, std_ctx)
        
        # Run Hybrid
        hyb_ans, hyb_ctx = hybrid_rag_final(query_input)
        m_hyb = calculate_metrics(query_input, hyb_ans, hyb_ctx)
        
        # Save to session state
        st.session_state['results'] = {
            'std': (std_ans, std_ctx, m_std),
            'hyb': (hyb_ans, hyb_ctx, m_hyb),
            'query': query_input
        }

# Display Results
if 'results' in st.session_state:
    res = st.session_state['results']
    
    # --- TAB 1: HASIL ---
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Standard RAG")
            st.info(res['std'][0])
            with st.expander("Lihat Konteks"):
                st.text(res['std'][1])
        with col2:
            st.subheader("Hybrid RAG")
            st.success(res['hyb'][0])
            with st.expander("Lihat Konteks"):
                st.text(res['hyb'][1])

        # =========================================================
        # PENAMBAHAN: HUMAN EVALUATION SECTION
        # =========================================================
        # 
        # =========================================================
        # PENAMBAHAN: HUMAN EVALUATION SECTION (A/B TESTING)
        # =========================================================
        st.markdown("---")
        st.subheader("📝 Evaluasi Ahli (Human)")
        
        with st.form("human_eval_form"):
            st.write("Berikan penilaian komparatif Anda terhadap kedua jawaban sistem:")
            
            # Membuat dua kolom untuk evaluasi berdampingan
            col_eval_std, col_eval_hyb = st.columns(2)
            
            # --- EVALUASI STANDARD RAG ---
            with col_eval_std:
                st.markdown("**Penilaian Standard RAG**")
                score_std = st.select_slider(
                    "Skor Kualitas (Standard):",
                    options=[1, 2, 3, 4],
                    value=3,
                    key="score_std" # WAJIB ADA KEY AGAR TIDAK ERROR
                )
                is_accurate_std = st.checkbox("Data Sesuai Kitab (Standard)", key="acc_std")
                is_natural_std = st.checkbox("Bahasa Natural/Akademik (Standard)", key="nat_std")

            # --- EVALUASI HYBRID RAG ---
            with col_eval_hyb:
                st.markdown("**Penilaian Hybrid RAG**")
                score_hyb = st.select_slider(
                    "Skor Kualitas (Hybrid):",
                    options=[1, 2, 3, 4],
                    value=3,
                    key="score_hyb" # WAJIB ADA KEY AGAR TIDAK ERROR
                )
                is_accurate_hyb = st.checkbox("Data Sesuai Kitab (Hybrid)", key="acc_hyb")
                is_natural_hyb = st.checkbox("Bahasa Natural/Akademik (Hybrid)", key="nat_hyb")
            
            st.markdown("---")
            # Komentar tambahan secara umum untuk perbandingan
            feedback = st.text_area("Catatan/Kritik Ahli (Perbandingan):", placeholder="Contoh: Hybrid RAG lebih komprehensif menjelaskan argumen Al-Ghazali, sedangkan Standard RAG kehilangan konteks pada bagian...")
            
            submit_eval = st.form_submit_button("Simpan Evaluasi Komparatif")
            
            if submit_eval:
                # Mengambil nilai metrik untuk KEDUANYA agar kode lebih bersih
                m_faith_s, m_relev_s, m_prec_s = res['std'][2]
                m_faith_h, m_relev_h, m_prec_h = res['hyb'][2]

                eval_data = {
                    "Tanggal": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
                    "Pertanyaan": res['query'],
                    
                    # Log Standard RAG
                    "Jawaban_Standard": res['std'][0],
                    "Skor_Human_Std": score_std,
                    "Cek_Akurasi_Std": 1 if is_accurate_std else 0,
                    "Cek_Bahasa_Std": 1 if is_natural_std else 0,
                    "Faith_AI_Std": m_faith_s,
                    "Relev_AI_Std": m_relev_s,
                    "Prec_AI_Std": m_prec_s,
                    
                    # Log Hybrid RAG
                    "Jawaban_Hybrid": res['hyb'][0],
                    "Skor_Human_Hyb": score_hyb,
                    "Cek_Akurasi_Hyb": 1 if is_accurate_hyb else 0,
                    "Cek_Bahasa_Hyb": 1 if is_natural_hyb else 0,
                    "Faith_AI_Hyb": m_faith_h,
                    "Relev_AI_Hyb": m_relev_h,
                    "Prec_AI_Hyb": m_prec_h,
                    
                    # Log Kesimpulan
                    "Komentar_Ahli": feedback
                }
                
                # Panggil fungsi simpan yang sudah dibuat sebelumnya
                save_human_evaluation(eval_data)
                st.success("✅ Data perbandingan berhasil dicatat ke CSV!")
                st.balloons()

    # --- TAB 2: METRIKS ---
    with tab2:
        # Ekstrak 3 nilai metrik dari hasil evaluasi
        m_faith_s, m_relev_s, m_prec_s = res['std'][2]
        m_faith_h, m_relev_h, m_prec_h = res['hyb'][2]
        
        # Update DataFrame untuk 3 metrik
        df = pd.DataFrame({
            "Metrik": ["Faithfulness", "Relevance", "Precision"],
            "Standard RAG": [m_faith_s, m_relev_s, m_prec_s],
            "Hybrid RAG": [m_faith_h, m_relev_h, m_prec_h]
        })
        
        # Tampilkan Tabel dan Grafik Metrik
        st.dataframe(df, use_container_width=True)
        st.bar_chart(df.set_index("Metrik"), color=["#2563EB", "#16A34A"])
        
        # =========================================================
        # KODE ASLI ANDA UNTUK LOG EVALUASI MANUSIA
        # =========================================================
        st.markdown("---")
        st.subheader("📋 Log Evaluasi Manusia (Data Skripsi)")
        
        if os.path.isfile("hasil_evaluasi_human.csv"):
            df_human = pd.read_csv("hasil_evaluasi_human.csv")
            st.dataframe(df_human, use_container_width=True)
            
            # Tombol Download CSV
            csv_data = df_human.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Hasil Evaluasi (.CSV)",
                data=csv_data,
                file_name="evaluasi_skripsi_hybrid_rag.csv",
                mime="text/csv",
                help="Klik untuk mengunduh data evaluasi sebagai lampiran skripsi"
            )
        else:
            st.info("Belum ada data evaluasi manusia yang disimpan.")

    # --- TAB 3: GRAPH (Updated with Filter & Colors) ---
    with tab3:
        st.subheader("Visualisasi Graph Neo4j")
        
        # 1. Kontrol (Filter & Limit)
        col_f1, col_f2, col_f3 = st.columns([2, 1, 1])
        
        with col_f1:
            # Multiselect untuk memfilter node
            filter_options = ["Argumen", "Konsep", "Masalah", "Tokoh"]
            selected_nodes = st.multiselect(
                "Filter Tipe Node (Kosongkan = Tampilkan Semua):", 
                options=filter_options,
                default=filter_options
            )
            
        with col_f2:
            limit_nodes = st.number_input("Limit Node:", min_value=10, max_value=200, value=50)
            
        with col_f3:
            st.write("") # Spacer layout
            st.write("") 
            refresh = st.button("🔄 Refresh Graph", use_container_width=True)

        # 2. Legenda Warna
        st.caption("Keterangan Warna Node:")
        render_legend()
        
        # 3. Generate Graph
        # Gunakan key unik agar tidak reload berulang ulang
        graph_state_key = f"graph_{selected_nodes}_{limit_nodes}"
        
        if refresh or graph_state_key not in st.session_state:
            with st.spinner("Mengambil data graph..."):
                # Kirim filter ke fungsi get_pyvis_html
                filters = selected_nodes if selected_nodes else None
                st.session_state[graph_state_key] = get_pyvis_html(limit_nodes, filters)
                st.session_state['active_key'] = graph_state_key
                
        # Render HTML
        active_key = st.session_state.get('active_key', graph_state_key)
        if active_key in st.session_state:
            components.html(st.session_state[active_key], height=650)

# # =========================================================
# # SISTEM SKRIPSI HYBRID RAG + EVALUASI MATRIKS (FINAL)
# # =========================================================

# import gradio as gr
# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
# import re
# from sklearn.metrics.pairwise import cosine_similarity
# from pyvis.network import Network
# from neo4j import GraphDatabase
# from langchain_openai import OpenAIEmbeddings
# from langchain_openai import ChatOpenAI
# from langchain_community.vectorstores import Chroma
# import base64

# from dotenv import load_dotenv
# import os


# load_dotenv()




# # =========================
# # 3. EMBEDDINGS
# # =========================
# embeddings = OpenAIEmbeddings(
#     model="text-embedding-3-large"
# )


# # =========================
# # 4. VECTOR DB (INI JAWABAN UTAMA)
# # =========================
# vectordb = Chroma(
#     persist_directory=os.getenv("CHROMA_PATH"),
#     embedding_function=embeddings
# )

# # =========================
# # 5. LLM
# # =========================
# llm = ChatOpenAI(
#     model="gpt-4o-mini",
#     temperature=0
# )


# # =========================
# # 6. NEO4J DRIVER
# # =========================
# driver = GraphDatabase.driver(
#     os.getenv("NEO4J_URI"),
#     auth=(
#         os.getenv("NEO4J_USERNAME"),
#         os.getenv("NEO4J_PASSWORD")
#     )
# )


# # =========================================================
# # 1. FUNGSI EVALUASI (SAMA DENGAN KODE ANDA)
# # =========================================================
# def calculate_metrics(query, answer, context, embeddings):
#     if not answer or not context:
#         return 0.0, 0.0, 0.0

#     try:
#         v_q = np.array(embeddings.embed_query(query)).reshape(1, -1)
#         v_a = np.array(embeddings.embed_query(answer)).reshape(1, -1)
#         v_c = np.array(embeddings.embed_query(context)).reshape(1, -1)

#         faithfulness = cosine_similarity(v_a, v_c)[0][0]
#         relevance = cosine_similarity(v_q, v_a)[0][0]

#         citations = re.findall(
#             r'\(hal:|hal\s*\d+|graph|fakta|sumber',
#             answer.lower()
#         )
#         precision = 1.0 if len(citations) > 0 else 0.0

#         return round(faithfulness, 3), round(relevance, 3), round(precision, 3)

#     except Exception as e:
#         print("Metric error:", e)
#         return 0.0, 0.0, 0.0


# # =========================================================
# # 2. VISUALISASI GRAPH (NEO4J → PYVIS → BASE64)
# # =========================================================
# def get_graph_iframe(driver_instance):
#     from pyvis.network import Network
#     import base64
#     import traceback

#     net = Network(
#         height="500px",
#         width="100%",
#         bgcolor="#222222",
#         font_color="white",
#         cdn_resources="in_line"
#     )

#     try:
#         driver_instance.verify_connectivity()

#         with driver_instance.session() as session:
#             query = """
#             MATCH (n)-[r]->(m)
#             RETURN n.nama AS source,
#                    labels(n)[0] AS source_label,
#                    type(r) AS rel,
#                    m.nama AS target,
#                    labels(m)[0] AS target_label
#             LIMIT 30
#             """
#             results = session.run(query)

#             count = 0
#             for record in results:
#                 count += 1
#                 src = record["source"]
#                 tgt = record["target"]

#                 if not src or not tgt:
#                     continue

#                 net.add_node(src, label=src)
#                 net.add_node(tgt, label=tgt)
#                 net.add_edge(src, tgt, label=record["rel"])

#         if count == 0:
#             return "<div style='padding:20px;color:yellow'>⚠️ Neo4j terkoneksi, tapi TIDAK ADA DATA GRAPH.</div>"

#     except Exception as e:
#         return f"""
#         <div style="padding:20px;background:#330000;color:white">
#             <h3>❌ Graph Error</h3>
#             <pre>{repr(e)}</pre>
#             <pre>{traceback.format_exc()}</pre>
#         </div>
#         """

#     html = net.generate_html()

#     with open("temp_graph.html", "w", encoding="utf-8") as f:
#         f.write(html)

#     with open("temp_graph.html", "rb") as f:
#         encoded = base64.b64encode(f.read()).decode()

#     return f"""
#     <iframe
#         src="data:text/html;base64,{encoded}"
#         width="100%"
#         height="550px"
#         style="border:none;"
#     ></iframe>
#     """




# # ======================================================
# # FUNGSI HYBRID RAG (VECTOR + GRAPH)
# # ======================================================
# def hybrid_rag_final(query, vectordb, driver):
#     """
#     Hybrid RAG:
#     - Vector search (Chroma)
#     - Graph lookup (Neo4j)
#     """

#     # --- 1. Vector Retrieval ---
#     docs = vectordb.similarity_search(query, k=5)
#     text_context = "\n\n".join(
#         [f"(Hal: {d.metadata.get('page','-')}) {d.page_content[:300]}..."
#          for d in docs]
#     )

#     # --- 2. Graph Retrieval ---
#     graph_facts = []
#     try:
#         with driver.session() as session:
#             cypher = """
#             MATCH (t:Tokoh)-[r]->(m)
#             WHERE toLower(m.nama) CONTAINS toLower($q)
#                OR toLower(t.nama) CONTAINS toLower($q)
#             RETURN t.nama AS tokoh, type(r) AS rel, m.nama AS objek
#             LIMIT 5
#             """
#             res = session.run(cypher, q=query)
#             for row in res:
#                 graph_facts.append(
#                     f"{row['tokoh']} {row['rel']} {row['objek']} (data graph)"
#                 )
#     except Exception as e:
#         graph_facts.append(f"(Graph error: {e})")

#     graph_context = "\n".join(graph_facts)

#     # --- 3. Gabungkan konteks ---
#     final_context = f"""
#     KONTEN TEKS:
#     {text_context}

#     FAKTA GRAPH:
#     {graph_context}
#     """

#     # --- 4. Prompt ke LLM ---
#     prompt = f"""
#     Anda adalah asisten akademik.
#     Jawab pertanyaan berdasarkan konteks berikut.
#     Sertakan sitasi (Hal: X) atau (data graph) pada setiap klaim fakta.

#     {final_context}

#     Pertanyaan: {query}
#     Jawaban:
#     """

#     answer = llm.invoke(prompt).content

#     return {
#         "answer": answer,
#         "context": final_context
#     }

# # =========================================================
# # 3. PIPELINE UTAMA (RAG + EVALUASI)
# # =========================================================


# def process_query(query):
#     if not query:
#         return "", "", "", "", None, None

#     # ---------- STANDARD RAG ----------
#     docs = vectordb.similarity_search(query, k=5)
#     std_ctx = "\n\n".join([
#         f"[{i+1}] (Hal: {d.metadata.get('page','-')})\n{d.page_content[:250]}..."
#         for i, d in enumerate(docs)
#     ])

#     std_prompt = f"""
#     Jawab secara akademik berdasarkan konteks berikut.
#     Sertakan sitasi (Hal: X).
#     Konteks:
#     {std_ctx}
#     Pertanyaan: {query}
#     """
#     std_ans = llm.invoke(std_prompt).content

#     # ---------- HYBRID RAG ----------
#     hyb = hybrid_rag_final(query, vectordb, driver)
#     hyb_ans = hyb["answer"]
#     hyb_ctx = hyb["context"]

#     # ---------- EVALUASI ----------
#     m_std = calculate_metrics(query, std_ans, std_ctx, embeddings)
#     m_hyb = calculate_metrics(query, hyb_ans, hyb_ctx, embeddings)

#     df = pd.DataFrame({
#         "Metrik": ["Faithfulness", "Relevance", "Precision"],
#         "Standard RAG": m_std,
#         "Hybrid RAG": m_hyb
#     })

#     # ---------- GRAFIK ----------
#     fig, ax = plt.subplots(figsize=(6,4))
#     x = np.arange(3)
#     ax.bar(x-0.2, m_std, 0.4, label="Standard")
#     ax.bar(x+0.2, m_hyb, 0.4, label="Hybrid")
#     ax.set_xticks(x)
#     ax.set_xticklabels(df["Metrik"])
#     ax.set_ylim(0,1.1)
#     ax.set_title("Evaluasi Real-Time per Pertanyaan")
#     ax.legend()
#     plt.tight_layout()

#     return std_ans, std_ctx, hyb_ans, hyb_ctx, df, fig


# # =========================================================
# # 4. UI GRADIO (FINAL)
# # =========================================================
# graph_html = get_graph_iframe(driver)

# with gr.Blocks(theme=gr.themes.Soft(), title="Skripsi Hybrid RAG") as demo:
#     gr.Markdown("# 🎓 Sistem Skripsi Hybrid RAG + Evaluasi Matriks")

#     with gr.Tabs():

#         # --- TAB 1 ---
#         with gr.TabItem("💬 Analisis"):
#             q = gr.Textbox(label="Pertanyaan Akademik")
#             btn = gr.Button("🚀 PROSES")

#             with gr.Row():
#                 with gr.Column():
#                     gr.Markdown("### 🔴 Standard RAG")
#                     out_std = gr.Textbox(lines=5)
#                     ctx_std = gr.Textbox(lines=3, label="Konteks")
#                 with gr.Column():
#                     gr.Markdown("### 🟢 Hybrid RAG")
#                     out_hyb = gr.Textbox(lines=5)
#                     ctx_hyb = gr.Textbox(lines=3, label="Konteks")

#         # --- TAB 2 ---
#         with gr.TabItem("📊 Evaluasi Matriks"):
#             out_df = gr.Dataframe(label="Tabel Evaluasi")
#             out_plot = gr.Plot(label="Grafik Evaluasi")

#         # --- TAB 3 ---
#         with gr.TabItem("🕸️ Knowledge Graph"):
#             gr.HTML(graph_html)

#     btn.click(
#         process_query,
#         inputs=q,
#         outputs=[out_std, ctx_std, out_hyb, ctx_hyb, out_df, out_plot]
#     )

# demo.launch(debug=True)

# import streamlit as st
# import streamlit.components.v1 as components
# import numpy as np
# import pandas as pd
# import re
# import os
# import networkx as nx
# import textwrap
# from pyvis.network import Network
# from dotenv import load_dotenv


# # Langchain & Neo4j Imports
# from langchain_openai import OpenAIEmbeddings, ChatOpenAI
# from langchain_community.vectorstores import Chroma
# from neo4j import GraphDatabase
# from sklearn.metrics.pairwise import cosine_similarity

# # =========================================================
# # 1. KONFIGURASI HALAMAN
# # =========================================================
# st.set_page_config(
#     page_title="Sistem Skripsi Hybrid RAG",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # Load environment variables
# load_dotenv()

# # =========================================================
# # 2. INISIALISASI RESOURCE (CACHED)
# # =========================================================
# @st.cache_resource
# def init_resources():
#     """
#     Menginisialisasi koneksi DB & Model sekali saja agar hemat resource.
#     """
#     # A. Embeddings
#     embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    
#     # B. Vector DB
#     vectordb = Chroma(
#         persist_directory=os.getenv("CHROMA_PATH"),
#         embedding_function=embeddings
#     )
    
#     # C. LLM
#     llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
#     # D. Neo4j Driver
#     driver = GraphDatabase.driver(
#         os.getenv("NEO4J_URI"),
#         auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
#     )
    
#     return embeddings, vectordb, llm, driver

# try:
#     embeddings, vectordb, llm, driver = init_resources()
# except Exception as e:
#     st.error(f"⚠️ Gagal terhubung ke Database: {e}")
#     st.stop()

# # =========================================================
# # 3. HELPER: FORMAT TOOLTIP RAPI (TABEL HTML)
# # =========================================================


# def format_node_tooltip(node):
#     """
#     Versi TEXT-ONLY (Paling Stabil):
#     Menggunakan format teks biasa dengan baris baru (\n) agar rapi 
#     dan dijamin tidak akan muncul kode HTML yang bocor.
#     """
#     # 1. Ambil Tipe Node
#     labels = list(node.labels)
#     node_type = labels[0] if labels else "INFO"
    
#     # 2. Buat Header Tooltip (Huruf Besar & Pemisah)
#     # Gunakan \n untuk enter ke bawah
#     tooltip_text = f"[{node_type.upper()}]\n"
#     tooltip_text += "-" * 30 + "\n" # Garis pemisah
    
#     # 3. Filter & Urutkan Properti
#     blacklisted_keys = ["embedding", "vector", "element_id", "id", "label"]
#     sorted_keys = sorted(node.keys())
    
#     for key in sorted_keys:
#         if key in blacklisted_keys:
#             continue
            
#         val = node[key]
#         val_str = str(val)
        
#         # 4. Rapikan Teks Panjang (Word Wrap)
#         # Jika teks panjang, kita potong barisnya agar tooltip tidak melebar ke kanan
#         if len(val_str) > 50:
#             # Bungkus teks setiap 50 karakter
#             wrapped_lines = textwrap.wrap(val_str, width=50)
#             # Ambil maksimal 4 baris pertama saja agar tidak kepanjangan
#             if len(wrapped_lines) > 4:
#                 val_str = "\n".join(wrapped_lines[:4]) + "\n... (baca selengkapnya)"
#             else:
#                 val_str = "\n".join(wrapped_lines)
        
#         # Percantik Key (misal: "page_number" -> "Page Number")
#         pretty_key = key.replace("_", " ").title()
        
#         # 5. Susun Format: Key : Value
#         tooltip_text += f"{pretty_key} :\n{val_str}\n"
#         tooltip_text += "-" * 10 + "\n" # Pemisah antar field kecil
        
#     return tooltip_text

# # =========================================================
# # 4. LOGIC: GRAPH VISUALIZATION (PYVIS)
# # =========================================================
# def get_pyvis_html(limit=40):
#     G = nx.Graph()
    
#     # 1. DEFINISI WARNA (Sesuai Screenshot Anda)
#     color_map = {
#         "Argumen": "#f375d6",  # Pink/Magenta Cerah
#         "Konsep":  "#c5b568",  # Gold/Mustard (Kecoklatan)
#         "Masalah": "#ffad7a",  # Orange/Salmon
#         "Tokoh":   "#b6ecd9",  # Mint/Tosca Muda (Hijau Pucat)
#         "Default": "#94A3B8"   # Abu-abu (Cadangan)
#     }

#     # 2. Query dengan ORDER BY rand() agar variasi node muncul
#     query = f"""
#     MATCH (a)-[r]->(b) 
#     RETURN a, type(r) AS rel, b 
#     ORDER BY rand()
#     LIMIT {limit}
#     """
    
#     with driver.session() as session:
#         result = list(session.run(query))
        
#         if not result:
#             return "<div>Data Graph Kosong. Pastikan Neo4j berisi data.</div>"

#         for rec in result:
#             a = rec["a"]
#             b = rec["b"]
#             rel = rec["rel"]
            
#             # --- NODE A ---
#             la = list(a.labels)[0] if a.labels else "Default"
#             label_display_a = a.get("nama", la) 
#             tooltip_a = format_node_tooltip(a)
#             # Ambil warna dari map, jika tidak ada pakai Default
#             color_a = color_map.get(la, color_map["Default"])
            
#             # --- NODE B ---
#             lb = list(b.labels)[0] if b.labels else "Default"
#             label_display_b = b.get("nama", lb)
#             tooltip_b = format_node_tooltip(b)
#             color_b = color_map.get(lb, color_map["Default"])
            
#             # Tambahkan Node (Pakai warna manual)
#             G.add_node(a.element_id, label=label_display_a, title=tooltip_a, color=color_a)
#             G.add_node(b.element_id, label=label_display_b, title=tooltip_b, color=color_b)
            
#             # Tambahkan Edge
#             G.add_edge(a.element_id, b.element_id, title=rel, label=rel, color="#CBD5E1")

#     # Konfigurasi PyVis
#     net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="black")
#     net.from_nx(G)
    
#     # Physics & Visual Settings
#     net.set_options("""
#     var options = {
#       "nodes": {
#         "font": { "size": 16, "strokeWidth": 2, "color": "white" }, 
#         "borderWidth": 2,
#         "shadow": { "enabled": true }
#       },
#       "edges": {
#         "color": { "inherit": false }, 
#         "smooth": false,
#         "font": { "size": 10, "align": "middle" },
#         "arrows": { "to": { "enabled": true, "scaleFactor": 0.5 } }
#       },
#       "physics": {
#         "forceAtlas2Based": {
#           "gravitationalConstant": -50,
#           "centralGravity": 0.01,
#           "springLength": 100
#         },
#         "maxVelocity": 50,
#         "solver": "forceAtlas2Based",
#         "timestep": 0.35,
#         "stabilization": { "enabled": true }
#       },
#       "interaction": {
#         "hover": true, 
#         "tooltipDelay": 50
#       }
#     }
#     """)
    
#     try:
#         path = "tmp_graph.html"
#         net.save_graph(path)
#         with open(path, 'r', encoding='utf-8') as f:
#             return f.read()
#     except Exception as e:
#         return f"<div>Error generating graph: {e}</div>"

# # =========================================================
# # 5. LOGIC: RAG & METRICS
# # =========================================================
# def calculate_metrics(query, answer, context):
#     if not answer or not context:
#         return 0.0, 0.0, 0.0

#     v_q = np.array(embeddings.embed_query(query)).reshape(1, -1)
#     v_a = np.array(embeddings.embed_query(answer)).reshape(1, -1)
#     v_c = np.array(embeddings.embed_query(context)).reshape(1, -1)

#     faithfulness = cosine_similarity(v_a, v_c)[0][0]
#     relevance = cosine_similarity(v_q, v_a)[0][0]
    
#     # Simple citation check
#     citations = re.findall(r'(hal|graph|data)', answer.lower())
#     precision = 1.0 if citations else 0.0

#     return round(faithfulness, 3), round(relevance, 3), round(precision, 3)

# def standard_rag(query):
#     docs = vectordb.similarity_search(query, k=5)
#     ctx = "\n".join([f"(Hal: {d.metadata.get('page','-')}) {d.page_content[:250]}..." for d in docs])
#     ans = llm.invoke(f"{ctx}\n\nPertanyaan: {query}").content
#     return ans, ctx

# def hybrid_rag_final(query):
#     # 1. Vector Search
#     docs = vectordb.similarity_search(query, k=5)
#     text_ctx = "\n".join([f"(Hal: {d.metadata.get('page','-')}) {d.page_content[:250]}..." for d in docs])

#     # 2. Graph Search
#     graph_facts = []
#     with driver.session() as session:
#         cypher = """
#         MATCH (t:Tokoh)-[r]->(m)
#         WHERE toLower(t.nama) CONTAINS toLower($q) 
#            OR toLower(m.nama) CONTAINS toLower($q)
#         RETURN t.nama AS tokoh, type(r) AS rel, m.nama AS obj
#         LIMIT 5
#         """
#         for row in session.run(cypher, q=query):
#             graph_facts.append(f"{row['tokoh']} {row['rel']} {row['obj']} (data graph)")
    
#     graph_ctx = "\n".join(graph_facts)

#     # 3. Synthesis
#     prompt = f"""
#     Jawab secara akademik berdasarkan konteks berikut.
#     Sertakan sitasi (Hal: X) atau (data graph).
    
#     TEKS:
#     {text_ctx}
    
#     GRAPH:
#     {graph_ctx}
    
#     Pertanyaan: {query}
#     """
    
#     answer = llm.invoke(prompt).content
#     return answer, text_ctx + "\n" + graph_ctx

# # =========================================================
# # 6. UI UTAMA (STREAMLIT)
# # =========================================================
# st.title("🎓 Sistem Skripsi Hybrid RAG")
# st.markdown("---")

# # --- SIDEBAR ---
# with st.sidebar:
#     st.header("⚙️ Input Pertanyaan")
#     query_input = st.text_area("Pertanyaan:", height=150, placeholder="Contoh: Apa pendapat Al-Ghazali tentang kausalitas?")
#     process_btn = st.button("🚀 PROSES ANALISIS", type="primary")

# # --- MAIN TABS ---
# tab1, tab2, tab3 = st.tabs(["💬 Perbandingan", "📊 Metriks Evaluasi", "🕸️ Knowledge Graph"])

# # Logic Process
# if process_btn and query_input:
#     with st.spinner("Sedang memproses (Standard vs Hybrid)..."):
#         # Run Standard
#         std_ans, std_ctx = standard_rag(query_input)
#         m_std = calculate_metrics(query_input, std_ans, std_ctx)
        
#         # Run Hybrid
#         hyb_ans, hyb_ctx = hybrid_rag_final(query_input)
#         m_hyb = calculate_metrics(query_input, hyb_ans, hyb_ctx)
        
#         # Save to session state
#         st.session_state['results'] = {
#             'std': (std_ans, std_ctx, m_std),
#             'hyb': (hyb_ans, hyb_ctx, m_hyb),
#             'query': query_input
#         }

# # Display Results
# if 'results' in st.session_state:
#     res = st.session_state['results']
    
#     # --- TAB 1: HASIL ---
#     with tab1:
#         col1, col2 = st.columns(2)
#         with col1:
#             st.subheader("Standard RAG")
#             st.info(res['std'][0])
#             with st.expander("Lihat Konteks"):
#                 st.text(res['std'][1])
#         with col2:
#             st.subheader("Hybrid RAG")
#             st.success(res['hyb'][0])
#             with st.expander("Lihat Konteks"):
#                 st.text(res['hyb'][1])

#     # --- TAB 2: METRIKS ---
#     with tab2:
#         df = pd.DataFrame({
#             "Metrik": ["Faithfulness", "Relevance", "Precision"],
#             "Standard RAG": res['std'][2],
#             "Hybrid RAG": res['hyb'][2]
#         })
#         st.dataframe(df, use_container_width=True)
#         st.bar_chart(df.set_index("Metrik"), color=["#2563EB", "#16A34A"])

# # --- TAB 3: GRAPH (Selalu render ulang jika diminta) ---
# with tab3:
#     st.caption("Arahkan mouse ke node untuk melihat metadata lengkap.")
    
#     col_opt, col_view = st.columns([1, 4])
#     with col_opt:
#         limit_nodes = st.slider("Limit Node:", 10, 200, 50)
#         refresh = st.button("🔄 Refresh Graph")
    
#     if refresh or 'graph_html' not in st.session_state:
#         with st.spinner("Mengambil Graph dari Neo4j..."):
#             st.session_state['graph_html'] = get_pyvis_html(limit_nodes)
            
#     components.html(st.session_state['graph_html'], height=650)

#di revisi tgl 11/03/2024
# import streamlit as st
# import streamlit.components.v1 as components
# import numpy as np
# import pandas as pd
# import re
# import os
# import networkx as nx
# import textwrap
# from pyvis.network import Network
# from dotenv import load_dotenv

# # Langchain & Neo4j Imports
# from langchain_openai import OpenAIEmbeddings, ChatOpenAI
# from langchain_community.vectorstores import Chroma
# from neo4j import GraphDatabase
# from sklearn.metrics.pairwise import cosine_similarity

# # =========================================================
# # 1. KONFIGURASI HALAMAN
# # =========================================================
# st.set_page_config(
#     page_title="Sistem Skripsi Hybrid RAG",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # Load environment variables
# load_dotenv()

# # =========================================================
# # 2. DEFINISI WARNA (GLOBAL) - SESUAI GAMBAR ANDA
# # =========================================================
# COLOR_MAP = {
#     "Argumen": "#f375d6",
#     "Konsep":  "#c5b568",
#     "Masalah": "#ffad7a",
#     "Tokoh":   "#b6ecd9",
#     "Default": "#94A3B8"
# }   

# # =========================================================
# # 3. INISIALISASI RESOURCE (CACHED)
# # =========================================================
# def save_human_evaluation(data):
#     """Menyimpan hasil evaluasi manusia ke file CSV secara permanen."""
#     file_name = "hasil_evaluasi_human.csv"
#     df_new = pd.DataFrame([data])
    
#     if not os.path.isfile(file_name):
#         df_new.to_csv(file_name, index=False)
#     else:
#         df_new.to_csv(file_name, mode='a', header=False, index=False)

# @st.cache_resource
# def init_resources():
#     """
#     Menginisialisasi koneksi DB & Model sekali saja.
#     """
#     # A. Embeddings
#     embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    
#     # B. Vector DB
#     vectordb = Chroma(
#         persist_directory=os.getenv("CHROMA_PATH"),
#         embedding_function=embeddings
#     )
    
#     # C. LLM
#     llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
#     # D. Neo4j Driver
#     driver = GraphDatabase.driver(
#         os.getenv("NEO4J_URI"),
#         auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
#     )
    
#     return embeddings, vectordb, llm, driver

# try:
#     embeddings, vectordb, llm, driver = init_resources()
# except Exception as e:
#     st.error(f"⚠️ Gagal terhubung ke Database: {e}")
#     st.stop()

# # =========================================================
# # 4. HELPER: TOOLTIP TEXT-ONLY (STABIL & RAPI)
# # =========================================================
# def format_node_tooltip(node):
#     """
#     Menggunakan format text biasa dengan baris baru (\n) 
#     agar DIJAMIN AMAN dari error rendering HTML.
#     """
#     # 1. Ambil Tipe Node
#     labels = list(node.labels)
#     node_type = labels[0] if labels else "INFO"
    
#     # 2. Header
#     tooltip_text = f"[{node_type.upper()}]\n"
#     tooltip_text += "=" * 25 + "\n"
    
#     # 3. Filter Properti
#     blacklisted_keys = ["embedding", "vector", "element_id", "id", "label"]
#     sorted_keys = sorted(node.keys())
    
#     for key in sorted_keys:
#         if key in blacklisted_keys:
#             continue
            
#         val = node[key]
#         val_str = str(val)
        
#         # 4. Rapikan Teks Panjang (Word Wrap)
#         if len(val_str) > 50:
#             # Bungkus teks setiap 50 karakter agar tidak melebar
#             wrapped_lines = textwrap.wrap(val_str, width=50)
#             if len(wrapped_lines) > 5:
#                 val_str = "\n".join(wrapped_lines[:5]) + "\n... (baca selengkapnya)"
#             else:
#                 val_str = "\n".join(wrapped_lines)
        
#         pretty_key = key.replace("_", " ").title()
        
#         # 5. Susun: Key : Value
#         tooltip_text += f"{pretty_key} :\n{val_str}\n"
#         tooltip_text += "-" * 15 + "\n" 
        
#     return tooltip_text

# # =========================================================
# # 5. LOGIC: GRAPH VISUALIZATION (PYVIS + FILTER)
# # =========================================================
# def get_pyvis_html(limit=40, selected_types=None):
#     G = nx.Graph()
    
#     # Logic Query Dinamis (Filter vs Semua)
#     if not selected_types:
#         # Ambil Semua (Diacak agar variatif)
#         query = f"""
#         MATCH (a)-[r]->(b) 
#         RETURN a, type(r) AS rel, b 
#         ORDER BY rand() LIMIT {limit}
#         """
#         params = {}
#     else:
#         # Filter berdasarkan tipe yang dipilih user
#         query = f"""
#         MATCH (a)-[r]->(b) 
#         WHERE any(label IN labels(a) WHERE label IN $types) 
#            OR any(label IN labels(b) WHERE label IN $types)
#         RETURN a, type(r) AS rel, b 
#         ORDER BY rand() LIMIT {limit}
#         """
#         params = {"types": selected_types}

#     with driver.session() as session:
#         result = list(session.run(query, **params))
        
#         if not result:
#             return "<div style='padding:20px; color:red; font-family:sans-serif;'>Tidak ada data graph untuk kategori ini. Coba pilih kategori lain atau naikkan limit.</div>"

#         for rec in result:
#             a = rec["a"]
#             b = rec["b"]
#             rel = rec["rel"]
            
#             # --- NODE A ---
#             la = list(a.labels)[0] if a.labels else "Default"
#             tooltip_a = format_node_tooltip(a)
#             # Ambil warna dari GLOBAL MAP
#             color_a = COLOR_MAP.get(la, COLOR_MAP["Default"])
            
#             # --- NODE B ---
#             lb = list(b.labels)[0] if b.labels else "Default"
#             tooltip_b = format_node_tooltip(b)
#             color_b = COLOR_MAP.get(lb, COLOR_MAP["Default"])
            
#             # Add Nodes dengan WARNA SPESIFIK
#             G.add_node(a.element_id, label=a.get("nama", la), title=tooltip_a, color=color_a)
#             G.add_node(b.element_id, label=b.get("nama", lb), title=tooltip_b, color=color_b)
            
#             # Add Edge
#             G.add_edge(a.element_id, b.element_id, title=rel, label=rel, color="#CBD5E1")

#     # Konfigurasi PyVis
#     net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="black")
#     net.from_nx(G)
    
#     # Physics Settings (Stabil & Teks Putih agar kontras dengan warna node)
#     net.set_options("""
#     var options = {
#       "nodes": {
#         "font": { "size": 16, "strokeWidth": 2, "color": "white" }, 
#         "borderWidth": 2,
#         "shadow": { "enabled": true }
#       },
#       "edges": {
#         "color": { "inherit": false }, 
#         "smooth": false,
#         "font": { "size": 10, "align": "middle" },
#         "arrows": { "to": { "enabled": true, "scaleFactor": 0.5 } }
#       },
#       "physics": {
#         "forceAtlas2Based": {
#           "gravitationalConstant": -50,
#           "springLength": 100
#         },
#         "solver": "forceAtlas2Based",
#         "stabilization": { "enabled": true }
#       },
#       "interaction": {
#         "hover": true, 
#         "tooltipDelay": 50
#       }
#     }
#     """)
    
#     try:
#         path = "tmp_graph.html"
#         net.save_graph(path)
#         with open(path, 'r', encoding='utf-8') as f:
#             return f.read()
#     except Exception as e:
#         return f"<div>Error generating graph: {e}</div>"

# # =========================================================
# # 6. HELPER: LEGENDA WARNA
# # =========================================================
# def render_legend():
#     """
#     Menampilkan Bar Legenda Warna.
#     Dibuat satu baris (compact) agar tidak dianggap sebagai 'Code Block' oleh Markdown.
#     """
#     # Container Flexbox
#     html_content = '<div style="display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; font-family: sans-serif;">'
    
#     for label, color in COLOR_MAP.items():
#         if label == "Default": continue
        
#         # Item Legenda (Pill Shape) - Dibuat satu baris string agar aman
#         html_content += f'<div style="display: flex; align-items: center; background-color: {color}; color: white; padding: 5px 12px; border-radius: 20px; font-size: 13px; font-weight: bold; box-shadow: 0 2px 4px rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.3);"><span style="margin-right: 6px; font-size: 16px;">●</span> {label}</div>'
        
#     html_content += '</div>'
    
#     # Render dengan unsafe_allow_html=True
#     st.markdown(html_content, unsafe_allow_html=True)

# # =========================================================
# # 7. LOGIC: RAG & METRICS
# # =========================================================
# import random
# import json
# def generate_auto_questions_with_answers(num_questions=5):
#     """Fungsi untuk mengenerate soal & kunci jawaban otomatis dari Chroma DB"""
    
#     keywords = [
#         "kausalitas", "qadim alam", "emanasi", "kebangkitan jasmani", 
#         "pengetahuan Tuhan tentang partikular", "waktu dan ruang", "penciptaan alam"
#     ]
#     random_query = random.choice(keywords)
    
#     # Ambil konteks acak dari Vector DB
#     docs = vectordb.similarity_search(random_query, k=5)
#     context_text = "\n\n".join([d.page_content for d in docs])
    
#     # Prompt JSON untuk Soal + Kunci Jawaban
#     prompt = f"""
#     Anda adalah pakar Filsafat Islam yang sedang menyusun soal ujian analitis berdasarkan kitab Tahafut al-Falasifah karya Imam Al-Ghazali.
    
#     Berdasarkan teks referensi berikut, buatlah {num_questions} pasangan pertanyaan tingkat lanjut beserta kunci jawabannya.
#     Pertanyaan harus analitis, dan kunci jawaban harus padat, akurat, serta murni berdasarkan teks referensi di bawah ini.
    
#     Teks Referensi:
#     {context_text}
    
#     WAJIB kembalikan output HANYA dalam format array JSON yang valid persis seperti contoh berikut, TANPA teks awalan atau akhiran apa pun:
#     [
#         {{"Pertanyaan": "Tulis pertanyaan di sini...", "Kunci_Jawaban": "Tulis jawaban acuan di sini..."}},
#         {{"Pertanyaan": "Tulis pertanyaan kedua...", "Kunci_Jawaban": "Tulis jawaban acuan kedua..."}}
#     ]
#     """
    
#     response = llm.invoke(prompt).content
    
#     # Parsing JSON (Membersihkan sisa-sisa markdown LLM jika ada)
#     try:
#         clean_json = response.strip().strip('```json').strip('```').strip()
#         qa_data = json.loads(clean_json)
#         return qa_data[:num_questions]
#     except Exception as e:
#         return [{"Pertanyaan": "Gagal memproses JSON dari LLM", "Kunci_Jawaban": str(e)}]
    
# def calculate_metrics(query, answer, context, ground_truth=None):
#     """Fungsi menghitung 4 metrik evaluasi (termasuk Answer Correctness)"""
#     if not answer or not context:
#         return 0.0, 0.0, 0.0, 0.0

#     try:
#         v_q = np.array(embeddings.embed_query(query)).reshape(1, -1)
#         v_a = np.array(embeddings.embed_query(answer)).reshape(1, -1)
#         v_c = np.array(embeddings.embed_query(context)).reshape(1, -1)

#         faithfulness = cosine_similarity(v_a, v_c)[0][0]
#         relevance = cosine_similarity(v_q, v_a)[0][0]
#         precision = cosine_similarity(v_q, v_c)[0][0]
        
#         # Metrik Baru: Akurasi (Correctness) vs Kunci Jawaban
#         correctness = 0.0
#         if ground_truth:
#             v_gt = np.array(embeddings.embed_query(ground_truth)).reshape(1, -1)
#             correctness = cosine_similarity(v_a, v_gt)[0][0]

#         return round(faithfulness, 3), round(relevance, 3), round(precision, 3), round(correctness, 3)
#     except Exception as e:
#         print(f"Error metrik: {e}")
#         return 0.0, 0.0, 0.0, 0.0
# def standard_rag(query):
#     # 1. Tingkatkan k=10 agar Context Precision lebih tinggi
#     docs = vectordb.similarity_search(query, k=10)
    
#     # 2. Ambil teks lebih panjang (800 karakter) & masukkan metadata spesifik
#     candidates = []
#     for d in docs:
#         masalah = d.metadata.get('masalah', '-')
#         label = d.metadata.get('label', '-')
#         page = d.metadata.get('page', '-')
        
#         # Teks diperpanjang agar argumen filsafat tidak terpotong di tengah kalimat
#         text_snippet = d.page_content[:800].strip()
        
#         candidates.append(f"(Masalah: {masalah}, Label: {label}, Hal: {page})\n{text_snippet}")
        
#     ctx = "\n\n".join(candidates)
    
#     # 3. Prompt terstruktur untuk menjaga skor Faithfulness & Answer Relevance
#     prompt = f"""
#     Anda adalah asisten akademik filsafat Islam.

#     Gunakan konteks berikut untuk menjawab pertanyaan secara ilmiah,
#     sistematis, dan berbasis teks Tahafut al-Falasifah.

#     Struktur jawaban WAJIB sebagai berikut:
#     1. Penjelasan Konsep
#     2. Argumen Filsuf
#     3. Bantahan Al-Ghazali
#     4. Referensi (Masalah & Halaman PDF)

#     Jika informasi untuk menjawab tidak ditemukan di dalam konteks,
#     tuliskan "Tidak ditemukan dalam Tahafut al-Falasifah". JANGAN mengarang jawaban.

#     Konteks:
#     {ctx}

#     Pertanyaan:
#     {query}

#     Jawaban:
#     """
    
#     # 4. Eksekusi LLM
#     ans = llm.invoke(prompt).content
    
#     # Return format dikembalikan seperti aslinya agar web/UI Anda tidak error
#     return ans, ctx

# def hybrid_rag_final(query):
#     import time
    

#     # --- 0. Ekstraksi Multi-Keyword (Penyapu Bersih) ---
#     ext_prompt = f"""Ekstrak maksimal 3 kata kunci utama (nama tokoh atau konsep filosofis) dari pertanyaan berikut. 
#     Kembalikan HANYA kata kuncinya, pisahkan dengan koma. JANGAN beri penjelasan.
#     Pertanyaan: {query}"""
    
#     raw_kws = llm.invoke(ext_prompt).content.strip()
#     keyword_list = [k.strip() for k in raw_kws.split(',') if k.strip()]
    
#     # --- 1. Vector Search ---
#     docs = vectordb.similarity_search(query, k=5)
#     text_ctx = "\n".join([f"(Hal: {d.metadata.get('page','-')}) {d.page_content[:400]}..." for d in docs])

#     # --- 2. Graph Search (Tangguh Anti-Error dengan Coalesce) ---
#     graph_facts = []
#     with driver.session() as session:
#         cypher_query = """
#         MATCH (n) WHERE toLower(n.nama) CONTAINS toLower($q)
#             MATCH (n)-[r]-(m)
#             RETURN n.nama AS asal, type(r) AS relasi, m.nama AS tujuan
#             LIMIT 20
#         """
#         for row in session.run(cypher_query, q=query):
#             graph_facts.append(f"Fakta Graph: '{row['asal']}' {row['relasi']} '{row['tujuan']}'")

#     # Jika graph_facts kosong, beri pesan khusus
#     if not graph_facts:
#         graph_ctx = "Tidak ada data graph relevan yang ditemukan."
#     else:
#         graph_ctx = "\n".join(graph_facts)
        
#     full_ctx = "=== TEXT CONTEXT ===\n" + text_ctx + "\n\n=== GRAPH CONTEXT ===\n" + graph_ctx

#     # --- 3. Prompt Synthesis ---
#     prompt = f"""
#     Anda adalah asisten peneliti Filsafat Islam spesialis Tahafut al-Falasifah.

#     TUGAS:
#     Jawab pertanyaan pengguna dengan menggabungkan konteks Teks (Chroma) dan Hubungan (Graph).

#     ATURAN WAJIB:
#     1. Gunakan Bahasa Indonesia akademis yang baik.
#     2. SETIAP klaim fakta harus menyertakan referensi dalam kurung.
#        - Jika dari teks: (Hal: X)
#        - Jika dari graph: (Data Graph)
#     3. Jika informasi bertentangan, utamakan Teks PDF.
    
#     {full_ctx}
    
#     Pertanyaan: {query}
#     Jawaban:
#     """
    
#     ans = llm.invoke(prompt).content
    
#     return ans, full_ctx # Kembalikan 3 jika ingin waktu tampil

# # =========================================================
# # 8. UI UTAMA (STREAMLIT)
# # =========================================================
# st.title("🎓 Sistem Tanya Jawab Filsafat Islam Hybrid RAG")
# st.markdown("---")

# # --- SIDEBAR ---
# with st.sidebar:
#     st.header("⚙️ Input Pertanyaan")
#     query_input = st.text_area("Pertanyaan:", height=150, placeholder="Contoh: Apa pendapat Al-Ghazali tentang kausalitas?")
#     # Tambahan input untuk Ground Truth
#     ground_truth_input = st.text_area("Kunci Jawaban (Ground Truth) - Opsional:", height=100, placeholder="Masukkan kunci jawaban dari Tab 4 untuk menghitung Akurasi.")
    
#     process_btn = st.button("🚀 PROSES ANALISIS", type="primary")
#     st.info("Sistem ini membandingkan Standard RAG vs Hybrid RAG (Neo4j).")

# # --- MAIN TABS ---
# tab1, tab2, tab3, tab4 = st.tabs(["💬 Perbandingan", "📊 Metriks Evaluasi", "🕸️ Knowledge Graph Explorer", "🤖 Generator Soal"])

# # Logic Process
# if process_btn and query_input:
#     with st.spinner("Sedang memproses (Standard vs Hybrid)..."):
#         # Run Standard
#         std_ans, std_ctx = standard_rag(query_input)
#         m_std = calculate_metrics(query_input, std_ans, std_ctx, ground_truth_input)
        
#         # Run Hybrid
#         hyb_ans, hyb_ctx = hybrid_rag_final(query_input)
#         m_hyb = calculate_metrics(query_input, hyb_ans, hyb_ctx, ground_truth_input)
        
#         # Save to session state
#         st.session_state['results'] = {
#             'std': (std_ans, std_ctx, m_std),
#             'hyb': (hyb_ans, hyb_ctx, m_hyb),
#             'query': query_input,
#             'ground_truth': ground_truth_input
#         }

# # Display Results
# if 'results' in st.session_state:
#     res = st.session_state['results']
    
#     # --- TAB 1: HASIL ---
#     with tab1:
#         col1, col2 = st.columns(2)
#         with col1:
#             st.subheader("Standard RAG")
#             st.info(res['std'][0])
#             with st.expander("Lihat Konteks"):
#                 st.text(res['std'][1])
#         with col2:
#             st.subheader("Hybrid RAG")
#             st.success(res['hyb'][0])
#             with st.expander("Lihat Konteks"):
#                 st.text(res['hyb'][1])

#         # =========================================================
#         # PENAMBAHAN: HUMAN EVALUATION SECTION
#         # =========================================================
#         st.markdown("---")
#         st.subheader("📝 Evaluasi Ahli (Human)")
        
#         with st.form("human_eval_form"):
#             st.write("Berikan penilaian Anda terhadap jawaban **Hybrid RAG**:")
            
#             # Pilihan skor Likert 1-5
#             score = st.select_slider(
#                 "Skor Kualitas (1: Tidak Sesuai, 2: Kurang Sesuai, 3: Cukup Sesuai, 4: Sesuai):",
#                 options=[1, 2, 3, 4],
#                 value=3
#             )
            
#             # Checklist kualitatif
#             col_eval1, col_eval2 = st.columns(2)
#             is_accurate = col_eval1.checkbox("Data Sesuai sesuai Kitab")
#             is_natural = col_eval2.checkbox("Bahasa Natural/Akademik")
            
#             # Komentar tambahan
#             feedback = st.text_area("Catatan/Kritik Ahli:", placeholder="Contoh: Interpretasi tentang emansipasi sudah benar, tapi kurang detail di bagian...")
            
#             submit_eval = st.form_submit_button("Simpan Evaluasi Manusia")
#             if submit_eval:
#                 # Mengambil nilai metrik agar kode lebih bersih
#                 # res['hyb'][2] berisi tuple (faithfulness, relevance, precision)
#                 m_faith, m_relev, m_prec, m_corr = res['hyb'][2]

#                 eval_data = {
#                     "Tanggal": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
#                     "Pertanyaan": res['query'],
#                     "Jawaban_Hybrid": res['hyb'][0], # Tambahkan ini agar CSV lengkap
#                     "Skor_Human_Likert": score,
#                     "Cek_Akurasi": 1 if is_accurate else 0, # Ubah ke angka agar mudah diolah di Excel
#                     "Cek_Bahasa": 1 if is_natural else 0,
#                     "Komentar_Ahli": feedback,
#                     "Faithfulness_AI": m_faith,
#                     "Answer_Relevance_AI": m_relev,
#                     "Context_Precision_AI": m_prec
#                 }
                
#                 # Panggil fungsi simpan yang sudah dibuat sebelumnya
#                 save_human_evaluation(eval_data)
#                 st.success("✅ Data berhasil dicatat ke CSV!")
#                 st.balloons()

#     # --- TAB 2: METRIKS ---
#     # --- TAB 2: METRIKS ---
#     with tab2:
#         # Menampilkan status Ground Truth
#         if res.get('ground_truth'):
#             st.success("✅ Menggunakan Kunci Jawaban (Ground Truth) untuk metrik Answer Correctness.")
#         else:
#             st.warning("⚠️ Kunci Jawaban tidak diisi. Skor Answer Correctness akan bernilai 0.")

#         # Ekstrak 4 nilai metrik dari hasil evaluasi
#         m_faith_s, m_relev_s, m_prec_s, m_corr_s = res['std'][2]
#         m_faith_h, m_relev_h, m_prec_h, m_corr_h = res['hyb'][2]
        
#         # Update DataFrame untuk 4 metrik
#         df = pd.DataFrame({
#             "Metrik": ["Faithfulness", "Relevance", "Precision", "Answer Correctness"],
#             "Standard RAG": [m_faith_s, m_relev_s, m_prec_s, m_corr_s],
#             "Hybrid RAG": [m_faith_h, m_relev_h, m_prec_h, m_corr_h]
#         })
        
#         # Tampilkan Tabel dan Grafik Metrik
#         st.dataframe(df, use_container_width=True)
#         st.bar_chart(df.set_index("Metrik"), color=["#2563EB", "#16A34A"])
        
#         # =========================================================
#         # KODE ASLI ANDA UNTUK LOG EVALUASI MANUSIA
#         # =========================================================
#         st.markdown("---")
#         st.subheader("📋 Log Evaluasi Manusia (Data Skripsi)")
        
#         if os.path.isfile("hasil_evaluasi_human.csv"):
#             df_human = pd.read_csv("hasil_evaluasi_human.csv")
#             st.dataframe(df_human, use_container_width=True)
            
#             # Tombol Download CSV
#             csv_data = df_human.to_csv(index=False).encode('utf-8')
#             st.download_button(
#                 label="📥 Download Hasil Evaluasi (.CSV)",
#                 data=csv_data,
#                 file_name="evaluasi_skripsi_hybrid_rag.csv",
#                 mime="text/csv",
#                 help="Klik untuk mengunduh data evaluasi sebagai lampiran skripsi"
#             )
#         else:
#             st.info("Belum ada data evaluasi manusia yang disimpan.")

#     # --- TAB 3: GRAPH (Updated with Filter & Colors) ---
#     with tab3:
#         st.subheader("Visualisasi Graph Neo4j")
        
#         # 1. Kontrol (Filter & Limit)
#         col_f1, col_f2, col_f3 = st.columns([2, 1, 1])
        
#         with col_f1:
#             # Multiselect untuk memfilter node
#             filter_options = ["Argumen", "Konsep", "Masalah", "Tokoh"]
#             selected_nodes = st.multiselect(
#                 "Filter Tipe Node (Kosongkan = Tampilkan Semua):", 
#                 options=filter_options,
#                 default=filter_options
#             )
            
#         with col_f2:
#             limit_nodes = st.number_input("Limit Node:", min_value=10, max_value=200, value=50)
            
#         with col_f3:
#             st.write("") # Spacer layout
#             st.write("") 
#             refresh = st.button("🔄 Refresh Graph", use_container_width=True)

#         # 2. Legenda Warna
#         st.caption("Keterangan Warna Node:")
#         render_legend()
        
#         # 3. Generate Graph
#         # Gunakan key unik agar tidak reload berulang ulang
#         graph_state_key = f"graph_{selected_nodes}_{limit_nodes}"
        
#         if refresh or graph_state_key not in st.session_state:
#             with st.spinner("Mengambil data graph..."):
#                 # Kirim filter ke fungsi get_pyvis_html
#                 filters = selected_nodes if selected_nodes else None
#                 st.session_state[graph_state_key] = get_pyvis_html(limit_nodes, filters)
#                 st.session_state['active_key'] = graph_state_key
                
#         # Render HTML
#         active_key = st.session_state.get('active_key', graph_state_key)
#         if active_key in st.session_state:
#             components.html(st.session_state[active_key], height=650)

#     # --- TAB 4: GENERATOR SOAL OTOMATIS ---
#     # --- TAB 4: GENERATOR & EVALUASI MASSAL (AUTO-EVALUATE) ---
# with tab4:
#     st.subheader("🤖 Generator & Evaluasi Massal (Automated Testing)")
#     st.write("Sistem akan membuat soal otomatis, lalu mengadunya secara real-time antara Standard RAG vs Hybrid RAG.")
    
#     col_gen1, col_gen2 = st.columns([1, 3])
    
#     with col_gen1:
#         jumlah_soal = st.number_input("Jumlah Soal Uji:", min_value=1, max_value=50, value=5)
#         btn_generate_eval = st.button("🚀 Buat & Evaluasi Otomatis", type="primary", use_container_width=True)
        
#     with col_gen2:
#         if btn_generate_eval:
#             with st.spinner(f"Tahap 1/2: AI sedang membaca dokumen & merangkai {jumlah_soal} soal..."):
#                 try:
#                     generated_qa = generate_auto_questions_with_answers(num_questions=jumlah_soal)
#                     st.success("Soal berhasil dibuat! Memulai evaluasi model...")
                    
#                     hasil_evaluasi_massal = []
                    
#                     # Looping mengevaluasi setiap pertanyaan
#                     progress_bar = st.progress(0)
#                     for idx, item in enumerate(generated_qa):
#                         q = item.get("Pertanyaan", "")
#                         gt = item.get("Kunci_Jawaban", "")
                        
#                         if not q: continue
                        
#                         # Jalankan Standard RAG
#                         s_ans, s_ctx = standard_rag(q)
#                         f_s, r_s, p_s, c_s = calculate_metrics(q, s_ans, s_ctx, gt)
                        
#                         # Jalankan Hybrid RAG
#                         h_ans, h_ctx = hybrid_rag_final(q)
#                         f_h, r_h, p_h, c_h = calculate_metrics(q, h_ans, h_ctx, gt)
#                         # Simpan ke list dengan metrik LENGKAP untuk kedua model
#                         hasil_evaluasi_massal.append({
#                             "No": idx + 1,
#                             "Pertanyaan": q,
#                             "Kunci Jawaban (Ground Truth)": gt,
                            
#                             # --- HASIL STANDARD RAG ---
#                             "Jawaban Standard RAG": s_ans,
#                             "Faithfulness Standard": f_s,
#                             "Relevance Standard": r_s,
#                             "Precision Standard": p_s,
#                             "Akurasi Standard": c_s, 
                            
#                             # --- HASIL HYBRID RAG ---
#                             "Jawaban Hybrid RAG": h_ans,
#                             "Faithfulness Hybrid": f_h,
#                             "Relevance Hybrid": r_h,
#                             "Precision Hybrid": p_h,
#                             "Akurasi Hybrid": c_h
#                         })
                        
#                         # Update progress bar
#                         progress_bar.progress((idx + 1) / len(generated_qa))
                        
#                     # Simpan hasil akhir ke session state
#                     st.session_state['eval_massal'] = hasil_evaluasi_massal
#                     st.success(f"Selesai! {len(hasil_evaluasi_massal)} pertanyaan berhasil dievaluasi.")
                    
#                 except Exception as e:
#                     st.error(f"Terjadi kesalahan saat evaluasi massal: {e}")
                    
#         # TAMPILKAN TABEL HASIL & SKORNYA
#         if 'eval_massal' in st.session_state:
#             df_massal = pd.DataFrame(st.session_state['eval_massal'])
            
#             st.write("### 📊 Hasil Perbandingan Skor Otomatis")
            
#             # Tampilkan metrik rata-rata di atas tabel
#             avg_std = df_massal['Akurasi Standard'].mean()
#             avg_hyb = df_massal['Akurasi Hybrid'].mean()
            
#             col_met1, col_met2 = st.columns(2)
#             col_met1.metric("Rata-rata Akurasi Standard RAG", f"{avg_std:.3f}")
#             col_met2.metric("Rata-rata Akurasi Hybrid RAG", f"{avg_hyb:.3f}", delta=f"{(avg_hyb - avg_std):.3f}")
            
#             # Tampilkan tabel lengkapnya
#             st.dataframe(df_massal, use_container_width=True)
            
#             # Tombol Download untuk Bab 4 Skripsi
#             csv_massal = df_massal.to_csv(index=False).encode('utf-8')
#             st.download_button(
#                 label="📥 Download Tabel Hasil Evaluasi (.CSV)",
#                 data=csv_massal,
#                 file_name="hasil_uji_massal_skripsi.csv",
#                 mime="text/csv"
#             )
# import streamlit as st
# import streamlit.components.v1 as components
# import numpy as np
# import pandas as pd
# import re
# import os
# import time
# import networkx as nx
# import textwrap
# from pyvis.network import Network
# from dotenv import load_dotenv

# # Langchain & Neo4j Imports
# from langchain_openai import OpenAIEmbeddings, ChatOpenAI
# from langchain_community.vectorstores import Chroma
# from neo4j import GraphDatabase
# from sklearn.metrics.pairwise import cosine_similarity

# # =========================================================
# # 1. KONFIGURASI HALAMAN
# # =========================================================
# st.set_page_config(
#     page_title="Sistem Skripsi Hybrid RAG",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# load_dotenv()

# # =========================================================
# # 2. DEFINISI WARNA (GLOBAL)
# # =========================================================
# COLOR_MAP = {
#     "Argumen": "#f375d6",  # Pink
#     "Konsep":  "#c5b568",  # Gold
#     "Masalah": "#ffad7a",  # Salmon
#     "Tokoh":   "#b6ecd9",  # Mint
#     "Default": "#94A3B8"   # Slate
# }

# # =========================================================
# # 3. INISIALISASI RESOURCE
# # =========================================================
# @st.cache_resource
# def init_resources():
#     embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
#     vectordb = Chroma(persist_directory=os.getenv("CHROMA_PATH"), embedding_function=embeddings)
#     llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
#     driver = GraphDatabase.driver(
#         os.getenv("NEO4J_URI"),
#         auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
#     )
#     return embeddings, vectordb, llm, driver

# try:
#     embeddings, vectordb, llm, driver = init_resources()
# except Exception as e:
#     st.error(f"⚠️ Gagal terhubung ke Database: {e}")
#     st.stop()

# # =========================================================
# # 4. HELPER: GRAPH VISUALIZATION
# # =========================================================
# def format_node_tooltip(node):
#     labels = list(node.labels)
#     node_type = labels[0] if labels else "INFO"
#     tooltip_text = f"[{node_type.upper()}]\n" + "=" * 25 + "\n"
#     blacklisted_keys = ["embedding", "vector", "element_id", "id", "label"]
#     for key in sorted(node.keys()):
#         if key not in blacklisted_keys:
#             val = str(node[key])
#             if len(val) > 50: val = "\n".join(textwrap.wrap(val, width=50)[:5]) + "..."
#             tooltip_text += f"{key.replace('_', ' ').title()} :\n{val}\n" + "-" * 15 + "\n"
#     return tooltip_text

# def get_pyvis_html(limit=50):
#     G = nx.Graph()
#     query = f"MATCH (a)-[r]->(b) RETURN a, type(r) AS rel, b ORDER BY rand() LIMIT {limit}"
#     with driver.session() as session:
#         result = list(session.run(query))
#         if not result: return "<div style='color:red;'>Data graph kosong di Neo4j.</div>"
#         for rec in result:
#             for key in ["a", "b"]:
#                 node = rec[key]
#                 lbl = list(node.labels)[0] if node.labels else "Default"
#                 G.add_node(node.element_id, label=node.get("nama", lbl), title=format_node_tooltip(node), color=COLOR_MAP.get(lbl, COLOR_MAP["Default"]))
#             G.add_edge(rec["a"].element_id, rec["b"].element_id, title=rec["rel"], label=rec["rel"], color="#CBD5E1")
#     net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="black")
#     net.from_nx(G)
#     net.set_options('{"nodes": {"font": {"color": "white"}}, "physics": {"enabled": true}}')
#     path = "tmp_graph.html"
#     net.save_graph(path)
#     return open(path, 'r', encoding='utf-8').read()

# # =========================================================
# # 5. LOGIC: RAG & METRICS
# # =========================================================
# def calculate_metrics(query, answer, context):
#     if not answer or not context: return 0.0, 0.0, 0.0
#     v_q = np.array(embeddings.embed_query(query)).reshape(1, -1)
#     v_a = np.array(embeddings.embed_query(answer)).reshape(1, -1)
#     v_c = np.array(embeddings.embed_query(context)).reshape(1, -1)
#     faith = round(cosine_similarity(v_a, v_c)[0][0], 3)
#     relev = round(cosine_similarity(v_q, v_a)[0][0], 3)
#     # Perhitungan Context Precision (Query vs Context)
#     # Mengukur apakah data yang ditarik (dari Chroma/Neo4j) benar-benar relevan dengan pertanyaan
#     prec = cosine_similarity(v_q, v_c)[0][0]
#     return faith, relev, prec

# def standard_rag(query):
#     start = time.time()
#     docs = vectordb.similarity_search(query, k=5)
#     ctx = "\n".join([f"(Hal: {d.metadata.get('page','-')}) {d.page_content[:250]}..." for d in docs])
#     ans = llm.invoke(f"Konteks:\n{ctx}\n\nPertanyaan: {query}").content
#     return ans, ctx, round(time.time() - start, 2)

# def hybrid_rag(query):
#     start = time.time()
#     docs = vectordb.similarity_search(query, k=5)
#     text_ctx = "\n".join([f"(Hal: {d.metadata.get('page','-')}) {d.page_content[:250]}..." for d in docs])
#     graph_facts = []
#     with driver.session() as session:
#         cypher = "MATCH (t:Tokoh)-[r]->(m) WHERE toLower(t.nama) CONTAINS toLower($q) OR toLower(m.nama) CONTAINS toLower($q) RETURN t.nama AS t, type(r) AS r, m.nama AS o LIMIT 5"
#         for row in session.run(cypher, q=query): graph_facts.append(f"{row['t']} {row['r']} {row['o']} (data graph)")
#     graph_ctx = "\n".join(graph_facts)
#     full_ctx = text_ctx + "\n" + graph_ctx
#     ans = llm.invoke(f"Jawab akademik dengan sitasi.\nTEKS:\n{text_ctx}\nGRAPH:\n{graph_ctx}\nPertanyaan: {query}").content
#     return ans, full_ctx, round(time.time() - start, 2)

# # =========================================================
# # 6. UI STREAMLIT
# # =========================================================
# st.title("🎓 Sistem Tanya Jawab Filsafat Islam Hybrid RAG")

# with st.sidebar:
#     st.header("⚙️ Kontrol")
#     query_input = st.text_area("Input Pertanyaan Skripsi:", height=100)
#     process_btn = st.button("🚀 ANALISIS SEKARANG", type="primary")

# tab1, tab2, tab3 = st.tabs(["💬 Jawaban", "📊 Evaluasi & Waktu", "🕸️ Graph Explorer"])

# if process_btn and query_input:
#     with st.spinner("Memproses..."):
#         s_ans, s_ctx, s_time = standard_rag(query_input)
#         h_ans, h_ctx, h_time = hybrid_rag(query_input)
#         st.session_state['results'] = {
#             'std': (s_ans, s_ctx, calculate_metrics(query_input, s_ans, s_ctx), s_time),
#             'hyb': (h_ans, h_ctx, calculate_metrics(query_input, h_ans, h_ctx), h_time)
#         }

# if 'results' in st.session_state:
#     res = st.session_state['results']
#     with tab1:
#         c1, c2 = st.columns(2); c1.subheader("Standard RAG"); c1.info(res['std'][0]); c2.subheader("Hybrid RAG"); c2.success(res['hyb'][0])
#     with tab2:
#         df = pd.DataFrame({
#             "Metrik": ["Faithfulness", "Relevance", "Precision", "Time (sec)"],
#             "Standard": [res['std'][2][0], res['std'][2][1], res['std'][2][2], res['std'][3]],
#             "Hybrid": [res['hyb'][2][0], res['hyb'][2][1], res['hyb'][2][2], res['hyb'][3]]
#         })
#         st.table(df); st.bar_chart(df.iloc[:3].set_index("Metrik")); st.write("**Waktu Respons**"); st.bar_chart(df.iloc[3:].set_index("Metrik"))

# with tab3:
#     st.subheader("Knowledge Graph Neo4j")
#     st.markdown(" ".join([f'<span style="background:{c};padding:5px;border-radius:10px;color:white">{k}</span>' for k,c in COLOR_MAP.items()]), unsafe_allow_html=True)
    
#     # OTOMATIS LOAD: Jika g_html belum ada di session_state, buat sekarang
#     if 'g_html' not in st.session_state:
#         with st.spinner("Memuat Graph..."):
#             st.session_state['g_html'] = get_pyvis_html(50)
    
#     # Tombol refresh tetap ada jika user ingin mengacak ulang node
#     if st.button("🔄 Refresh/Acak Graf"):
#         with st.spinner("Mengacak Ulang..."):
#             st.session_state['g_html'] = get_pyvis_html(50)
#             st.rerun()

#     components.html(st.session_state['g_html'], height=700)