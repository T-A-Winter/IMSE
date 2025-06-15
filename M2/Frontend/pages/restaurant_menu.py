import streamlit as st
import requests
import json
from streamlit_extras.switch_page_button import switch_page
from session import ensure_backend_consistency, check_backend_health, handle_backend_error, init_session

# Page configuration - MUST be first Streamlit command
st.set_page_config(page_title="Restaurant Menu", layout="wide")

# Initialize session
init_session()

# Ensure backend consistency
ensure_backend_consistency()

# Use the backend URL from session state
BASE_URL = st.session_state.backend_url

# Check if user is logged in
if "user" not in st.session_state:
    st.warning("Please sign in to continue")
    switch_page("sign_in")
    st.stop()

# Check if restaurant is selected - handle both old and new formats
restaurant = None
restaurant_id = None

if "selected_restaurant" in st.session_state:
    restaurant = st.session_state.selected_restaurant
    restaurant_id = restaurant["id"]
elif "selected_restaurant_id" in st.session_state:
    restaurant_id = st.session_state.selected_restaurant_id
    # Fetch restaurant details
    try:
        response = requests.get(f"{BASE_URL}/restaurants/{restaurant_id}", verify=False)
        if response.status_code == 200:
            restaurant = response.json()
        else:
            st.warning("Restaurant not found")
            switch_page("home")
            st.stop()
    except Exception as e:
        st.error(f"Error loading restaurant: {e}")
        switch_page("home")
        st.stop()
else:
    st.warning("No restaurant selected")
    switch_page("home")
    st.stop()

# Display user info in sidebar
st.sidebar.write(f"Welcome, {st.session_state.user['first_name']} {st.session_state.user['last_name']}")
st.sidebar.write(f"Backend: {st.session_state.get('backend_name', 'Unknown')}")

# Navigation buttons
if st.sidebar.button("🏠 Back to Restaurants"):
    # Clear cart when going back to restaurants
    if "cart" in st.session_state:
        del st.session_state.cart
    switch_page("home")
if st.sidebar.button("📦 Track My Orders"):
    switch_page("orders")
if st.sidebar.button("Logout"):
    # Clear cart and user when logging out
    if "cart" in st.session_state:
        del st.session_state.cart
    del st.session_state.user
    switch_page("landing_page")

# Display restaurant info
st.title(f"🍽️ {restaurant['name']}")
st.write(f"📍 {restaurant.get('street', '')}, {restaurant.get('city', '')} {restaurant.get('zipcode', '')}")
st.write(f"⏰ {restaurant.get('open_from', 'N/A')} - {restaurant.get('open_till', 'N/A')}")

# Check backend health
if not check_backend_health():
    handle_backend_error("Backend is not responding")
    st.stop()

# Fetch menu items with error handling
try:
    response = requests.get(f"{BASE_URL}/restaurants/{restaurant_id}/dishes", timeout=10, verify=False)
    if response.status_code == 200:
        dishes = response.json()
    else:
        handle_backend_error(f"Failed to fetch menu: {response.status_code}")
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

# Create a function to create a new cart
def create_new_cart(restaurant_id):
    try:
        # Create the cart
        response = requests.post(
            f"{BASE_URL}/carts",
            json={"restaurant_id": int(restaurant_id)},
            timeout=10,
            verify=False
        )
        
        # Check response
        if response.status_code == 201:
            cart_data = response.json()
            return {
                "id": cart_data["id"],
                "items": [],
                "total": 0.0,
                "backend": st.session_state.get('backend_name', 'Unknown'),
                "restaurant_id": int(restaurant_id)
            }
        else:
            st.error(f"Failed to create cart. Status: {response.status_code}")
            return {"id": None, "items": [], "total": 0.0, "backend": None, "restaurant_id": int(restaurant_id)}
    except Exception as e:
        st.error(f"Error creating cart: {str(e)}")
        return {"id": None, "items": [], "total": 0.0, "backend": None, "restaurant_id": int(restaurant_id)}

