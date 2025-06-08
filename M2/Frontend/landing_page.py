import streamlit as st
import requests

# Page config
st.set_page_config(page_title="Landing Page", layout="centered",)

# Title
st.title("📘 Welcome to My App")

st.markdown("Please choose an option below:")

# Layout with two buttons side by side
sign_in, sign_up = st.columns(2)

with sign_in:
    if st.button("🔐 Sign In"):
        st.session_state.page = "signin"

with sign_up:
    if st.button("📝 Sign Up"):
        st.session_state.page = "signup"


# Handle page routing (simple simulation)
if "page" in st.session_state:
    if st.session_state.page == "signin":
        st.markdown("### 🔐 Sign In Page")

        with st.form("signin_in"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Sign In")

            if submitted:
                # TODO: CALL BACKEND HERE AND CHECK FORM
                st.success("Eingelogget als {TODO}")

    elif st.session_state.page == "signup":
        st.markdown("### 📝 Sign Up Page (TODO)")
        
        with st.form("signin_up"):
            first_name = st.text_input("Vorname")
            last_name = st.text_input("Nachname")
            password = st.text_input("Passwort", type="password")
            confirm_password = st.text_input("Bitte Bestätigen sie das Passwort", type="password")
            email = st.text_input("Email - das wird später zum Loggin benutzt")
            city = st.text_input("Ort")
            street = st.text_input("Straße und Hausnummer")
            zipcode = st.text_input("PLZ")
            submitted = st.form_submit_button("Sign Up")

            if submitted:
                # TODO: CHECK INPUT HERE
                if password != confirm_password:
                    st.error("Das gewählte Passwort stimmt nicht mit dem Bestätigungspasswort überein")
                else:
                    user_data = {
                        "first_name": first_name,
                        "last_name": last_name,
                        "password": password,
                        "email": email,
                        "city": city,
                        "street": street,
                        "zipcode": zipcode,
                    }

                    try:
                        res = requests.post("http://localhost:5000/signup", json=user_data)
                        if res.status_code == 201:
                            st.success("Ihr Account wurde erstellt!")
                        else:
                            st.error(res.json().get("error", "Unbekannter Fehler"))
                    except Exception as e:
                        st.error(f"Verbindung zum Server fehlgeschlagen: {e}")