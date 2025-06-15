import streamlit as st
import requests
import time
from datetime import datetime
from session import SQL_BACKEND_URL, MONGO_BACKEND_URL, check_backend_health, get_available_backends

# Page configuration
st.set_page_config(page_title="Backend Debug", layout="wide")

st.title("🔧 Backend Debug & Diagnostics")
st.write("This page helps diagnose backend connectivity issues")

# Current session state
st.subheader("📊 Current Session State")
col1, col2 = st.columns(2)

with col1:
    st.write("**Backend Configuration:**")
    st.write(f"- Backend URL: `{st.session_state.get('backend_url', 'Not set')}`")
    st.write(f"- Backend Name: `{st.session_state.get('backend_name', 'Not set')}`")
    st.write(f"- Last Switch: `{st.session_state.get('last_backend_switch', 'Never')}`")

with col2:
    st.write("**Session Info:**")
    st.write(f"- User Logged In: `{'Yes' if 'user' in st.session_state else 'No'}`")
    st.write(f"- Cart ID: `{st.session_state.get('cart_id', 'Not set')}`")
    st.write(f"- Initialized: `{st.session_state.get('initialized', False)}`")

# Backend URLs
st.subheader("🌐 Backend URLs")
st.write(f"**SQL Backend:** `{SQL_BACKEND_URL}`")
st.write(f"**MongoDB Backend:** `{MONGO_BACKEND_URL}`")

# Health checks
st.subheader("🏥 Backend Health Checks")

col1, col2 = st.columns(2)

with col1:
    st.write("**SQL Backend Health:**")
    sql_healthy = check_backend_health(SQL_BACKEND_URL)
    if sql_healthy:
        st.success("✅ SQL Backend is healthy")
        try:
            response = requests.get(f"{SQL_BACKEND_URL}/health", timeout=5, verify=False)
            health_data = response.json()
            st.json(health_data)
        except Exception as e:
            st.error(f"Error getting health details: {e}")
    else:
        st.error("❌ SQL Backend is unhealthy")
        
    if st.button("🔄 Test SQL Backend"):
        with st.spinner("Testing SQL backend..."):
            try:
                response = requests.get(f"{SQL_BACKEND_URL}/health", timeout=10, verify=False)
                st.write(f"Status Code: {response.status_code}")
                if response.status_code == 200:
                    st.json(response.json())
                else:
                    st.error(f"HTTPS {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Connection failed: {str(e)}")

with col2:
    st.write("**MongoDB Backend Health:**")
    mongo_healthy = check_backend_health(MONGO_BACKEND_URL)
    if mongo_healthy:
        st.success("✅ MongoDB Backend is healthy")
        try:
            response = requests.get(f"{MONGO_BACKEND_URL}/health", timeout=5, verify=False)
            health_data = response.json()
            st.json(health_data)
        except Exception as e:
            st.error(f"Error getting health details: {e}")
    else:
        st.error("❌ MongoDB Backend is unhealthy")
        
    if st.button("🔄 Test MongoDB Backend"):
        with st.spinner("Testing MongoDB backend..."):
            try:
                response = requests.get(f"{MONGO_BACKEND_URL}/health", timeout=10, verify=False)
                st.write(f"Status Code: {response.status_code}")
                if response.status_code == 200:
                    st.json(response.json())
                else:
                    st.error(f"HTTPS {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Connection failed: {str(e)}")

# Available backends
st.subheader("🔍 Available Backends")
available_backends = get_available_backends()
if available_backends:
    st.success(f"Found {len(available_backends)} available backend(s):")
    for name, url in available_backends:
        st.write(f"- **{name}**: `{url}`")
else:
    st.error("No backends are currently available!")

# Test endpoints
st.subheader("🧪 Test Basic Endpoints")

backend_to_test = st.selectbox(
    "Select backend to test:",
    [SQL_BACKEND_URL, MONGO_BACKEND_URL],
    format_func=lambda x: "SQL Backend" if x == SQL_BACKEND_URL else "MongoDB Backend"
)

endpoints_to_test = [
    "/health",
    "/restaurants", 
    "/stats"
]

if st.button("🚀 Run Endpoint Tests"):
    st.write(f"Testing endpoints on: `{backend_to_test}`")
    
    for endpoint in endpoints_to_test:
        with st.expander(f"Testing {endpoint}"):
            try:
                start_time = time.time()
                response = requests.get(f"{backend_to_test}{endpoint}", timeout=10, verify=False)
                end_time = time.time()
                
                st.write(f"**Status Code:** {response.status_code}")
                st.write(f"**Response Time:** {(end_time - start_time):.2f}s")
                
                if response.status_code == 200:
                    st.success("✅ Success")
                    try:
                        data = response.json()
                        st.json(data)
                    except:
                        st.text(response.text[:500] + "..." if len(response.text) > 500 else response.text)
                else:
                    st.error(f"❌ Failed: HTTPS {response.status_code}")
                    st.text(response.text)
                    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# Manual backend switching
st.subheader("🔄 Manual Backend Control")

col1, col2 = st.columns(2)

with col1:
    if st.button("🔄 Switch to SQL Backend"):
        st.session_state.backend_url = SQL_BACKEND_URL
        st.session_state.backend_name = "SQL"
        st.session_state.last_backend_switch = datetime.now().isoformat()
        st.success("Switched to SQL Backend")
        st.rerun()

with col2:
    if st.button("🔄 Switch to MongoDB Backend"):
        st.session_state.backend_url = MONGO_BACKEND_URL
        st.session_state.backend_name = "MongoDB"
        st.session_state.last_backend_switch = datetime.now().isoformat()
        st.success("Switched to MongoDB Backend")
        st.rerun()

# Clear session
st.subheader("🧹 Session Management")
if st.button("🗑️ Clear Session State"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.success("Session state cleared")
    st.rerun()

# Docker troubleshooting
st.subheader("🐳 Docker Troubleshooting")
st.write("If backends are not available, try these commands:")

st.code("""
# Check container status
docker-compose ps

# Check backend logs
docker-compose logs backend
docker-compose logs mongo-backend

# Restart services
docker-compose restart backend
docker-compose restart mongo-backend

# Rebuild and restart
docker-compose up --build -d
""", language="bash")

# Navigation
st.markdown("---")
if st.button("🏠 Back to Home"):
    from streamlit_extras.switch_page_button import switch_page
    switch_page("home") 