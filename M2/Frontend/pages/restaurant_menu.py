import streamlit as st
import requests
import json
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

# Check if user is logged in
if "user" not in st.session_state:
    st.warning("Please sign in to continue")
    switch_page("sign_in")
    st.stop()

# Check if restaurant ID is in session state
if "selected_restaurant_id" not in st.session_state:
    st.warning("No restaurant selected")
    switch_page("home")
    st.stop()

restaurant_id = st.session_state.selected_restaurant_id

# Page configuration
st.set_page_config(page_title="Restaurant Menu", layout="wide")

# Display user info in sidebar
st.sidebar.write(f"Welcome, {st.session_state.user['first_name']} {st.session_state.user['last_name']}")
st.sidebar.write(f"Using {st.session_state.active_backend} backend")
if st.sidebar.button("Back to Restaurants"):
    # Clear cart when going back to restaurants
    if "cart" in st.session_state:
        del st.session_state.cart
    switch_page("home")
if st.sidebar.button("Logout"):
    # Clear cart and user when logging out
    if "cart" in st.session_state:
        del st.session_state.cart
    del st.session_state.user
    switch_page("landing_page")

# Fetch restaurant details
try:
    response = requests.get(f"{BASE_URL}/restaurants/{restaurant_id}")
    restaurant = response.json()
    st.title(f"🍽️ {restaurant['name']}")
    st.write(f"📍 {restaurant.get('street', '')}, {restaurant.get('city', '')}, {restaurant.get('zipcode', '')}")
    st.write(f"⏰ {restaurant.get('open_from', 'N/A')} - {restaurant.get('open_till', 'N/A')}")
except Exception as e:
    st.error(f"Error loading restaurant: {e}")
    st.stop()

# Fetch menu items
try:
    response = requests.get(f"{BASE_URL}/restaurants/{restaurant_id}/dishes")
    dishes = response.json()
except Exception as e:
    st.error(f"Error loading menu: {e}")
    dishes = []

# Create a function to create a new cart
def create_new_cart(restaurant_id):
    try:
        # Create the cart
        response = requests.post(
            f"{BASE_URL}/carts",
            json={"restaurant_id": int(restaurant_id)}
        )
        
        # Check response
        if response.status_code == 201:
            cart_data = response.json()
            return {
                "id": cart_data["id"],
                "items": [],
                "total": 0.0
            }
        else:
            st.error(f"Failed to create cart. Status: {response.status_code}")
            return {"id": None, "items": [], "total": 0.0}
    except Exception as e:
        st.error(f"Error creating cart: {str(e)}")
        return {"id": None, "items": [], "total": 0.0}

# Initialize or get cart from session state
if "cart" not in st.session_state or st.session_state.cart["id"] is None:
    st.session_state.cart = create_new_cart(restaurant_id)

# Add a button to manually create a new cart if needed
if st.session_state.cart["id"] is None:
    if st.button("Try creating cart again"):
        st.session_state.cart = create_new_cart(restaurant_id)

# Function to add item to cart
def add_to_cart(dish_id, dish_name, price, quantity):
    if quantity <= 0:
        st.warning("Please select a quantity greater than 0")
        return
    
    if st.session_state.cart["id"] is None:
        st.error("Could not create cart. Please try again.")
        return
    
    try:
        response = requests.post(
            f"{BASE_URL}/carts/{st.session_state.cart['id']}/items",
            json={"dish_id": int(dish_id), "quantity": int(quantity)}
        )
        
        if response.status_code == 201:
            # Update local cart state
            item_data = response.json()
            
            # Check if item already exists in cart
            item_exists = False
            for item in st.session_state.cart["items"]:
                if item["dish_id"] == dish_id:
                    item["quantity"] += quantity
                    item["total_price"] = item_data["total_price"]
                    item_exists = True
                    break
            
            if not item_exists:
                st.session_state.cart["items"].append({
                    "dish_id": dish_id,
                    "dish_name": dish_name,
                    "quantity": quantity,
                    "price": price,
                    "total_price": price * quantity
                })
            
            # Update cart total
            st.session_state.cart["total"] = sum(item["total_price"] for item in st.session_state.cart["items"])
            
            st.success(f"Added {quantity} x {dish_name} to cart")
            # Use session state to trigger rerun instead of st.rerun()
            st.session_state.item_added = True
        else:
            st.error(f"Error adding to cart: {response.text}")
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
            json={"user_id": st.session_state.user["id"]}
        )
        
        if response.status_code == 200:
            # Set checkout success flag instead of using st.rerun()
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