# Function to migrate cart between backends
def migrate_cart_to_current_backend(old_cart):
    """Migrate cart from one backend to another"""
    if not old_cart or not old_cart.get("items"):
        return create_new_cart(restaurant_id)
    
    try:
        # Create new cart in current backend
        new_cart = create_new_cart(old_cart.get("restaurant_id", restaurant_id))
        
        if new_cart["id"] is None:
            st.error("Failed to create cart in current backend")
            return old_cart
        
        # Migrate items one by one
        migrated_items = []
        for item in old_cart["items"]:
            try:
                response = requests.post(
                    f"{BASE_URL}/carts/{new_cart['id']}/items",
                    json={"dish_id": int(item["dish_id"]), "quantity": int(item["quantity"])},
                    timeout=10,
                    verify=False
                )
                
                if response.status_code == 201:
                    migrated_items.append(item)
                else:
                    st.warning(f"Failed to migrate item: {item['dish_name']}")
            except Exception as e:
                st.warning(f"Error migrating item {item['dish_name']}: {str(e)}")
        
        # Update cart with migrated items
        new_cart["items"] = migrated_items
        new_cart["total"] = sum(item["total_price"] for item in migrated_items)
        new_cart["backend"] = st.session_state.get('backend_name', 'Unknown')
        
        if migrated_items:
            st.success(f"✅ Migrated {len(migrated_items)} items to {st.session_state.get('backend_name', 'Unknown')} backend")
        
        return new_cart
        
    except Exception as e:
        st.error(f"Error during cart migration: {str(e)}")
        return create_new_cart(restaurant_id)

# Function to sync cart with backend
def sync_cart_with_backend(cart):
    """Ensure cart exists in current backend and sync items"""
    if not cart or cart["id"] is None:
        return create_new_cart(restaurant_id)
    
    try:
        # Try to get cart from current backend
        response = requests.get(f"{BASE_URL}/carts/{cart['id']}", timeout=10, verify=False)
        
        if response.status_code == 200:
            # Cart exists, sync items
            backend_cart = response.json()
            backend_items = backend_cart.get("items", [])
            
            # Update local cart with backend data
            cart["items"] = []
            cart["total"] = 0.0
            
            for item in backend_items:
                # Get dish details for display
                try:
                    dish_response = requests.get(f"{BASE_URL}/restaurants/{restaurant_id}/dishes", timeout=5, verify=False)
                    if dish_response.status_code == 200:
                        dishes = dish_response.json()
                        dish = next((d for d in dishes if d["id"] == item.get("dish_id")), None)
                        if dish:
                            cart["items"].append({
                                "dish_id": item["dish_id"],
                                "dish_name": dish["name"],
                                "quantity": item["quantity"],
                                "price": dish["price"],
                                "total_price": item["total_price"]
                            })
                            cart["total"] += item["total_price"]
                except:
                    pass
            
            cart["backend"] = st.session_state.get('backend_name', 'Unknown')
            return cart
        else:
            # Cart doesn't exist in current backend, create new one
            return create_new_cart(restaurant_id)
            
    except Exception as e:
        st.warning(f"Error syncing cart: {str(e)}")
        return create_new_cart(restaurant_id)

# Initialize or get cart from session state with backend switching support
if "cart" not in st.session_state:
    st.session_state.cart = create_new_cart(restaurant_id)
else:
    current_cart = st.session_state.cart
    
    # Check if backend has changed
    current_backend = st.session_state.get('backend_name', 'Unknown')
    if current_cart.get("backend") != current_backend:
        st.info(f"🔄 Switching from {current_cart.get('backend', 'Unknown')} to {current_backend} backend...")
        
        # Try to migrate cart to new backend
        st.session_state.cart = migrate_cart_to_current_backend(current_cart)
    else:
        # Same backend, just sync to ensure consistency
        st.session_state.cart = sync_cart_with_backend(current_cart)

# Add a button to manually create a new cart if needed
if st.session_state.cart["id"] is None:
    st.error("⚠️ Cart creation failed. This might be due to backend connectivity issues.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Retry Cart Creation"):
            st.session_state.cart = create_new_cart(restaurant_id)
            st.experimental_rerun()
    with col2:
        if st.button("🏠 Go Back to Home"):
            switch_page("home")

# Function to add item to cart with enhanced error handling
def add_to_cart(dish_id, dish_name, price, quantity):
    if quantity <= 0:
        st.warning("Please select a quantity greater than 0")
        return
    
    if st.session_state.cart["id"] is None:
        st.error("Could not create cart. Please try again or switch backends.")
        return
    
    try:
        response = requests.post(
            f"{BASE_URL}/carts/{st.session_state.cart['id']}/items",
            json={"dish_id": int(dish_id), "quantity": int(quantity)},
            verify=False
        )
        
        if response.status_code == 201:
            # Update local cart state
            item_data = response.json()
            
            # Check if item already exists in cart
            item_exists = False
            for item in st.session_state.cart["items"]:
                if item["dish_id"] == dish_id:
                    item["quantity"] += quantity
                    item["total_price"] = item_data.get("total_price", price * (item["quantity"]))
                    item_exists = True
                    break
            
            if not item_exists:
                st.session_state.cart["items"].append({
                    "dish_id": dish_id,
                    "dish_name": dish_name,
                    "quantity": quantity,
                    "price": price,
                    "total_price": item_data.get("total_price", price * quantity)
                })
            
            # Update cart total
            st.session_state.cart["total"] = sum(item["total_price"] for item in st.session_state.cart["items"])
            
            st.success(f"Added {quantity} x {dish_name} to cart")
            # Use session state to trigger rerun instead of st.rerun()
            st.session_state.item_added = True
        elif response.status_code == 404:
            st.error("Cart not found. Creating a new cart...")
            st.session_state.cart = create_new_cart(restaurant_id)
            st.experimental_rerun()
        else:
            st.error(f"Error adding to cart: {response.text}")
    except requests.exceptions.ConnectionError:
        st.error(f"Connection error to {st.session_state.active_backend} backend. Please check backend status.")
    except Exception as e:
        st.error(f"Error adding to cart: {e}")

