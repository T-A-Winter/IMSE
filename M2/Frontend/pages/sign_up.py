import streamlit as st
import requests
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

st.title("📝 Sign Up")

# Initialize signup success state if not exists
if "signup_success" not in st.session_state:
    st.session_state.signup_success = False
    st.session_state.signup_error = None

# Show success message outside the form
if st.session_state.signup_success:
    st.success("Ihr Account wurde erfolgreich erstellt!")
    if st.button("Go to Sign In"):
        st.session_state.signup_success = False
        switch_page("sign_in")

# Show error message outside the form
if st.session_state.signup_error:
    st.error(st.session_state.signup_error)
    # Clear error after displaying it
    st.session_state.signup_error = None

# Only show the form if signup was not successful
if not st.session_state.signup_success:
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
            if not all([first_name, last_name, password, confirm_password, email]):
                st.session_state.signup_error = "Bitte füllen Sie alle Pflichtfelder aus."
                st.experimental_rerun()
            elif password != confirm_password:
                st.session_state.signup_error = "Das Passwort stimmt nicht mit dem Bestätigungspasswort überein."
                st.experimental_rerun()
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
                    res = requests.post(f"{BASE_URL}/signup", json=user_data, verify=False)
                    if res.status_code == 201:
                        st.session_state.signup_success = True
                        st.experimental_rerun()
                    elif res.status_code == 409:
                        st.session_state.signup_error = "Diese E-Mail-Adresse ist bereits registriert."
                        st.experimental_rerun()
                    else:
                        try:
                            error_msg = res.json().get("error", "Unbekannter Fehler")
                            st.session_state.signup_error = error_msg
                        except:
                            st.session_state.signup_error = f"Fehler beim Erstellen des Accounts: Status Code {res.status_code}"
                        st.experimental_rerun()
                except Exception as e:
                    st.session_state.signup_error = f"Verbindung zum Server fehlgeschlagen: {str(e)}"
                    st.experimental_rerun()

# Add a button to go back to the landing page
if not st.session_state.signup_success:
    if st.button("Back to Home"):
        switch_page("landing_page")
