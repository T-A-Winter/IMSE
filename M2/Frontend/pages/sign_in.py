import streamlit as st
import requests
import time
from streamlit_extras.switch_page_button import switch_page

# Set default backend URL if not already set
if "active_backend" not in st.session_state:
    st.session_state.active_backend = "SQL"
    st.session_state.backend_url = "https://backend:5000"
elif st.session_state.active_backend == "SQL":
    st.session_state.backend_url = "https://backend:5000"
elif st.session_state.active_backend == "MONGO":
    st.session_state.backend_url = "https://mongo-backend:5001"

# Use the backend URL from session state
BASE_URL = st.session_state.backend_url

st.title("🔐 Sign In")

# Initialize signin error state if not exists
if "signin_error" not in st.session_state:
    st.session_state.signin_error = None

# Initialize signin success state if not exists
if "signin_success" not in st.session_state:
    st.session_state.signin_success = False

# Show error message outside the form
if st.session_state.signin_error:
    st.error(st.session_state.signin_error)
    # Clear error after displaying it
    st.session_state.signin_error = None

# Show success message and redirect
if st.session_state.signin_success:
    st.success(f"Eingeloggt als {st.session_state.user['first_name']} {st.session_state.user['last_name']}")
    # Wait briefly before redirecting
    time.sleep(1)
    st.session_state.signin_success = False
    switch_page("home")

with st.form("signin_form"):
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Sign In")

    if submitted:
        if not email or not password:
            st.session_state.signin_error = "Email und Passwort sind erforderlich."
            st.experimental_rerun()
        else:
            try:
                res = requests.post(f"{BASE_URL}/signin", json={"email": email, "password": password}, verify=False)
                if res.status_code == 200:
                    st.session_state.user = res.json()["user"]
                    st.session_state.signin_success = True
                    st.experimental_rerun()
                elif res.status_code == 401:
                    st.session_state.signin_error = "Falsches Passwort."
                    st.experimental_rerun()
                elif res.status_code == 404:
                    st.session_state.signin_error = "Benutzer nicht gefunden."
                    st.experimental_rerun()
                else:
                    try:
                        error_msg = res.json().get("error", "Unbekannter Fehler beim Login")
                        st.session_state.signin_error = error_msg
                    except:
                        st.session_state.signin_error = f"Fehler beim Login: Status Code {res.status_code}"
                    st.experimental_rerun()
            except Exception as e:
                st.session_state.signin_error = f"Verbindung zum Server fehlgeschlagen: {str(e)}"
                st.experimental_rerun()

# Add buttons to go to sign up page or back to home
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("Create Account"):
        switch_page("sign_up")
with col2:
    if st.button("Back to Home"):
        switch_page("landing_page")