# Set item_added flag if not exists
if "item_added" not in st.session_state:
    st.session_state.item_added = False

# Check if item was added and reload the page
if st.session_state.item_added:
    st.session_state.item_added = False
    st.experimental_rerun()

# Function to checkout
def checkout():
    if not st.session_state.cart["items"]:
        st.warning("Your cart is empty")
        return
    
    try:
        response = requests.post(
            f"{BASE_URL}/carts/{st.session_state.cart['id']}/checkout",
            json={"user_id": st.session_state.user["id"]},
            verify=False
        )
        
        if response.status_code == 200:
            order_data = response.json()
            
            # Show order confirmation with delivery details
            st.success("🎉 Order placed successfully!")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Order ID", f"#{order_data.get('order_id', 'N/A')}")
            with col2:
                st.metric("Total Amount", f"€{order_data.get('total', 0):.2f}")
            with col3:
                if order_data.get('is_prime_order'):
                    st.success("🌟 Prime Order - Free Delivery!")
                else:
                    st.info(f"Delivery Fee: €{order_data.get('delivery_fee', 3.99):.2f}")
            
            # Delivery information with Prime benefits highlight
            st.write("**🚚 Delivery Information:**")
            st.write(f"**Supplier:** {order_data.get('supplier', 'Assigning...')}")
            if order_data.get('estimated_delivery'):
                st.write(f"**Estimated Delivery:** {order_data['estimated_delivery']}")
            
            # Highlight Prime benefits
            if order_data.get('is_prime_order'):
                st.success("""
                🌟 **Prime Benefits Applied:**
                - ✅ FREE delivery (saved €3.99)
                - ✅ Priority processing
                - ✅ Advanced tracking available
                - ✅ Quality guarantee included
                """)
            else:
                st.info("""
                💡 **Upgrade to Prime to enjoy:**
                - 🚚 Free delivery on all orders
                - ⚡ Priority processing
                - 📱 Advanced tracking
                - 🛡️ Quality guarantee
                """)
            
            st.info("📱 Track your order in real-time on the Orders page!")
            
            # Set checkout success flag
            st.session_state.checkout_success = True
            # Clear cart after successful checkout
            st.session_state.cart = {"id": None, "items": [], "total": 0.0}
        else:
            st.error(f"Error during checkout: {response.text}")
    except Exception as e:
        st.error(f"Error during checkout: {e}")

# Set checkout_success flag if not exists
if "checkout_success" not in st.session_state:
    st.session_state.checkout_success = False

# Check if checkout was successful and show message
if st.session_state.checkout_success:
    st.success("Order placed successfully!")
    st.session_state.checkout_success = False
    # Create a new cart
    st.session_state.cart = create_new_cart(restaurant_id)

# Display menu items
st.header("Menu")
menu_cols = st.columns(3)

for i, dish in enumerate(dishes):
    with menu_cols[i % 3]:
        st.subheader(dish["name"])
        st.write(f"💰 ${dish['price']:.2f}")
        
        quantity = st.number_input(
            f"Quantity for {dish['name']}", 
            min_value=0, 
            value=0, 
            step=1,
            key=f"qty_{dish['id']}"
        )
        
        st.button(
            "Add to Cart", 
            key=f"add_{dish['id']}", 
            on_click=add_to_cart, 
            args=(dish["id"], dish["name"], dish["price"], quantity)
        )
        st.divider()

# Display cart
st.sidebar.header("Your Cart")
if not st.session_state.cart["items"]:
    st.sidebar.write("Your cart is empty")
else:
    for item in st.session_state.cart["items"]:
        st.sidebar.write(f"{item['quantity']} x {item['dish_name']} - ${item['total_price']:.2f}")
    
    st.sidebar.write(f"**Total: ${st.session_state.cart['total']:.2f}**")
    st.sidebar.button("Checkout", on_click=checkout) 