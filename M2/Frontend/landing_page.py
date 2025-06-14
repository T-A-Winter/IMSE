import streamlit as st
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(page_title="Welcome", layout="centered")

st.title("🍽️ Welcome to Food Delivery App")
st.markdown("Your favorite restaurants, delivered to your door!")

# Check if user is logged in
if "user" in st.session_state:
    # User is logged in - show welcome message and navigation
    st.success(f"Welcome back, {st.session_state.user['first_name']} {st.session_state.user['last_name']}! 👋")
    
    # Show user's Prime status
    try:
        import requests
        backend_url = st.session_state.get("backend_url", "http://backend:5000")
        prime_response = requests.get(f"{backend_url}/users/{st.session_state.user['id']}/prime/status")
        
        if prime_response.status_code == 200:
            prime_data = prime_response.json()
            if prime_data.get("free_delivery"):
                st.info("🌟 **Prime Member** - Enjoy free delivery on all orders!")
            else:
                st.info("💡 **Tip:** Upgrade to Prime for free delivery and exclusive benefits!")
        else:
            st.info("💡 **Tip:** Upgrade to Prime for free delivery and exclusive benefits!")
    except:
        pass
    
    st.markdown("---")
    st.subheader("🚀 Quick Actions")
    
    # Navigation buttons for logged-in users
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🏠 Browse Restaurants", use_container_width=True):
            switch_page("home")
    
    with col2:
        if st.button("📦 My Orders", use_container_width=True):
            switch_page("orders")
    
    with col3:
        if st.button("🌟 Prime Benefits", use_container_width=True):
            switch_page("prime_activation")
    
    st.markdown("---")
    
    # Additional options
    col4, col5, col6 = st.columns(3)
    
    with col4:
        if st.button("🔧 Admin Panel", use_container_width=True):
            switch_page("admin")
    
    with col5:
        if st.button("📊 Prime Management", use_container_width=True):
            switch_page("prime_management")
    
    with col6:
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            # Clear session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.success("Logged out successfully!")
            st.rerun()

else:
    # User is not logged in - show signin/signup options
    st.markdown("### 🔐 Please sign in to continue")
    st.markdown("Access thousands of restaurants and enjoy fast delivery!")
    
    # Features showcase
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🍕 Wide Selection**
        - 1000+ restaurants
        - All cuisines
        - Local favorites
        """)
    
    with col2:
        st.markdown("""
        **🚚 Fast Delivery**
        - 30-45 min delivery
        - Real-time tracking
        - Professional drivers
        """)
    
    with col3:
        st.markdown("""
        **🌟 Prime Benefits**
        - Free delivery
        - Exclusive deals
        - Priority support
        """)
    
    st.markdown("---")
    
    # Authentication buttons
    sign_in, sign_up = st.columns(2)
    
    with sign_in:
        if st.button("🔐 Sign In", use_container_width=True, type="primary"):
            switch_page("sign_in")
    
    with sign_up:
        if st.button("📝 Sign Up", use_container_width=True):
            switch_page("sign_up")
    
    st.markdown("---")
    st.markdown("*New to our platform? Sign up to get started with exclusive offers!*")