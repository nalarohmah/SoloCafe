import streamlit as st
import pandas as pd
import plotly.express as px
import os
import markdown
import base64
from datetime import datetime
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
import requests

# Load env variables
load_dotenv()

@st.cache_data(ttl=3600)
def get_weather_solo():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=-7.5561&longitude=110.8317&current_weather=true"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            temp = data['current_weather']['temperature']
            code = data['current_weather']['weathercode']
            
            weather_desc = {
                0: "Cerah", 1: "Cerah Berawan", 2: "Berawan Sebagian", 3: "Mendung",
                45: "Berkabut", 48: "Kabut Tebal",
                51: "Gerimis Ringan", 53: "Gerimis Sedang", 55: "Gerimis Lebat",
                61: "Hujan Ringan", 63: "Hujan Sedang", 65: "Hujan Lebat",
                95: "Badai Petir", 96: "Badai Petir Ringan", 99: "Badai Petir Lebat"
            }
            condition = weather_desc.get(code, "Tidak diketahui")
            return f"Suhu {temp}°C, Kondisi: {condition}"
        return "Tidak dapat memuat data cuaca (API Error)"
    except Exception as e:
        return "Tidak dapat memuat data cuaca"

# --- Page Config ---
st.set_page_config(page_title="AI UMKM Assistant", layout="wide")

