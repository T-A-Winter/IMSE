import streamlit as st
import requests
from streamlit_extras.switch_page_button import switch_page

# Page configuration - MUST be first Streamlit command
st.set_page_config(page_title="Prime Activation", layout="centered")

# Set default backend URL
if "active_backend" not in st.session_state:
    st.session_state.active_backend = "SQL"
    st.session_state.backend_url = "http://backend:5000"
elif st.session_state.active_backend == "SQL":
    st.session_state.backend_url = "http://backend:5000"
elif st.session_state.active_backend == "MONGO":
    st.session_state.backend_url = "http://mongo-backend:5001"

BASE_URL = st.session_state.backend_url

# PRECONDITION: Check if user is logged in (addressing M1 feedback)
if "user" not in st.session_state:
    st.warning("Please sign in to access Prime activation")
    switch_page("sign_in")
    st.stop()

st.title("🌟 Activate Prime Membership")
st.write("**Use Case:** Prime aktivieren und Bestellen")

# Check current Prime status
try:
    user_id = st.session_state.user.get('id')
    if not user_id:
        st.error("❌ User ID not found in session. Please sign in again.")
        if st.button("Go to Sign In"):
            switch_page("sign_in")
        st.stop()
    
    response = requests.get(f"{BASE_URL}/users/{user_id}/prime/status")
    
    if response.status_code == 200:
        prime_status = response.json()
        
        if prime_status["is_prime"]:
            st.success("🎉 You are already a Prime member!")
            st.write(f"✅ Free delivery: {'Yes' if prime_status['free_delivery'] else 'No'}")
            st.write(f"💰 Monthly fee: €{prime_status['fee']}")
            
            # POSTCONDITION: User is Prime member and in Member table
            st.write("**Postconditions met:**")
            st.write(f"- ✅ User is Prime member: {prime_status['is_prime']}")
            st.write(f"- ✅ User is in Member table: {prime_status['is_member']}")
            st.write(f"- ✅ User has free delivery: {prime_status['free_delivery']}")
            
            if st.button("Continue Shopping with Prime Benefits"):
                switch_page("home")
            st.stop()
    elif response.status_code == 404:
        st.error("❌ User not found in the current backend database!")
        st.warning("**This happens when you switch between SQL and MongoDB backends.**")
        
        st.write("**To fix this issue, you have several options:**")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Option 1: Import Test Data**")
            st.write("This will create sample users including your account")
            if st.button("🏠 Go to Home to Import Data", key="import_data"):
                switch_page("home")
        
        with col2:
            st.write("**Option 2: Sign Up Again**")
            st.write("Create your account in the current backend")
            if st.button("📝 Go to Sign Up", key="sign_up"):
                del st.session_state.user  # Clear current session
                switch_page("sign_up")
        
        st.write("---")
        st.info("💡 **Why this happens:** When you switch from SQL to MongoDB (or vice versa), your user account exists only in the previous backend. You need to either import test data or create the account in the current backend.")
        st.stop()
    else:
        st.error(f"Could not check Prime status. Status code: {response.status_code}")
        st.write("**This might be a backend connectivity issue.**")
        if st.button("🔄 Try Again"):
            st.rerun()
        st.stop()
        
except Exception as e:
    st.error(f"Error checking Prime status: {e}")
    st.write("**This might be a connection issue with the backend.**")
    if st.button("🔄 Try Again"):
        st.rerun()
    st.stop()

# Prime Advantages Section
st.markdown("---")
st.subheader("🌟 Prime Membership Advantages")

# Create columns for advantages
adv_col1, adv_col2 = st.columns(2)

with adv_col1:
    st.markdown("""
    ### 🚚 **Delivery Benefits**
    - ✅ **FREE delivery** on ALL orders (save €3.99 per order)
    - ✅ **Priority delivery** - faster processing
    - ✅ **No minimum order** requirement for free delivery
    - ✅ **Weather protection** - delivery guaranteed even in bad weather
    """)
    
    st.markdown("""
    ### 💰 **Financial Benefits**
    - ✅ **Monthly savings** - Average €15.96/month on delivery fees
    - ✅ **Exclusive discounts** up to 20% on select restaurants
    - ✅ **Birthday special** - Free delivery for the entire birthday month
    - ✅ **Cashback rewards** - 2% back on all orders over €25
    """)

with adv_col2:
    st.markdown("""
    ### 🎯 **Exclusive Features**
    - ✅ **Early access** to new restaurants and menu items
    - ✅ **Prime-only deals** and flash sales
    - ✅ **Advanced order tracking** with live GPS
    - ✅ **Priority customer support** - dedicated Prime hotline
    """)
    
    st.markdown("""
    ### 🏆 **Premium Experience**
    - ✅ **Special packaging** for Prime orders
    - ✅ **Quality guarantee** - 100% satisfaction or refund
    - ✅ **Flexible scheduling** - order up to 7 days in advance
    - ✅ **Group ordering** - coordinate orders with friends/family
    """)

