import streamlit as st
from groq import Groq
import base64

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="AHIM CODE - AI Assistant | Powered by Groq",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. ASSET & DESAIN (SVG LOGO) ---
# Logo tetap bernuansa gelap agar kontras dan keren di background putih
icon_svg_code = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
    <defs>
        <linearGradient id="gradAhim" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#00C6FF;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#8A2BE2;stop-opacity:1" />
        </linearGradient>
    </defs>
    <path d="M50 5 L90 27.5 L90 72.5 L50 95 L10 72.5 L10 27.5 Z" fill="#111" stroke="#333" stroke-width="2"/>
    <path d="M50 25 L35 70 L42 70 L45 60 L55 60 L58 70 L65 70 Z" fill="url(#gradAhim)"/>
    <path d="M40 40 Q35 40 35 45 Q35 50 40 50 M60 40 Q65 40 65 45 Q65 50 60 50" stroke="#FFF" stroke-width="2.5" fill="none" opacity="0.8"/>
</svg>
"""

def get_svg_base64(svg_html):
    return base64.b64encode(svg_html.encode('utf-8')).decode('utf-8')

svg_base64 = get_svg_base64(icon_svg_code)

# --- 3. CSS KUSTOM (VERSI TERANG / LIGHT MODE) ---
st.markdown(f"""
    <style>
    /* Tema Dasar Terang */
    .stApp {{ background-color: #ffffff; color: #111111; }}
    [data-testid="stSidebar"] {{ background-color: #f8f9fa; border-right: 1px solid #e0e0e0; padding-top: 20px; }}
    
    /* Logo & Tulisan Sidebar */
    .sidebar-logo-container {{ text-align: center; margin-bottom: 10px; }}
    .brand-title {{ font-family: 'Poppins', sans-serif; font-weight: 800; background: -webkit-linear-gradient(45deg, #0072FF, #8A2BE2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0px; font-size: 24px; }}
    .brand-subtitle {{ color: #555555; font-size: 14px; margin-top: 0px; margin-bottom: 20px; }}
    
    /* Pilihan Model Label */
    .stSelectbox label, .stTextInput label {{ color: #111111 !important; font-weight: 600; }}

    /* Tombol Upgrade (Tetap Merah Mencolok) */
    .upgrade-btn {{ background: linear-gradient(45deg, #ff4b4b, #ff7676); color: white !important; font-weight: bold; width: 100%; border: none; padding: 12px; border-radius: 10px; cursor: pointer; transition: transform 0.2s; text-align: center; text-decoration: none; display: inline-block; margin-top: 10px; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(255,75,75,0.2); }}
    .upgrade-btn:hover {{ transform: scale(1.03); box-shadow: 0 6px 15px rgba(255, 75, 75, 0.4); }}
    
    /* Kotak Input Sidebar */
    .stTextInput>div>div>input {{ background-color: #ffffff; color: #111111; border: 1px solid #cccccc; border-radius: 8px; }}
    
    /* Area Chat Utama */
    .main-header {{ display: flex; align-items: center; gap: 15px; margin-bottom: 25px; color: #111111; }}
    
    /* Bubble Chat Assistant (Putih dengan Shadow) */
    .stChatMessage {{ background-color: #ffffff; border-radius: 15px; border: 1px solid #eaeaea; padding: 15px; color: #111111; box-shadow: 0 2px 10px rgba(0,0,0,0.02); }}
    
    /* Bubble Chat User (Biru Sangat Muda) */
    .stChatMessage[data-testid="stChatMessageUser"] {{ background-color: #f0f7ff; border: 1px solid #dcebfa; }}
    
    /* KOTAK CHAT BAWAH (Terang) */
    [data-testid="stChatInput"] > div {{
        background-color: #ffffff !important;
        border: 1px solid #cccccc !important;
        border-radius: 15px !important;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.03);
    }}
    
    /* Warna teks di dalam kotak ketik */
    [data-testid="stChatInput"] textarea {{ color: #111111 !important; }}
    
    /* Warna teks Streamlit Markdown */
    .stMarkdown p {{ color: #111111; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown(f"""
        <div class="sidebar-logo-container">
            <img src="data:image/svg+xml;base64,{svg_base64}" width="80">
            <h1 class="brand-title">AHIM CODE</h1>
            <p class="brand-subtitle">AHIM DEVELOPER</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()

    st.markdown("### 🧠 Select AI Model")
    model_option = st.selectbox(
        "Pilih Model:",
        ("llama-3.3-70b-versatile", "llama-3.1-8b-instant (Free Tier)", "mixtral-8x7b-32768", "gemma2-9b-it"),
        index=0,
        label_visibility="collapsed"
    )

    st.markdown(
        """
        <a href="https://console.groq.com/settings/billing" target="_blank" class="upgrade-btn">
            ➕ TAMBAH / UPGRADE MODEL
        </a>
        """, 
        unsafe_allow_html=True
    )

    st.markdown("### 🔑 API AUTHENTICATION")
    api_key = st.text_input("Groq API Key:", type="password", placeholder="Masukkan API Key Anda...")

    st.divider()

    st.markdown("### Login with:")
    st.markdown("""
        <button style="width:100%; border-radius:8px; border:1px solid #ccc; background-color:#fff; color:#333; padding:10px; font-weight:bold; cursor:pointer; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
            <img src="https://upload.wikimedia.org/wikipedia/commons/c/c1/Google_\"G\"_logo.svg" width="18" style="margin-right:8px; vertical-align:middle;">
            Google Sign-In
        </button>
        """, unsafe_allow_html=True)
    
    st.write("") # Spacer
    if st.button("Email Address", use_container_width=True):
        st.info("Fitur login email akan segera hadir.")

    st.divider()
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- 5. AREA UTAMA ---
st.markdown(f"""
    <div class="main-header">
        <img src="data:image/svg+xml;base64,{svg_base64}" width="50">
        <div>
            <h2 style="margin:0; color: #111;">AHIM CODE - AI Assistant</h2>
            <p style="margin:0; color:#555;">Powered by Groq | Status: <span style="color:#28a745; font-weight:bold;">Active</span></p>
        </div>
    </div>
    """, unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user", avatar="👤"): # Avatar user saya ganti jadi siluet agar lebih pas di light mode
            st.markdown(message["content"])
    else:
        with st.chat_message("assistant", avatar=f"data:image/svg+xml;base64,{svg_base64}"):
            st.markdown(message["content"])

# KOTAK INPUT CHAT
if prompt := st.chat_input("Tulis pesan atau paste kode (Shift + Enter untuk baris baru)..."):
    if not api_key:
        st.error("⚠️ Silakan masukkan Groq API Key di menu Pengaturan (Sidebar)!")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        try:
            client = Groq(api_key=api_key)
            with st.chat_message("assistant", avatar=f"data:image/svg+xml;base64,{svg_base64}"):
                response_placeholder = st.empty()
                full_response = ""
                cleaned_model = model_option.split(' ')[0]

                completion = client.chat.completions.create(
                    model=cleaned_model,
                    messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                    stream=True,
                )

                for chunk in completion:
                    content = chunk.choices[0].delta.content
                    if content:
                        full_response += content
                        response_placeholder.markdown(full_response + "▌")
                
                response_placeholder.markdown(full_response)
            
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"Error: {str(e)}")