def add_bg_from_local(image_file):
    try:
        with open(image_file, "rb") as file:
            encoded_string = base64.b64encode(file.read()).decode()
        st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url(data:image/png;base64,{encoded_string});
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        /* Membuat area konten utama sepenuhnya transparan (melayang) */
        .block-container {{
            background-color: transparent !important;
            box-shadow: none !important;
            padding-top: 1rem;
        }}
        
        /* Mengubah warna teks global menjadi coklat kopi gelap */
        .stApp, .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .stApp span, .stApp label, .stApp div {{
            color: #3e2723 !important; 
        }}
        
        /* Teks pada metrik dan tab */
        [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {{
            color: #3e2723 !important;
        }}
        button[data-baseweb="tab"] p {{
            color: #3e2723 !important;
            font-weight: 600;
        }}
        
        /* Transparansi header bawaan */
        .stApp > header {{
            background-color: transparent !important;
        }}
        
        /* Modifikasi kotak input chat agar terang */
        [data-testid="stChatInput"] > div, [data-testid="stChatInput"] div[data-baseweb="input"] {{
            background-color: #f7f3eb !important;
            border-radius: 8px;
            border: 1px solid #8d6e63 !important;
        }}
        [data-testid="stChatInput"] textarea {{
            color: #3e2723 !important;
            background-color: transparent !important;
        }}
        [data-testid="stChatInput"] textarea::placeholder {{
            color: #8d6e63 !important;
        }}
        /* Modifikasi Sidebar agar bernuansa Kopi Putih */
        [data-testid="stSidebar"] {{
            background-color: #fdfaf5 !important;
        }}
        [data-testid="stSidebar"] * {{
            color: #3e2723 !important;
        }}
        
        /* Modifikasi File Uploader agar terang */
        [data-testid="stFileUploader"], [data-testid="stFileUploader"] > section, [data-testid="stFileUploaderDropzone"] {{
            background-color: #ffffff !important;
            border: 2px dashed #8d6e63 !important;
            border-radius: 10px;
        }}
        [data-testid="stFileUploader"] * {{
            color: #3e2723 !important;
        }}
        [data-testid="stFileUploader"] button {{
            background-color: #f7f3eb !important;
            border: 1px solid #8d6e63 !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
        )
    except FileNotFoundError:
        pass

# Memanggil fungsi background (Pastikan gambar bernama background.png ada di folder assets)
add_bg_from_local(os.path.join("assets", "background.png"))

# --- Custom CSS for Social Media Chat Style ---
st.markdown("""
<style>
/* Base Bubble Style */
.chat-bubble-wrapper {
    display: flex;
    width: 100%;
    margin-bottom: 15px;
}

.chat-bubble {
    max-width: 80%;
    padding: 12px 18px;
    border-radius: 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    font-size: 15px;
}

.chat-bubble p {
    margin-bottom: 0.5rem;
}
.chat-bubble p:last-child {
    margin-bottom: 0;
}

/* User Message */
.chat-bubble-wrapper.user {
    justify-content: flex-end;
}
.chat-bubble-wrapper.user .chat-bubble {
    background-color: #e2e8f0;
    color: #1e293b;
    border-bottom-right-radius: 4px;
}

/* Agent Message */
.chat-bubble-wrapper.agent {
    justify-content: flex-start;
}
.chat-bubble-wrapper.agent .chat-bubble {
    background-color: #dcd0ff;
    color: #2d3748;
    border-bottom-left-radius: 4px;
}

/* Typing Indicator Animation */
@keyframes bounce {
    0%, 80%, 100% { transform: scale(0); }
    40% { transform: scale(1); }
}
.typing-dot {
    width: 8px;
    height: 8px;
    background-color: #6b46c1;
    border-radius: 50%;
    animation: bounce 1.4s infinite ease-in-out both;
}
.typing-dot:nth-child(1) { animation-delay: -0.32s; }
.typing-dot:nth-child(2) { animation-delay: -0.16s; }
.typing-container {
    display: flex;
    align-items: center;
    gap: 6px;
    height: 24px;
    padding: 0 5px;
}
</style>
""", unsafe_allow_html=True)

# --- Load Data ---
@st.cache_data
def load_data():
    df_penjualan = pd.read_csv("penjualan_coffee.csv")
    df_stok = pd.read_csv("stok_barang_coffee.csv")
    df_penjualan['Tanggal'] = pd.to_datetime(df_penjualan['Tanggal'])
    return df_penjualan, df_stok

df_penjualan, df_stok = load_data()

# --- Sidebar: Unggah Data Penjualan ---
with st.sidebar:
    st.header("⚙️ Pengaturan Data")
    st.markdown("Unggah data penjualan bulanan baru (CSV) untuk ditambahkan secara permanen ke database.")
    uploaded_file = st.file_uploader("Pilih File CSV", type=['csv'])
    
    if uploaded_file is not None:
        try:
            df_new = pd.read_csv(uploaded_file)
            required_cols = ['Tanggal', 'Nama_Barang', 'Terjual', 'Total_Pendapatan']
            
            # Cek apakah kolom yang diwajibkan ada di dalam file CSV yang diunggah
            if all(col in df_new.columns for col in required_cols):
                st.write(f"Terdeteksi {len(df_new)} baris data valid.")
                if st.button("Tambahkan ke Database"):
                    df_old = pd.read_csv("penjualan_coffee.csv")
                    df_combined = pd.concat([df_old, df_new], ignore_index=True)
                    df_combined.to_csv("penjualan_coffee.csv", index=False)
                    st.success("Data berhasil ditambahkan!")
                    st.cache_data.clear()
                    st.rerun()
            else:
                st.error(f"Format salah! Pastikan ada kolom: {', '.join(required_cols)}")
        except Exception as e:
            st.error(f"Terjadi kesalahan saat membaca file: {e}")

# --- Title / Logo ---
logo_path = os.path.join("assets", "logo.png")
if os.path.exists(logo_path):
    st.image(logo_path, width=400)  # Ukuran lebar disesuaikan agar rapi
else:
    st.title("📊 Dashboard Analis AI - UMKM")

# --- Tabs ---
tab1, tab3, tab2 = st.tabs(["📈 Dashboard Visual", "📅 Laporan Bulanan", "🤖 Chat Asisten AI"])

with tab1:
    st.header("Ringkasan Bisnis (1 Tahun Terakhir)")
    
    # --- Metrics ---
    total_pendapatan = df_penjualan['Total_Pendapatan'].sum()
    produk_terlaris = df_penjualan.groupby('Nama_Barang')['Terjual'].sum().idxmax()
    stok_menipis = df_stok[df_stok['Stok_Saat_Ini'] <= df_stok['Batas_Aman']]['Nama_Barang'].tolist()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Pendapatan", f"Rp {total_pendapatan:,.0f}")
    col2.metric("Produk Terlaris", produk_terlaris)
    
    if stok_menipis:
        col3.warning(f"Stok Menipis: {', '.join(stok_menipis)}")
    else:
        col3.success("Semua stok aman.")
        
    st.markdown("---")
    
    # --- Charts ---
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Tren Penjualan Harian")
        tren_penjualan = df_penjualan.groupby('Tanggal')['Total_Pendapatan'].sum().reset_index()
        fig_tren = px.line(tren_penjualan, x='Tanggal', y='Total_Pendapatan', title="Total Pendapatan per Hari", 
                           color_discrete_sequence=['#5d4037'])
        fig_tren.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(255,255,255,0.4)', 
            font_color='#3e2723',
            xaxis=dict(gridcolor='rgba(62,39,35,0.2)', zerolinecolor='rgba(62,39,35,0.2)', title_font=dict(color='#3e2723'), tickfont=dict(color='#3e2723')),
            yaxis=dict(gridcolor='rgba(62,39,35,0.2)', zerolinecolor='rgba(62,39,35,0.2)', title_font=dict(color='#3e2723'), tickfont=dict(color='#3e2723')),
            legend=dict(font=dict(color='#3e2723'), title=dict(font=dict(color='#3e2723')))
        )
        st.plotly_chart(fig_tren, use_container_width=True, theme=None)
        
    with c2:
        st.subheader("Status Stok Barang")
        fig_stok = px.bar(df_stok, x='Nama_Barang', y=['Stok_Saat_Ini', 'Batas_Aman'], 
                          barmode='group', title="Stok Saat Ini vs Batas Aman",
                          color_discrete_sequence=['#8d6e63', '#4e342e'])
        fig_stok.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(255,255,255,0.4)', 
            font_color='#3e2723',
            xaxis=dict(gridcolor='rgba(62,39,35,0.2)', zerolinecolor='rgba(62,39,35,0.2)', title_font=dict(color='#3e2723'), tickfont=dict(color='#3e2723')),
            yaxis=dict(gridcolor='rgba(62,39,35,0.2)', zerolinecolor='rgba(62,39,35,0.2)', title_font=dict(color='#3e2723'), tickfont=dict(color='#3e2723')),
            legend=dict(font=dict(color='#3e2723'), title=dict(font=dict(color='#3e2723')))
        )
        st.plotly_chart(fig_stok, use_container_width=True, theme=None)

