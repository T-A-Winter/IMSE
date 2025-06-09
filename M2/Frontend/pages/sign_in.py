import streamlit as st
import requests

BASE_URL = "http://localhost:5000"

st.title("🔐 Sign In")

with st.form("signin_form"):
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Sign In")

    if submitted:
        try:
            res = requests.post(f"{BASE_URL}/signin", json={"email": email, "password": password})
            if res.status_code != 200:
                st.error(res.json().get("error", "Unbekannter Fehler beim Login"))
            else:
                st.session_state.user = res.json()["user"]
                st.success(f"Eingeloggt als {st.session_state.user['first_name']} {st.session_state.user['last_name']}")
                st.session_state.page = "home"
                st.experimental_rerun()
        except Exception as e:
            st.error(f"Verbindung zum Server fehlgeschlagen: {e}")