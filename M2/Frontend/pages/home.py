import streamlit as st
import requests
from streamlit_extras.switch_page_button import switch_page
from session import ensure_backend_consistency, check_backend_health, handle_backend_error, display_backend_selector, init_session

# Page configuration 
st.set_page_config(page_title="Food Delivery App", layout="wide")

# Initialize session
init_session()

# Ensure backend consistency
ensure_backend_consistency()

# Use the backend URL from session state
BASE_URL = st.session_state.backend_url

# Check if user is logged in
if "user" not in st.session_state:
    st.warning("Please sign in to continue")
    st.stop()

st.title("🍽️ Food Delivery App")
st.write(f"**Current Backend:** {st.session_state.get('backend_name', 'Unknown')}")

# Add manual refresh button for debugging
col1, col2 = st.columns([3, 1])
with col2:
    if st.button("🔄 Refresh Data"):
        # Clear cached data
        keys_to_clear = ['restaurants', 'dishes', 'stats']
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

# Display user info
st.sidebar.write(f"Welcome, {st.session_state.user['first_name']} {st.session_state.user['last_name']}")

# Display backend selector
display_backend_selector()

# Enhanced Prime status display
st.sidebar.markdown("---")
st.sidebar.subheader("🌟 Prime Status")
try:
    prime_response = requests.get(f"{BASE_URL}/users/{st.session_state.user['id']}/prime/status", verify=False)
    if prime_response.status_code == 200:
        prime_data = prime_response.json()
        if prime_data["is_prime"]:
            st.sidebar.success("🌟 **Prime Member**")
            st.sidebar.write("✅ Free delivery on all orders")
            st.sidebar.write("✅ Priority processing")
            st.sidebar.write("✅ Exclusive discounts")
            st.sidebar.write("✅ Advanced tracking")
            
            # Show savings
            try:
                orders_response = requests.get(f"{BASE_URL}/users/{st.session_state.user['id']}/orders", verify=False)
                if orders_response.status_code == 200:
                    orders = orders_response.json()
                    prime_orders = [o for o in orders if o.get('was_prime_order')]
                    total_saved = len(prime_orders) * 3.99
                    if total_saved > 0:
                        st.sidebar.metric("Total Saved", f"€{total_saved:.2f}", "Delivery fees")
            except:
                pass
                
            if st.sidebar.button("📊 View Prime Report"):
                switch_page("prime_report")
            if st.sidebar.button("⚙️ Manage Prime"):
                switch_page("prime_management")
        else:
            st.sidebar.warning("💡 **Not a Prime Member**")
            st.sidebar.write("❌ Paying €3.99 delivery per order")
            st.sidebar.write("❌ Standard processing")
            st.sidebar.write("❌ Missing exclusive deals")
            
            # Calculate potential savings
            try:
                orders_response = requests.get(f"{BASE_URL}/users/{st.session_state.user['id']}/orders", verify=False)
                if orders_response.status_code == 200:
                    orders = orders_response.json()
                    total_orders = len(orders)
                    potential_savings = total_orders * 3.99
                    if potential_savings > 0:
                        st.sidebar.metric("Could Have Saved", f"€{potential_savings:.2f}", "With Prime")
            except:
                pass
                
            if st.sidebar.button("🌟 Upgrade to Prime"):
                switch_page("prime_activation")
    else:
        st.sidebar.info("💡 **Upgrade to Prime**")
        st.sidebar.write("🚚 Free delivery on all orders")
        st.sidebar.write("⚡ Priority processing")
        st.sidebar.write("🎯 Exclusive discounts")
        if st.sidebar.button("🌟 Get Prime Benefits"):
            switch_page("prime_activation")
except:
    st.sidebar.info("💡 **Upgrade to Prime for amazing benefits!**")
    if st.sidebar.button("🌟 Learn More"):
        switch_page("prime_activation")

# Admin functions (if user is admin or for testing)
st.sidebar.write("---")
st.sidebar.subheader("🔧 Admin Functions")

