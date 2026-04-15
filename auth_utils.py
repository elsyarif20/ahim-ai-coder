import streamlit as st

def handle_login(supabase):
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        st.markdown("<h1 style='text-align:center;'>AHIM DEVPAD</h1>", unsafe_allow_html=True)
        t1, t2 = st.tabs(["🔐 Login", "📝 Daftar Akun"])
        with t1:
            with st.form("login"):
                e, p = st.text_input("Email"), st.text_input("Password", type="password")
                if st.form_submit_button("Masuk Sekarang", use_container_width=True, type="primary"):
                    try:
                        res = supabase.auth.sign_in_with_password({"email": e, "password": p})
                        if res.user: st.session_state.user = res.user; st.rerun()
                    except: st.error("Email atau Password salah!")
        with t2:
            with st.form("signup"):
                ne = st.text_input("Email Baru")
                np = st.text_input("Password Baru (Min 6 Karakter)", type="password")
                if st.form_submit_button("Daftar Sekarang", use_container_width=True):
                    try:
                        supabase.auth.sign_up({"email": ne, "password": np})
                        supabase.table("user_data").insert({"email": ne, "groq_api_key": "", "chat_history": {}}).execute()
                        st.success("Akun berhasil dibuat! Silakan Login.")
                    except Exception as ex: st.error(f"Gagal: {ex}")
