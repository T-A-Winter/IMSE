import streamlit as st
import requests
import json
from session import switch_backend, SQL_BACKEND_URL, MONGO_BACKEND_URL, ensure_backend_consistency

st.set_page_config(page_title="Admin Panel", layout="centered")

# Check if user is logged in
if "user" not in st.session_state:
    st.warning("Please sign in to access this page.")
    st.stop()

# Ensure backend consistency
ensure_backend_consistency()

st.title("🔧 Admin Panel")
st.subheader("Database Management")

# Backend selection using session management
current_backend = st.session_state.get('backend_name', 'Unknown')
st.write(f"### Current Backend: {current_backend}")

backend_col1, backend_col2 = st.columns(2)

with backend_col1:
    if st.button("Use SQL Backend", type="primary" if current_backend == "SQL" else "secondary"):
        if st.session_state.get('backend_url') != SQL_BACKEND_URL:
            with st.spinner("Switching to SQL Backend..."):
                success, message = switch_backend(SQL_BACKEND_URL)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

with backend_col2:
    if st.button("Use MongoDB Backend", type="primary" if current_backend == "MongoDB" else "secondary"):
        if st.session_state.get('backend_url') != MONGO_BACKEND_URL:
            with st.spinner("Switching to MongoDB Backend..."):
                success, message = switch_backend(MONGO_BACKEND_URL)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

# Migration section
st.write("### Data Migration")

col1, col2 = st.columns(2)

with col1:
    st.write("**SQL → MongoDB**")
    if st.button("Migrate to MongoDB"):
        try:
            response = requests.post(f"{MONGO_BACKEND_URL}/migrate", verify=False)
            if response.status_code == 200:
                st.success("✅ Migration to MongoDB started!")
                st.info("Check the MongoDB backend logs for progress.")
            else:
                st.error(f"❌ Migration failed: {response.text}")
        except Exception as e:
            st.error(f"❌ Error during migration: {str(e)}")

with col2:
    st.write("**MongoDB → SQL**")
    if st.button("Migrate to SQL"):
        try:
            response = requests.post(f"{SQL_BACKEND_URL}/admin/migrate-from-mongo", verify=False)
            if response.status_code == 200:
                st.success("✅ Migration to SQL completed!")
            else:
                st.error(f"❌ Migration failed: {response.text}")
        except Exception as e:
            st.error(f"❌ Error during migration: {str(e)}")

# Database statistics
st.write("### Database Statistics")

try:
    backend_url = st.session_state.get('backend_url', SQL_BACKEND_URL)
    response = requests.get(f"{backend_url}/stats", verify=False)
    
    if response.status_code == 200:
        stats = response.json()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Users", stats.get("users", "N/A"))
        with col2:
            st.metric("Restaurants", stats.get("restaurants", "N/A"))
        with col3:
            st.metric("Dishes", stats.get("dishes", "N/A"))
        with col4:
            st.metric("Orders", stats.get("orders", "N/A"))
    else:
        st.warning("Could not fetch database statistics")
except Exception as e:
    st.warning(f"Could not connect to backend: {str(e)}") 