if st.sidebar.button("📊 Import Test Data"):
    with st.spinner("Importing randomized data... This may take a few minutes."):
        try:
            import_response = requests.post(f"{BASE_URL}/admin/import-data", verify=False)
            if import_response.status_code == 200:
                st.sidebar.success("✅ Data import completed!")
                st.sidebar.info("Database has been populated with randomized test data")
                st.rerun()
            else:
                st.sidebar.error(f"❌ Data import failed: {import_response.text}")
        except Exception as e:
            st.sidebar.error(f"❌ Error during data import: {e}")

if st.sidebar.button("🔄 Migrate to MongoDB"):
    with st.spinner("Migrating data to MongoDB..."):
        try:
            migrate_response = requests.post(f"{BASE_URL}/admin/migrate", verify=False)
            if migrate_response.status_code == 200:
                st.sidebar.success("✅ Migration completed!")
                st.sidebar.info("Data has been migrated to MongoDB")
            else:
                st.sidebar.error(f"❌ Migration failed: {migrate_response.text}")
        except Exception as e:
            st.sidebar.error(f"❌ Error during migration: {e}")

if st.sidebar.button("🔄 Migrate from MongoDB"):
    with st.spinner("Migrating data from MongoDB to SQL..."):
        try:
            migrate_response = requests.post(f"{BASE_URL}/admin/migrate-from-mongo", verify=False)
            if migrate_response.status_code == 200:
                st.sidebar.success("✅ Migration completed!")
                st.sidebar.info("Data has been migrated from MongoDB to SQL")
            else:
                st.sidebar.error(f"❌ Migration failed: {migrate_response.text}")
        except Exception as e:
            st.sidebar.error(f"❌ Error during migration: {e}")

# Navigation buttons
if st.sidebar.button("📦 My Orders"):
    switch_page("orders")
if st.sidebar.button("Logout"):
    del st.session_state.user
    switch_page("landing_page")

# Check backend health
if not check_backend_health():
    handle_backend_error("Backend is not responding")
    st.stop()

# Fetch restaurants with error handling
try:
    response = requests.get(f"{BASE_URL}/restaurants", timeout=10, verify=False)
    if response.status_code == 200:
        restaurants = response.json()
    else:
        handle_backend_error(f"Failed to fetch restaurants: {response.status_code}")
        st.stop()
except requests.exceptions.ConnectionError:
    handle_backend_error("Connection error - backend may be down")
    st.stop()
except requests.exceptions.Timeout:
    handle_backend_error("Request timeout - backend is slow to respond")
    st.stop()
except Exception as e:
    handle_backend_error(f"Unexpected error: {str(e)}")
    st.stop()

if restaurants:
    st.subheader("🏪 Available Restaurants")
    
    # Create columns for restaurant cards
    cols = st.columns(3)
    
    for idx, restaurant in enumerate(restaurants):
        col = cols[idx % 3]
        
        with col:
            with st.container():
                st.markdown(f"### {restaurant['name']}")
                st.write(f"📍 {restaurant.get('street', '')}, {restaurant.get('city', '')} {restaurant.get('zipcode', '')}")
                st.write(f"🕒 {restaurant.get('open_from', 'N/A')} - {restaurant.get('open_till', 'N/A')}")
                
                if st.button(f"View Menu", key=f"menu_{restaurant['id']}"):
                    st.session_state.selected_restaurant = restaurant
                    switch_page("restaurant_menu")
                
                st.divider()
else:
    st.info("No restaurants available at the moment.")

# Display app statistics
st.subheader("📊 App Statistics")

try:
    stats_response = requests.get(f"{BASE_URL}/stats", verify=False)
    if stats_response.status_code == 200:
        stats = stats_response.json()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Restaurants", stats.get("total_restaurants", 0))
        
        with col2:
            st.metric("Total Dishes", stats.get("total_dishes", 0))
        
        with col3:
            st.metric("Total Users", stats.get("total_users", 0))
        
        with col4:
            st.metric("Total Orders", stats.get("total_orders", 0))
            
except Exception as e:
    st.warning(f"Could not load statistics: {str(e)}")

# Footer
st.markdown("---")
st.markdown("*Food Delivery App - IMSE M2 Project*")
st.markdown(f"*Backend: {st.session_state.get('backend_name', 'Unknown')} | Status: {'🟢 Healthy' if check_backend_health() else '🔴 Unhealthy'}*") 