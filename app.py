import streamlit as st
from supabase import create_client
from groq import Groq
import uuid, hashlib, re, io
from datetime import datetime
from auth_utils import handle_login
from research_utils import *

st.set_page_config(page_title="Ahim Devpad v6.8", layout="wide")
url, key = st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

if "user" not in st.session_state: st.session_state.user = None
if not st.session_state.user:
    handle_login(supabase)
    st.stop()

# Load Data
db_data = supabase.table("user_data").select("*").eq("email", st.session_state.user.email).single().execute().data
user_api_key = db_data.get("groq_api_key", "")
chat_history = db_data.get("chat_history", {}) or {}

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = list(chat_history.keys())[0] if chat_history else str(uuid.uuid4())
cur_id = st.session_state.current_chat_id

# SIDEBAR (Fitur 9: Chat Management + Info)
with st.sidebar:
    st.title("⚙️ Ahim Devpad")
    if st.button("🚪 Logout"):
        supabase.auth.sign_out(); st.session_state.user = None; st.rerun()
    with st.expander("🔑 Pengaturan & Info"):
        new_k = st.text_input("Groq Key", value=user_api_key, type="password")
        if st.button("Simpan"):
            supabase.table("user_data").update({"groq_api_key": new_k}).eq("email", st.session_state.user.email).execute(); st.rerun()
        st.markdown(f"**Pembuat:** Liyas Syarifudin, M.Pd.\n**Tahun:** 2026")
    
    if st.button("➕ Chat Baru", use_container_width=True):
        st.session_state.current_chat_id = str(uuid.uuid4()); st.rerun()
    
    st.markdown("### 🕒 Riwayat Chat")
    for cid, cdata in sorted(chat_history.items(), key=lambda x: x[1].get('timestamp',''), reverse=True):
        if st.button(f"💬 {cdata.get('title','')[:20]}", key=cid, use_container_width=True):
            st.session_state.current_chat_id = cid; st.rerun()

# CHAT AREA (Fitur 5 & 6: Export & Sheet)
current_chat = chat_history.get(cur_id, {"messages": []})
for m in current_chat["messages"]:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if m["role"] == "assistant":
            h = hashlib.md5(m["content"].encode()).hexdigest()[:8]
            c1, c2, c3, c4, c5 = st.columns([1,1,1,1,2])
            c1.download_button("📄 TXT", m["content"].encode(), f"{h}.txt", key=f"t{h}")
            c2.download_button("🟦 Word", export_docx_pro(m["content"]), f"{h}.docx", key=f"w{h}")
            c3.download_button("🟥 PDF", export_pdf_pro(m["content"]), f"{h}.pdf", key=f"p{h}")
            if c4.button("🔊", key=f"v{h}"):
                audio = speak_text(m["content"])
                if audio: st.audio(audio, format='audio/mp3')
            df = parse_markdown_table(m["content"])
            if df is not None:
                c5.download_button("🟢 Copy to Sheet", export_excel_pro(df), f"data_{h}.xlsx", key=f"x{h}")

# INPUT (Fitur 2, 3, 7, 8: Search, 1000 kata, OCR, Voice)
prompt = st.chat_input("Cari, Analisis, atau Tulis 1000 kata...", accept_audio=True)
if prompt:
    client = Groq(api_key=user_api_key)
    u_text = prompt.text if not prompt.audio else client.audio.transcriptions.create(file=("i.wav", prompt.audio.read()), model="whisper-large-v3-turbo", response_format="text")
    
    if u_text:
        is_long = any(x in u_text.lower() for x in ["1000 kata", "panjang", "detail"])
        needs_search = any(x in u_text.lower() for x in ["cari", "google", "referensi"])
        
        web_data = search_web(u_text) if needs_search else ""
        sys_msg = "Kamu Ahim AI, asisten riset buatan Liyas Syarifudin, M.Pd. Gunakan bahasa manusiawi."
        final_p = f"Referensi Web: {web_data}\n\n{u_text}" if web_data else u_text
        if is_long: final_p += " (Tulis minimal 1000 kata mendetail)."

        chat_history[cur_id]["messages"].append({"role": "user", "content": u_text})
        with st.chat_message("user"): st.markdown(u_text)

        with st.chat_message("assistant"):
            ph, full = st.empty(), ""
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role":"system","content":sys_msg}, *[{"role":m["role"],"content":m["content"]} for m in chat_history[cur_id]["messages"][:-1]], {"role":"user","content":final_p}],
                temperature=0.7, max_tokens=8192, stream=True
            )
            for chunk in stream:
                if (content := chunk.choices[0].delta.content):
                    full += content; ph.markdown(full + "▌")
            ph.markdown(full)
        
        chat_history[cur_id]["messages"].append({"role": "assistant", "content": full})
        chat_history[cur_id]["timestamp"] = str(datetime.now())
        supabase.table("user_data").update({"chat_history": chat_history}).eq("email", st.session_state.user.email).execute()
        st.rerun()