with tab3:
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    st.header(f"Laporan Bulan Ini ({datetime.now().strftime('%B %Y')})")
    st.markdown("Ringkasan performa penjualan secara *realtime* berdasarkan daftar menu dan harga Anda.")
    
    df_bulan_ini = df_penjualan[(df_penjualan['Tanggal'].dt.month == current_month) & (df_penjualan['Tanggal'].dt.year == current_year)]
    
    if df_bulan_ini.empty:
        st.info("Belum ada data penjualan untuk bulan ini.")
    else:
        total_pendapatan_bulan = df_bulan_ini['Total_Pendapatan'].sum()
        produk_terlaris_bulan = df_bulan_ini.groupby('Nama_Barang')['Terjual'].sum().idxmax()
        
        cb1, cb2 = st.columns(2)
        cb1.metric("Total Pendapatan", f"Rp {total_pendapatan_bulan:,.0f}")
        cb2.metric("Produk Paling Laris", produk_terlaris_bulan)
        
        st.markdown("### Rincian Penjualan per Menu")
        # Gabungkan data penjualan bulan ini dengan info harga dari df_stok
        rincian_bulan = df_bulan_ini.groupby('Nama_Barang').agg({'Terjual': 'sum', 'Total_Pendapatan': 'sum'}).reset_index()
        rincian_lengkap = pd.merge(rincian_bulan, df_stok[['Nama_Barang', 'Kategori', 'Harga_Satuan']], on='Nama_Barang', how='left')
        
        # Format agar rapi
        rincian_lengkap = rincian_lengkap[['Kategori', 'Nama_Barang', 'Harga_Satuan', 'Terjual', 'Total_Pendapatan']]
        rincian_lengkap.columns = ['Kategori', 'Nama Menu', 'Harga Satuan (Rp)', 'Jumlah Terjual', 'Total Pendapatan (Rp)']
        rincian_lengkap = rincian_lengkap.sort_values('Total Pendapatan (Rp)', ascending=False).reset_index(drop=True)
        
        # Tampilkan tabel yang didesain agar warnanya cocok (dark mode / transparent compatible)
        st.dataframe(rincian_lengkap, use_container_width=True, hide_index=True)
        
        tren_bulan_ini = df_bulan_ini.groupby('Tanggal')['Total_Pendapatan'].sum().reset_index()
        fig_bulan = px.line(tren_bulan_ini, x='Tanggal', y='Total_Pendapatan', title="Tren Penjualan Bulan Ini", color_discrete_sequence=['#5d4037'])
        fig_bulan.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(255,255,255,0.4)', 
            font_color='#3e2723',
            xaxis=dict(gridcolor='rgba(62,39,35,0.2)', zerolinecolor='rgba(62,39,35,0.2)', title_font=dict(color='#3e2723'), tickfont=dict(color='#3e2723')),
            yaxis=dict(gridcolor='rgba(62,39,35,0.2)', zerolinecolor='rgba(62,39,35,0.2)', title_font=dict(color='#3e2723'), tickfont=dict(color='#3e2723'))
        )
        st.plotly_chart(fig_bulan, use_container_width=True, theme=None)

