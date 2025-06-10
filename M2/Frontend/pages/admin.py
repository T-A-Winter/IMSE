import streamlit as st
import requests
import json

st.set_page_config(page_title="Admin Panel", layout="centered")

# Check if user is logged in
if "user" not in st.session_state:
    st.warning("Please sign in to access this page.")
    st.stop()

# Backend URLs
SQL_BACKEND_URL = "http://backend:5000"
MONGO_BACKEND_URL = "http://mongo-backend:5001"

# Set default backend if not already set
if "active_backend" not in st.session_state:
    st.session_state.active_backend = "SQL"

st.title("🔧 Admin Panel")
st.subheader("Database Management")

# Backend selection
st.write("### Current Backend: " + st.session_state.active_backend)
backend_col1, backend_col2 = st.columns(2)

with backend_col1:
    if st.button("Use SQL Backend", type="primary" if st.session_state.active_backend == "SQL" else "secondary"):
        st.session_state.active_backend = "SQL"
        st.session_state.backend_url = SQL_BACKEND_URL
        st.rerun()

with backend_col2:
    if st.button("Use MongoDB Backend", type="primary" if st.session_state.active_backend == "MONGO" else "secondary"):
        st.session_state.active_backend = "MONGO"
        st.session_state.backend_url = MONGO_BACKEND_URL
        st.rerun()

# Migration section
st.write("### Data Migration")
st.write("Transfer data from SQL to MongoDB database")

if st.button("Start Migration"):
    try:
        response = requests.post(f"{MONGO_BACKEND_URL}/migrate")
        if response.status_code == 200:
            st.success("Migration completed successfully!")
        else:
            st.error(f"Migration failed with status code: {response.status_code}")
            st.error(response.text)
    except Exception as e:
        st.error(f"Error during migration: {str(e)}")

# Database statistics
st.write("### Database Statistics")

try:
    if st.session_state.active_backend == "SQL":
        response = requests.get(f"{SQL_BACKEND_URL}/stats")
    else:
        response = requests.get(f"{MONGO_BACKEND_URL}/stats")
    
    if response.status_code == 200:
        stats = response.json()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Users", stats.get("users", "N/A"))
        with col2:
            st.metric("Restaurants", stats.get("restaurants", "N/A"))
        with col3:
            st.metric("Orders", stats.get("carts", "N/A"))
    else:
        st.warning("Could not fetch database statistics")
except Exception as e:
    st.warning(f"Could not connect to backend: {str(e)}") 