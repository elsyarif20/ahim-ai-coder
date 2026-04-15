import streamlit as st
from groq import Groq
import base64

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="AHIM CODE - AI Assistant",
    page_icon="🤖",
    layout="wide"
)

# --- 2. LOGO (SVG) ---
icon_svg_code = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
    <defs>
        <linearGradient id="gradAhim" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#0072FF;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#8A2BE2;stop-opacity:1" />
        </linearGradient>
    </defs>
    <path d="M50 5 L90 27.5 L90 72.5 L50 95 L10 72.5 L10 27.5 Z" fill="#111" stroke="#333" stroke-width="2"/>
    <path d="M50 25 L35 70 L42 70 L45 60 L55 60 L58 70 L65 70 Z" fill="url(#gradAhim)"/>
</svg>
"""
def get_svg_base64(svg_html):
    return base64.b64encode(svg_html.encode('utf-8')).decode('utf-8')
svg_base64 = get_svg_base64(icon_svg_code)

# --- 3. CSS KUSTOM (LIGHT MODE) ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #ffffff; color: #111111; }}
    [data-testid="stSidebar"] {{ background-color: #f8f9fa; border-right: 1px solid #e0e0e0; }}
    .brand-title {{ font-family: 'Poppins', sans-serif; font-weight: 800; background: -webkit-linear-gradient(45deg, #0072FF, #8A2BE2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 24px; text-align: center; }}
    .upgrade-btn {{ background: linear-gradient(45deg, #ff4b4b, #ff7676); color: white !important; font-weight: bold; width: 100%; border: none; padding: 12px; border-radius: 10px; text-align: center; text-decoration: none; display: inline-block; margin: 10px 0; }}
    .stChatMessage {{ background-color: #ffffff; border-radius: 15px; border: 1px solid #eaeaea; box-shadow: 0 2px 5px rgba(0,0,0,0.02); }}
    .stChatMessage[data-testid="stChatMessageUser"] {{ background-color: #f0f7ff; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. INISIALISASI SESSION STATE ---
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown(f"""
        <div style="text-align: center;">
            <img src="data:image/svg+xml;base64,{svg_base64}" width="70">
            <h1 class="brand-title">AHIM CODE</h1>
            <p style="color: #666; font-size: 13px;">BY AHIM DEVELOPER</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()

    # Pilihan Model
    st.markdown("### 🧠 AI Model")
    model_option = st.selectbox(
        "Pilih Model:",
        ("llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"),
        label_visibility="collapsed"
    )

    # TOMBOL PENGATURAN API (POPOVER)
    with st.popover("⚙️ Pengaturan API Key", use_container_width=True):
        st.markdown("### Konfigurasi Groq")
        temp_key = st.text_input("Masukkan API Key:", value=st.session_state.api_key, type="password")
        if st.button("💾 Simpan Key", use_container_width=True):
            st.session_state.api_key = temp_key
            st.success("API Key berhasil disimpan!")
            st.rerun()

    # Status API Key (Visual Feedback)
    if st.session_state.api_key:
        st.caption("✅ API Key Terkonfigurasi")
    else:
        st.caption("❌ API Key Belum Ada")

    st.markdown(
        """<a href="https://console.groq.com/settings/billing" target="_blank" class="upgrade-btn">➕ UPGRADE MODEL</a>""", 
        unsafe_allow_html=True
    )

    st.divider()
    if st.button("🗑️ Hapus Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- 6. AREA UTAMA ---
st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 20px;">
        <img src="data:image/svg+xml;base64,{svg_base64}" width="45">
        <h2 style="margin:0; color: #111;">AHIM CODE Assistant</h2>
    </div>
    """, unsafe_allow_html=True)

# Menampilkan Riwayat Chat
for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else f"data:image/svg+xml;base64,{svg_base64}"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Input Chat
if prompt := st.chat_input("Tulis kode atau pertanyaan Anda..."):
    if not st.session_state.api_key:
        st.error("⚠️ Mohon simpan API Key di menu 'Pengaturan API Key' (Sidebar)!")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        try:
            client = Groq(api_key=st.session_state.api_key)
            with st.chat_message("assistant", avatar=f"data:image/svg+xml;base64,{svg_base64}"):
                resp_placeholder = st.empty()
                full_resp = ""
                
                completion = client.chat.completions.create(
                    model=model_option,
                    messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                    stream=True,
                )

                for chunk in completion:
                    content = chunk.choices[0].delta.content
                    if content:
                        full_resp += content
                        resp_placeholder.markdown(full_resp + "▌")
                resp_placeholder.markdown(full_resp)
            
            st.session_state.messages.append({"role": "assistant", "content": full_resp})

        except Exception as e:
            st.error(f"Terjadi kesalahan: {str(e)}")
