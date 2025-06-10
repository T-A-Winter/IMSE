import streamlit as st
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(page_title="Welcome", layout="centered")

st.title("📘 Welcome to My App")
st.markdown("Bitte wählen Sie eine Option:")

sign_in, sign_up = st.columns(2)

with sign_in:
    if st.button("🔐 Sign In"):
        switch_page("sign_in")  # Filename without `.py`

with sign_up:
    if st.button("📝 Sign Up"):
        switch_page("sign_up")

# Optionally redirect if already logged in
if "user" in st.session_state:
    st.success(f"Eingeloggt als {st.session_state.user['first_name']}")
    
    # Add admin button for logged-in users
    if st.button("🔧 Admin Panel"):
        switch_page("admin")