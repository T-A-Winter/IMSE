from typing import Union, Dict, Any
import streamlit as st
import requests
import time
from datetime import datetime

class Session():
    def __init__(self, user: Dict[str, Any]):
        self.user = user   
        
# Backend URLs
SQL_BACKEND_URL = "https://backend:5000"
MONGO_BACKEND_URL = "https://mongo-backend:5001"

def check_backend_health(backend_url=None):
    """Check if the specified backend is healthy"""
    if backend_url is None:
        backend_url = st.session_state.get('backend_url', SQL_BACKEND_URL)
    
    try:
        response = requests.get(f"{backend_url}/health", timeout=5, verify=False)
        return response.status_code == 200
    except:
        return False

def get_available_backends():
    """Get list of available backends"""
    backends = []
    
    if check_backend_health(SQL_BACKEND_URL):
        backends.append(("SQL Backend", SQL_BACKEND_URL))
    
    if check_backend_health(MONGO_BACKEND_URL):
        backends.append(("MongoDB Backend", MONGO_BACKEND_URL))
    
    return backends

def switch_backend(new_backend_url):
    """Switch to a different backend with proper migration and error handling"""
    current_backend = st.session_state.get('backend_url')
    
    if current_backend == new_backend_url:
        return True, "Already using this backend"
    
    # Check if new backend is available
    if not check_backend_health(new_backend_url):
        return False, "Target backend is not available"
    
    try:
        # Trigger migration before switching
        if current_backend == SQL_BACKEND_URL and new_backend_url == MONGO_BACKEND_URL:
            # Migrating from SQL to MongoDB
            migration_response = requests.post(f"{SQL_BACKEND_URL}/admin/migrate", timeout=60, verify=False)
            if migration_response.status_code != 200:
                return False, f"Migration to MongoDB failed: {migration_response.text}"
            # Wait a bit for migration to complete
            time.sleep(3)
        
        elif current_backend == MONGO_BACKEND_URL and new_backend_url == SQL_BACKEND_URL:
            # Migrating from MongoDB to SQL
            migration_response = requests.post(f"{SQL_BACKEND_URL}/admin/migrate-from-mongo", timeout=60, verify=False)
            if migration_response.status_code != 200:
                return False, f"Migration to SQL failed: {migration_response.text}"
            # Wait a bit for migration to complete
            time.sleep(3)
        
        # Update session state
        st.session_state.backend_url = new_backend_url
        st.session_state.backend_name = "SQL" if new_backend_url == SQL_BACKEND_URL else "MongoDB"
        st.session_state.last_backend_switch = datetime.now().isoformat()
        
        # Clear ALL cached data to force refresh from new backend
        keys_to_clear = [
            'cart_id', 'cart_items', 'selected_restaurant', 
            'restaurants', 'dishes', 'orders', 'prime_status',
            'user_orders', 'payment_history', 'stats'
        ]
        
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        
        # Force a page refresh to reload data from new backend
        st.rerun()
        
        return True, f"Successfully switched to {st.session_state.backend_name} backend"
        
    except requests.exceptions.Timeout:
        return False, "Migration timed out - backend switch failed"
    except Exception as e:
        return False, f"Backend switch failed: {str(e)}"

def ensure_backend_consistency():
    """Ensure backend consistency and handle fallbacks"""
    # Initialize backend if not set
    if 'backend_url' not in st.session_state or 'backend_name' not in st.session_state:
        available_backends = get_available_backends()
        if available_backends:
            # Use the first available backend
            backend_name, backend_url = available_backends[0]
            st.session_state.backend_url = backend_url
            st.session_state.backend_name = backend_name.split()[0]  # "SQL" or "MongoDB"
            st.session_state.last_backend_switch = datetime.now().isoformat()
        else:
            # Try with default URLs even if health check fails
            st.session_state.backend_url = SQL_BACKEND_URL
            st.session_state.backend_name = "SQL"
            st.warning("⚠️ Backend health check failed, using default SQL backend")
    
    # Check if current backend is still healthy
    current_backend = st.session_state.backend_url
    if not check_backend_health(current_backend):
        # Try to switch to an available backend
        available_backends = get_available_backends()
        if available_backends:
            # Find a different backend
            for name, url in available_backends:
                if url != current_backend:
                    st.warning(f"Current backend is down. Switching to {name}...")
                    success, message = switch_backend(url)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(f"Failed to switch backend: {message}")
                    break
        else:
            st.error("⚠️ All backends appear to be unavailable. Please check your Docker containers.")
            # Don't stop the app, let it continue with the current backend URL

def handle_backend_error(error_message):
    """Handle backend errors gracefully"""
    st.error(f"Backend Error: {error_message}")
    
    # Try to switch to an alternative backend
    current_backend = st.session_state.get('backend_url')
    available_backends = get_available_backends()
    
    for name, url in available_backends:
        if url != current_backend:
            st.info(f"Attempting to switch to {name}...")
            success, message = switch_backend(url)
            if success:
                st.success(f"Switched to {name}. Please try again.")
                time.sleep(2)
                st.rerun()
                return
            else:
                st.warning(f"Failed to switch to {name}: {message}")
    
    st.error("No alternative backends available. Please contact support.")