# Cost comparison
st.markdown("---")
st.subheader("💡 Cost Comparison")

comp_col1, comp_col2, comp_col3 = st.columns(3)

with comp_col1:
    st.metric(
        label="Regular User (4 orders/month)",
        value="€15.96",
        delta="Delivery fees",
        delta_color="normal"
    )

with comp_col2:
    st.metric(
        label="Prime Member",
        value="€9.99",
        delta="Monthly fee",
        delta_color="inverse"
    )

with comp_col3:
    st.metric(
        label="Monthly Savings",
        value="€5.97",
        delta="+ exclusive discounts",
        delta_color="inverse"
    )

st.info("💡 **Break-even point:** Just 3 orders per month and you're already saving money!")

# Usage statistics
st.markdown("---")
st.subheader("📊 Prime Member Statistics")

stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)

with stat_col1:
    st.metric("Average Orders/Month", "8.2", "↑ 65% vs Regular")

with stat_col2:
    st.metric("Average Savings/Month", "€18.50", "↑ Delivery + Discounts")

with stat_col3:
    st.metric("Customer Satisfaction", "98.5%", "↑ 12% vs Regular")

with stat_col4:
    st.metric("Delivery Time", "28 min", "↓ 15% faster")

# Testimonials
st.markdown("---")
st.subheader("💬 What Prime Members Say")

test_col1, test_col2 = st.columns(2)

with test_col1:
    st.markdown("""
    > *"Prime has completely changed how I order food. The free delivery and priority service make it so convenient!"*
    > 
    > **- Sarah M., Prime member since 2023**
    """)

with test_col2:
    st.markdown("""
    > *"I save over €20 every month with Prime. The exclusive discounts and free delivery are amazing!"*
    > 
    > **- Michael K., Prime member since 2022**
    """)

st.markdown("---")

# Main Flow Implementation (addressing M1 feedback)
st.header("Activate Your Prime Membership")
st.write("**Main Flow:**")
st.write("1. ✅ User selects Prime option")
st.write("2. 🔄 User creates subscription")
st.write("3. 🔄 User is marked as Member")
st.write("4. 🔄 User can then order with free delivery")

with st.form("prime_activation_form"):
    st.write("By clicking 'Activate Prime', you agree to:")
    st.write("- Monthly subscription fee of €9.99")
    st.write("- Automatic renewal until cancelled")
    st.write("- Terms and conditions of Prime membership")
    
    fee = st.number_input("Monthly Fee (€)", value=9.99, disabled=True)
    
    submitted = st.form_submit_button("🌟 Activate Prime Membership", type="primary")

# Handle form submission outside the form
if submitted:
    try:
        user_id = st.session_state.user.get('id')
        if not user_id:
            st.error("❌ User ID not found in session. Cannot activate Prime.")
            st.stop()
        
        with st.spinner("Activating Prime membership..."):
            response = requests.post(
                f"{BASE_URL}/users/{user_id}/prime/activate",
                json={"fee": fee}
            )
        
        if response.status_code == 201:
            st.success("🎉 Prime membership activated successfully!")
            st.balloons()
            
            # Update user session to reflect Prime status
            st.session_state.user["is_prime"] = True
            
            st.write("**Postconditions achieved:**")
            st.write("✅ User is Prime member and in Member table")
            st.write("✅ User has no delivery fee for future orders")
            
            st.write("You can now enjoy:")
            st.write("✅ Free delivery on all orders")
            st.write("✅ Priority customer support")
            st.write("✅ Exclusive member deals")
            
            # Button moved outside form
            st.session_state.prime_activated = True
                
        elif response.status_code == 409:
            st.warning("You are already a Prime member!")
        elif response.status_code == 404:
            st.error("❌ User not found in the current backend!")
            st.warning("**This happens when you switch between SQL and MongoDB backends.**")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🏠 Import Test Data", key="activate_import"):
                    switch_page("home")
            with col2:
                if st.button("📝 Sign Up Again", key="activate_signup"):
                    del st.session_state.user
                    switch_page("sign_up")
        else:
            st.error(f"Failed to activate Prime: {response.text}")
            st.write("Please try again or contact support if the problem persists.")
            
    except Exception as e:
        st.error(f"Error activating Prime: {e}")
        st.write("**This might be a connection issue with the backend.**")
        if st.button("🔄 Retry Activation"):
            st.rerun()

# Show navigation button outside form
if st.session_state.get("prime_activated", False):
    if st.button("Start Shopping with Prime Benefits"):
        st.session_state.prime_activated = False  # Reset flag
        switch_page("home")

# Navigation
st.write("---")
if st.button("← Back to Home"):
    switch_page("home") 