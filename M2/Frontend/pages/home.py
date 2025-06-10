import streamlit as st
import requests
from streamlit_extras.switch_page_button import switch_page

# Set default backend URL if not already set
if "active_backend" not in st.session_state:
    st.session_state.active_backend = "SQL"
    st.session_state.backend_url = "http://backend:5000"
elif st.session_state.active_backend == "SQL":
    st.session_state.backend_url = "http://backend:5000"
elif st.session_state.active_backend == "MONGO":
    st.session_state.backend_url = "http://mongo-backend:5001"

# Use the backend URL from session state
BASE_URL = st.session_state.backend_url

def check_login():
    if "user" not in st.session_state:
        st.warning("Please sign in to continue")
        st.stop()

# Page configuration
st.set_page_config(page_title="Home", layout="wide")
st.title("🍽️ Restaurants")

# Check if user is logged in
check_login()

# Display user info
st.sidebar.write(f"Welcome, {st.session_state.user['first_name']} {st.session_state.user['last_name']}")
st.sidebar.write(f"Using {st.session_state.active_backend} backend")
if st.sidebar.button("Logout"):
    del st.session_state.user
    switch_page("landing_page")

# Fetch restaurants from backend
try:
    # Try to fetch from backend
    response = requests.get(f"{BASE_URL}/restaurants")
    if response.status_code == 200:
        restaurants = response.json()
    else:
        # Fallback to mock data if backend request fails
        restaurants = [
            {"id": 1, "name": "Pizza Palace", "open_from": "11:00", "open_till": "22:00", 
             "address": "Karlsplatz 13, Vienna, 1040"},
            {"id": 2, "name": "Burger Heaven", "open_from": "10:00", "open_till": "23:00", 
             "address": "Stephansplatz 1, Vienna, 1010"},
            {"id": 3, "name": "Sushi World", "open_from": "12:00", "open_till": "22:00", 
             "address": "Mariahilfer Straße 100, Vienna, 1060"}
        ]
    
    # Display restaurants in a grid
    cols = st.columns(3)
    for i, restaurant in enumerate(restaurants):
        with cols[i % 3]:
            st.subheader(restaurant["name"])
            st.write(f"📍 {restaurant.get('address', 'Address not available')}")
            st.write(f"⏰ {restaurant.get('open_from', 'N/A')} - {restaurant.get('open_till', 'N/A')}")
            if st.button("View Menu", key=f"menu_{restaurant['id']}"):
                # Store the selected restaurant in session state
                st.session_state.selected_restaurant_id = restaurant["id"]
                # Use switch_page instead of experimental_set_query_params
                switch_page("restaurant_menu")
                
except Exception as e:
    st.error(f"Error loading restaurants: {e}") 