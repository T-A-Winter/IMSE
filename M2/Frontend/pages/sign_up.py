import streamlit as st
import requests

BASE_URL = "http://localhost:5000"

st.title("📝 Sign Up")

with st.form("signup_form"):
    first_name = st.text_input("Vorname")
    last_name = st.text_input("Nachname")
    password = st.text_input("Passwort", type="password")
    confirm_password = st.text_input("Bitte bestätigen Sie das Passwort", type="password")
    email = st.text_input("Email (Login)")
    city = st.text_input("Ort")
    street = st.text_input("Straße und Hausnummer")
    zipcode = st.text_input("PLZ")

    submitted = st.form_submit_button("Sign Up")

    if submitted:
        if password != confirm_password:
            st.error("Das Passwort stimmt nicht mit dem Bestätigungspasswort überein.")
        else:
            user_data = {
                "first_name": first_name,
                "last_name": last_name,
                "password": password,
                "confirm_password": confirm_password,
                "email": email,
                "city": city,
                "street": street,
                "zipcode": zipcode,
            }

            try:
                res = requests.post(f"{BASE_URL}/signup", json=user_data)
                if res.status_code == 201:
                    st.success("Ihr Account wurde erfolgreich erstellt!")
                else:
                    st.error(res.json().get("error", "Unbekannter Fehler"))
            except Exception as e:
                st.error(f"Verbindung zum Server fehlgeschlagen: {e}")