def get_or_create_cart(user_id, restaurant_id):
    """Get or create cart with proper error handling across backends"""
    backend_url = st.session_state.backend_url
    
    try:
        # First, try to get existing cart
        if 'cart_id' in st.session_state:
            cart_response = requests.get(f"{backend_url}/carts/{st.session_state.cart_id}", verify=False)
            if cart_response.status_code == 200:
                cart_data = cart_response.json()
                # Verify cart belongs to correct restaurant
                if cart_data.get('restaurant_id') == restaurant_id:
                    return st.session_state.cart_id, "Retrieved existing cart"
        
        # Create new cart
        cart_data = {
            "user_id": user_id,
            "restaurant_id": restaurant_id
        }
        
        response = requests.post(f"{backend_url}/carts", json=cart_data, verify=False)
        if response.status_code == 201:
            cart_info = response.json()
            cart_id = cart_info.get('cart_id') or cart_info.get('id')
            st.session_state.cart_id = cart_id
            return cart_id, "Created new cart"
        else:
            return None, f"Failed to create cart: {response.status_code}"
            
    except Exception as e:
        return None, f"Cart operation failed: {str(e)}"

def sync_cart_across_backends(cart_id):
    """Synchronize cart across both backends"""
    try:
        # Get cart from current backend
        current_backend = st.session_state.backend_url
        response = requests.get(f"{current_backend}/carts/{cart_id}", verify=False)
        
        if response.status_code == 200:
            cart_data = response.json()
            
            # Sync to other backend
            other_backend = MONGO_BACKEND_URL if current_backend == SQL_BACKEND_URL else SQL_BACKEND_URL
            
            if check_backend_health(other_backend):
                sync_response = requests.post(f"{other_backend}/admin/sync-cart", json=cart_data, verify=False)
                return sync_response.status_code in [200, 201]
        
        return False
        
    except Exception as e:
        st.warning(f"Cart sync failed: {str(e)}")
        return False

def validate_user_session():
    """Validate user session across backend switches"""
    if 'user' not in st.session_state:
        return False
    
    try:
        user_id = st.session_state.user['id']
        backend_url = st.session_state.backend_url
        
        # Try to fetch user from current backend
        response = requests.get(f"{backend_url}/users/{user_id}", verify=False)
        if response.status_code == 200:
            # Update user data if needed
            user_data = response.json()
            st.session_state.user.update(user_data)
            return True
        else:
            # User not found in current backend, try to sync
            if 'user' in st.session_state:
                other_backend = MONGO_BACKEND_URL if backend_url == SQL_BACKEND_URL else SQL_BACKEND_URL
                sync_response = requests.post(f"{backend_url}/admin/sync-user", json=st.session_state.user, verify=False)
                return sync_response.status_code in [200, 201]
            
        return False
        
    except Exception as e:
        st.warning(f"User session validation failed: {str(e)}")
        return False

def get_backend_status():
    """Get status of both backends"""
    sql_status = check_backend_health(SQL_BACKEND_URL)
    mongo_status = check_backend_health(MONGO_BACKEND_URL)
    
    return {
        "sql": {
            "url": SQL_BACKEND_URL,
            "healthy": sql_status,
            "name": "SQL Backend"
        },
        "mongo": {
            "url": MONGO_BACKEND_URL,
            "healthy": mongo_status,
            "name": "MongoDB Backend"
        }
    }

def display_backend_selector():
    """Display backend selector in sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔧 Backend Settings")
    
    # Show current backend
    current_backend = st.session_state.get('backend_name', 'Unknown')
    st.sidebar.info(f"Current: {current_backend}")
    
    # Get backend status
    status = get_backend_status()
    
    # Display status indicators
    for backend_key, backend_info in status.items():
        status_icon = "🟢" if backend_info["healthy"] else "🔴"
        st.sidebar.write(f"{status_icon} {backend_info['name']}")
    
    # Backend switching buttons
    available_backends = get_available_backends()
    
    if len(available_backends) > 1:
        st.sidebar.write("**Switch Backend:**")
        
        for name, url in available_backends:
            if url != st.session_state.get('backend_url'):
                if st.sidebar.button(f"Switch to {name}"):
                    with st.spinner(f"Switching to {name}..."):
                        success, message = switch_backend(url)
                        if success:
                            st.success(message)
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(message)
    
    # Migration status
    if st.sidebar.button("🔄 Force Sync"):
        with st.spinner("Synchronizing data..."):
            try:
                current_url = st.session_state.backend_url
                if current_url == SQL_BACKEND_URL:
                    response = requests.post(f"{SQL_BACKEND_URL}/admin/migrate", verify=False)
                else:
                    response = requests.post(f"{SQL_BACKEND_URL}/admin/migrate-from-mongo", verify=False)
                
                if response.status_code == 200:
                    st.success("Data synchronized successfully!")
                else:
                    st.error("Synchronization failed!")
            except Exception as e:
                st.error(f"Sync error: {str(e)}")

# Initialize session state
def init_session():
    """Initialize session state with proper defaults"""
    if 'initialized' not in st.session_state:
        ensure_backend_consistency()
        st.session_state.initialized = True
        