with tab2:
    st.header("Tanya Asisten AI")
    st.markdown("Ngobrol dengan AI untuk mendapatkan saran bisnis, prediksi efek cuaca, atau simulasi harga.")
    
    # Mengambil API Key secara rahasia dari file .env (tanpa menampilkan kotak input)
    api_key = os.getenv('GOOGLE_API_KEY')
    
    if api_key:
        # Initialize LLM
        try:
            llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", google_api_key=api_key)
        except Exception as e:
            st.error(f"Gagal memuat LLM: {e}")
            llm = None
            
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []
            
        def render_message(role, content, is_typing=False):
            role_class = "user" if role == "user" else "agent"
            if is_typing:
                content_html = "<div class='typing-container'><div class='typing-dot'></div><div class='typing-dot'></div><div class='typing-dot'></div></div>"
            else:
                content_html = markdown.markdown(content, extensions=['extra', 'nl2br'])
            html = f"<div class='chat-bubble-wrapper {role_class}'><div class='chat-bubble'>{content_html}</div></div>"
            return html
            
        for message in st.session_state.messages:
            st.markdown(render_message(message["role"], message["content"]), unsafe_allow_html=True)

        if prompt := st.chat_input("Contoh: Apa produk yang paling laku? Atau, bagaimana jika saya naikkan harga Kopi Susu 20%?"):
            # Display user message
            st.markdown(render_message("user", prompt), unsafe_allow_html=True)
            st.session_state.messages.append({"role": "user", "content": prompt})

            # Placeholder for agent response
            message_placeholder = st.empty()
            
            if llm:
                # Tampilkan animasi 3 titik berkedip (Typing Indicator)
                message_placeholder.markdown(render_message("assistant", "", is_typing=True), unsafe_allow_html=True)
                
                # Build Context
                ringkasan_penjualan = df_penjualan.groupby('Nama_Barang')['Terjual'].sum().to_string()
                ringkasan_stok = df_stok[['Nama_Barang', 'Stok_Saat_Ini', 'Batas_Aman']].to_string()
                
                # Rekap Bulanan untuk pertanyaan historis
                df_penjualan['Bulan_Tahun'] = df_penjualan['Tanggal'].dt.strftime('%Y-%m (%B)')
                ringkasan_bulanan = df_penjualan.groupby('Bulan_Tahun')['Total_Pendapatan'].sum().to_string()
                
                system_prompt = f"""
                Anda adalah Asisten AI Cerdas untuk pemilik UMKM. Anda bertugas menganalisis data keuangan, penjualan, dan stok barang, serta memberikan saran bisnis.
                
                KONTEKS DATA PENJUALAN KESELURUHAN (1 Tahun Terakhir):
                {ringkasan_penjualan}
                
                KONTEKS DATA PENDAPATAN PER BULAN:
                {ringkasan_bulanan}
                
                KONTEKS STATUS STOK BARANG SAAT INI:
                {ringkasan_stok}
                
                INFORMASI LINGKUNGAN / KONTEKS TAMBAHAN:
                Lokasi Kafe: Kota Solo / Surakarta, Jawa Tengah. Cuaca di Solo saat ini: {get_weather_solo()}. Sesuaikan saran promosi dengan karakteristik cuaca ini jika relevan.
                
                ATURAN MENJAWAB:
                1. Jawab HANYA apa yang ditanyakan secara ringkas dan padat. Jangan bertele-tele.
                2. JANGAN memberikan rekomendasi, analisis stok, atau menyebutkan prediksi cuaca KECUALI jika pengguna secara eksplisit memintanya.
                3. Jika ditanya soal data pendapatan pada bulan tertentu, rujuk pada KONTEKS DATA PENDAPATAN PER BULAN dan sebutkan angkanya secara akurat.
                4. Jawab dengan ramah dan profesional menggunakan bahasa Indonesia.
                5. Jika user menanyakan simulasi 'What-If', gunakan logika bisnismu untuk mensimulasikan dampaknya berdasarkan data.
                6. FORMATTING PENULISAN: Gunakan Markdown yang rapi. Jadikan nama kategori sebagai huruf tebal (contoh: **Kopi & Minuman:**), lalu gunakan bullet points (-) atau nomor urut khusus untuk daftar di bawahnya.
                """
                
                # Prepare messages
                langchain_messages = [SystemMessage(content=system_prompt)]
                for msg in st.session_state.messages:
                    if msg["role"] == "user":
                        langchain_messages.append(HumanMessage(content=msg["content"]))
                        
                try:
                    response = llm.invoke(langchain_messages)
                    raw_answer = response.content
                    
                    # Parser untuk menangani format respons baru dari model 3.5 (List of Dicts)
                    if isinstance(raw_answer, list):
                        extracted_text = []
                        for block in raw_answer:
                            if isinstance(block, dict) and 'text' in block:
                                extracted_text.append(block['text'])
                            elif isinstance(block, str):
                                extracted_text.append(block)
                        answer = "\n".join(extracted_text)
                    else:
                        answer = str(raw_answer)
                        
                except Exception as e:
                    answer = f"Maaf, terjadi kesalahan saat menghubungi Gemini API: {e}"
            else:
                answer = "LLM tidak diinisialisasi. Cek API Key Anda."
                
            message_placeholder.markdown(render_message("assistant", answer), unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": answer})
    else:
        st.info("Silakan masukkan API Key Gemini Anda di atas untuk mengaktifkan asisten AI.")
