import streamlit as st
import requests
import pandas as pd
from streamlit_extras.switch_page_button import switch_page
from datetime import datetime, timedelta
import time
from session import ensure_backend_consistency, check_backend_health, handle_backend_error

# Page configuration - MUST be first Streamlit command
st.set_page_config(page_title="My Orders", layout="wide")

# Ensure backend consistency
ensure_backend_consistency()

# Use the backend URL from session state
BASE_URL = st.session_state.backend_url

# Check if user is logged in
if "user" not in st.session_state:
    st.warning("Please sign in to continue")
    st.stop()

# Display user info and navigation
st.sidebar.write(f"Welcome, {st.session_state.user['first_name']} {st.session_state.user['last_name']}")

# Check Prime status and add Prime features
try:
    prime_response = requests.get(f"{BASE_URL}/users/{st.session_state.user['id']}/prime/status")
    if prime_response.status_code == 200:
        prime_data = prime_response.json()
        if prime_data["is_prime"]:
            st.sidebar.success("🌟 Prime Member")
            st.sidebar.write("✅ Free Delivery Active")
            if st.sidebar.button("📊 View Prime Report"):
                switch_page("prime_report")
        else:
            st.sidebar.info("Regular Member")
            if st.sidebar.button("🌟 Activate Prime"):
                switch_page("prime_activation")
except:
    pass

# Navigation buttons
if st.sidebar.button("🏠 Home"):
    switch_page("home")
if st.sidebar.button("📊 Prime Report"):
    switch_page("prime_report")
if st.sidebar.button("Logout"):
    del st.session_state.user
    switch_page("landing_page")

# Auto-refresh toggle
auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh (5s)", value=False)
if auto_refresh:
    time.sleep(5)
    st.rerun()

def get_status_color(status):
    """Get color for order status"""
    colors = {
        "open": "🟡",
        "in preparation": "🟠", 
        "in delivery": "🔵",
        "delivered": "🟢"
    }
    return colors.get(status.lower(), "⚪")

def get_delivery_progress(status):
    """Get progress percentage for delivery"""
    progress = {
        "open": 10,
        "in preparation": 30,
        "in delivery": 70,
        "delivered": 100
    }
    return progress.get(status.lower(), 0)

def format_datetime(dt_string):
    """Format datetime string for display"""
    if not dt_string:
        return "Not available"
    try:
        dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return dt_string

def get_supplier_name(order):
    """Get supplier name with fallback for different backend formats"""
    # Handle different field names from different backends
    if 'supplier' in order:
        return order['supplier']
    elif 'supplier_name' in order:
        return order['supplier_name']
    else:
        return "Unassigned"

def ensure_order_fields(order):
    """Ensure all required order fields exist with defaults"""
    defaults = {
        'id': order.get('id', 'Unknown'),
        'restaurant_name': order.get('restaurant_name', 'Unknown Restaurant'),
        'status': order.get('status', 'open'),
        'total': order.get('total', 0.0),
        'delivery_fee': order.get('delivery_fee', 3.99),
        'subtotal': order.get('subtotal', order.get('total', 0.0) - order.get('delivery_fee', 3.99)),
        'was_prime_order': order.get('was_prime_order', False),
        'order_date': order.get('order_date', datetime.now().isoformat()),
        'estimated_delivery': order.get('estimated_delivery'),
        'actual_delivery': order.get('actual_delivery'),
        'supplier': get_supplier_name(order)
    }
    
    # Update order with defaults for missing fields
    for key, default_value in defaults.items():
        if key not in order or order[key] is None:
            order[key] = default_value
    
    return order

def show_order_timeline(order):
    """Show order timeline with delivery tracking"""
    st.subheader("📍 Order Timeline & Tracking")
    
    # Progress bar
    progress = get_delivery_progress(order['status'])
    st.progress(progress / 100)
    
    # Timeline
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.write("**📝 Order Placed**")
        st.write(f"✅ {format_datetime(order['order_date'])}")
        st.write("Order confirmed and sent to restaurant")
    
    with col2:
        st.write("**👨‍🍳 In Preparation**")
        if order['status'] in ['in preparation', 'in delivery', 'delivered']:
            st.write("✅ Restaurant preparing")
            st.write("Your food is being prepared")
        else:
            st.write("⏳ Waiting...")
    
    with col3:
        st.write("**🚚 Out for Delivery**")
        if order['status'] in ['in delivery', 'delivered']:
            st.write("✅ On the way")
            st.write(f"Delivered by: {order['supplier']}")
            if order.get('estimated_delivery'):
                st.write(f"ETA: {format_datetime(order['estimated_delivery'])}")
        else:
            st.write("⏳ Waiting...")
    
    with col4:
        st.write("**🎉 Delivered**")
        if order['status'] == 'delivered':
            if order.get('actual_delivery'):
                st.write(f"✅ {format_datetime(order['actual_delivery'])}")
            else:
                st.write("✅ Delivered")
            st.write("Enjoy your meal!")
        else:
            st.write("⏳ Pending...")

st.title("📦 My Orders")

# Check backend health
if not check_backend_health():
    handle_backend_error("Backend is not responding")
    st.stop()

# Tabs for different views
tab1, tab2, tab3, tab4 = st.tabs(["🚚 Order Tracking", "📋 Order History", "📊 Admin Dashboard", "📈 Delivery Analytics"])

with tab1:
    st.header("🚚 Live Order Tracking")
    st.write("**Real-time tracking of your current orders**")
    
    # Fetch orders with error handling
    try:
        response = requests.get(f"{BASE_URL}/users/{st.session_state.user['id']}/orders", timeout=10)
        if response.status_code == 200:
            orders = response.json()
            # Ensure all orders have required fields
            orders = [ensure_order_fields(order) for order in orders]
        elif response.status_code == 404:
            orders = []
            st.info("No orders found. Start by placing your first order!")
        else:
            handle_backend_error(f"Failed to fetch orders: {response.status_code}")
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
    
    if orders:
        # Filter active orders (not delivered)
        active_orders = [order for order in orders if order['status'] != 'delivered']
        delivered_orders = [order for order in orders if order['status'] == 'delivered']
        
        if active_orders:
            st.subheader(f"🔄 Active Orders ({len(active_orders)})")
            
            for order in active_orders:
                status_icon = get_status_color(order['status'])
                
                with st.container():
                    st.markdown(f"### {status_icon} Order #{order['id']} - {order['restaurant_name']}")
                    
                    # Order summary
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Amount", f"€{float(order['total']):.2f}")
                    with col2:
                        st.metric("Status", order['status'].title())
                    with col3:
                        st.metric("Delivery Fee", f"€{float(order['delivery_fee']):.2f}")
                    with col4:
                        if order['was_prime_order']:
                            st.success("🌟 Prime Order")
                        else:
                            st.info("Regular Order")
                    
                    # Delivery information
                    st.write("**🚚 Delivery Information:**")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Supplier:** {order['supplier']}")
                    with col2:
                        if order.get('estimated_delivery'):
                            st.write(f"**ETA:** {format_datetime(order['estimated_delivery'])}")
                    with col3:
                        st.write(f"**Order Date:** {format_datetime(order['order_date'])}")
                    
                    # Timeline
                    show_order_timeline(order)
                    
                    st.divider()
        
        else:
            st.info("🎉 No active orders! All your orders have been delivered.")
        
        # Recent delivered orders
        if delivered_orders:
            st.subheader(f"✅ Recently Delivered ({len(delivered_orders)})")
            
            for order in delivered_orders[-3:]:  # Show last 3 delivered
                with st.expander(f"✅ Order #{order['id']} - {order['restaurant_name']} - €{float(order['total']):.2f}"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Delivered:** {format_datetime(order.get('actual_delivery', order['order_date']))}")
                    with col2:
                        st.write(f"**Total:** €{float(order['total']):.2f}")
                    with col3:
                        st.write(f"**Delivery Fee:** €{float(order['delivery_fee']):.2f}")
                    
                    if order['was_prime_order']:
                        st.success("🌟 Prime Order")
                    else:
                        st.info("Regular Order")
    else:
        st.info("No orders found. Start by placing your first order!")
        if st.button("🍽️ Browse Restaurants"):
            switch_page("home")

with tab2:
    st.header("📋 Complete Order History")
    st.write("**All your past orders with detailed delivery information**")
    
    try:
        response = requests.get(f"{BASE_URL}/users/{st.session_state.user['id']}/orders")
        if response.status_code == 200:
            orders = response.json()
            
            if orders:
                st.write(f"Found {len(orders)} total orders")
                
                # Order filters
                col1, col2, col3 = st.columns(3)
                with col1:
                    status_filter = st.selectbox("Filter by Status", 
                                               ["All", "delivered", "in delivery", "in preparation", "open"])
                with col2:
                    prime_filter = st.selectbox("Filter by Type", ["All", "Prime Orders", "Regular Orders"])
                with col3:
                    sort_order = st.selectbox("Sort by", ["Newest First", "Oldest First", "Highest Amount", "Lowest Amount"])
                
                # Apply filters
                filtered_orders = orders.copy()
                
                if status_filter != "All":
                    filtered_orders = [o for o in filtered_orders if o['status'] == status_filter]
                
                if prime_filter == "Prime Orders":
                    filtered_orders = [o for o in filtered_orders if o['was_prime_order']]
                elif prime_filter == "Regular Orders":
                    filtered_orders = [o for o in filtered_orders if not o['was_prime_order']]
                
                # Sort orders
                if sort_order == "Newest First":
                    filtered_orders.sort(key=lambda x: x['order_date'], reverse=True)
                elif sort_order == "Oldest First":
                    filtered_orders.sort(key=lambda x: x['order_date'])
                elif sort_order == "Highest Amount":
                    filtered_orders.sort(key=lambda x: x['total'], reverse=True)
                elif sort_order == "Lowest Amount":
                    filtered_orders.sort(key=lambda x: x['total'])
                
                st.write(f"Showing {len(filtered_orders)} orders")
                
                for order in filtered_orders:
                    status_icon = get_status_color(order['status'])
                    
                    with st.expander(f"{status_icon} Order #{order['id']} - {order['restaurant_name']} - €{order['total']:.2f} - {format_datetime(order['order_date'])}"):
                        
                        # Order details
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.write("**📝 Order Details**")
                            st.write(f"Order ID: #{order['id']}")
                            st.write(f"Date: {format_datetime(order['order_date'])}")
                            st.write(f"Status: {order['status'].title()}")
                            st.write(f"Restaurant: {order['restaurant_name']}")
                        
                        with col2:
                            st.write("**💰 Payment Details**")
                            st.write(f"Subtotal: €{order['subtotal']:.2f}")
                            st.write(f"Delivery Fee: €{order['delivery_fee']:.2f}")
                            st.write(f"**Total: €{order['total']:.2f}**")
                            if order['was_prime_order']:
                                st.success("🌟 Prime Order")
                            else:
                                st.info("Regular Order")
                        
                        with col3:
                            st.write("**🚚 Delivery Details**")
                            st.write(f"Supplier: {order['supplier']}")
                            if order.get('estimated_delivery'):
                                st.write(f"Estimated: {format_datetime(order['estimated_delivery'])}")
                            if order.get('actual_delivery'):
                                st.write(f"Delivered: {format_datetime(order['actual_delivery'])}")
                            else:
                                st.write("Delivery time: Not recorded")
                        
                        with col4:
                            st.write("**📊 Order Metrics**")
                            if order['delivery_fee'] == 0:
                                st.write("💰 Saved €3.99 with Prime")
                            else:
                                st.write(f"💸 Delivery fee: €{order['delivery_fee']:.2f}")
                            
                            # Calculate delivery time if available
                            if order.get('actual_delivery') and order.get('order_date'):
                                try:
                                    order_time = datetime.fromisoformat(order['order_date'].replace('Z', '+00:00'))
                                    delivery_time = datetime.fromisoformat(order['actual_delivery'].replace('Z', '+00:00'))
                                    duration = delivery_time - order_time
                                    st.write(f"⏱️ Delivery time: {duration}")
                                except:
                                    pass
            else:
                st.info("No orders found. Start shopping to see your orders here!")
                if st.button("Start Shopping"):
                    switch_page("home")
        else:
            st.error("Could not fetch your orders")
    except Exception as e:
        st.error(f"Error loading orders: {e}")

with tab3:
    st.header("📊 Admin Dashboard - All Orders")
    st.write("**System-wide order and delivery management**")
    
    try:
        response = requests.get(f"{BASE_URL}/orders")
        if response.status_code == 200:
            all_orders = response.json()
            
            if all_orders:
                st.write(f"Total orders in system: {len(all_orders)}")
                
                # Summary statistics
                total_revenue = sum(order['total'] for order in all_orders)
                prime_orders = [order for order in all_orders if order['was_prime_order']]
                regular_orders = [order for order in all_orders if not order['was_prime_order']]
                
                # Status breakdown
                status_counts = {}
                for order in all_orders:
                    status = order['status']
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                # Metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Orders", len(all_orders))
                with col2:
                    st.metric("Total Revenue", f"€{total_revenue:.2f}")
                with col3:
                    st.metric("Prime Orders", len(prime_orders))
                with col4:
                    st.metric("Regular Orders", len(regular_orders))
                
                # Status overview
                st.subheader("📈 Order Status Overview")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Order Status Distribution:**")
                    for status, count in status_counts.items():
                        icon = get_status_color(status)
                        st.write(f"{icon} {status.title()}: {count} orders")
                
                with col2:
                    if status_counts:
                        st.bar_chart(status_counts)
                
                # Recent orders with delivery tracking
                st.subheader("🚚 Recent Orders with Delivery Tracking")
                for order in all_orders[-10:]:  # Show last 10 orders
                    status_icon = get_status_color(order['status'])
                    
                    with st.expander(f"{status_icon} Order #{order['id']} - {order['user_name']} - €{order['total']:.2f}"):
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.write(f"**Customer:** {order['user_name']}")
                            st.write(f"**Restaurant:** {order['restaurant_name']}")
                            st.write(f"**Date:** {format_datetime(order['order_date'])}")
                        
                        with col2:
                            st.write(f"**Status:** {order['status'].title()}")
                            st.write(f"**Supplier:** {order['supplier']}")
                            if order.get('estimated_delivery'):
                                st.write(f"**ETA:** {format_datetime(order['estimated_delivery'])}")
                        
                        with col3:
                            st.write(f"**Subtotal:** €{order['subtotal']:.2f}")
                            st.write(f"**Delivery Fee:** €{order['delivery_fee']:.2f}")
                            st.write(f"**Total:** €{order['total']:.2f}")
                        
                        with col4:
                            if order['was_prime_order']:
                                st.success("🌟 Prime Order")
                            else:
                                st.info("Regular Order")
                            
                            if order.get('actual_delivery'):
                                st.write(f"**Delivered:** {format_datetime(order['actual_delivery'])}")
            else:
                st.info("No orders in the system yet")
        else:
            st.error("Could not fetch orders data")
    except Exception as e:
        st.error(f"Error loading orders: {e}")

with tab4:
    st.header("📈 Delivery Analytics & Performance")
    st.write("**Comprehensive delivery and performance analytics**")
    
    try:
        response = requests.get(f"{BASE_URL}/orders")
        if response.status_code == 200:
            all_orders = response.json()
            
            if all_orders:
                # Calculate analytics
                prime_orders = [order for order in all_orders if order['was_prime_order']]
                regular_orders = [order for order in all_orders if not order['was_prime_order']]
                
                total_delivery_fees = sum(order['delivery_fee'] for order in all_orders)
                prime_delivery_fees = sum(order['delivery_fee'] for order in prime_orders)
                regular_delivery_fees = sum(order['delivery_fee'] for order in regular_orders)
                
                # Supplier performance
                supplier_stats = {}
                for order in all_orders:
                    supplier = order['supplier']
                    if supplier not in supplier_stats:
                        supplier_stats[supplier] = {'orders': 0, 'revenue': 0}
                    supplier_stats[supplier]['orders'] += 1
                    supplier_stats[supplier]['revenue'] += order['total']
                
                # Display analytics
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📊 Order Type Distribution")
                    chart_data = {
                        "Prime Orders": len(prime_orders),
                        "Regular Orders": len(regular_orders)
                    }
                    st.bar_chart(chart_data)
                
                with col2:
                    st.subheader("💰 Delivery Fees Collected")
                    fee_data = {
                        "Prime Orders": prime_delivery_fees,
                        "Regular Orders": regular_delivery_fees
                    }
                    st.bar_chart(fee_data)
                
                # Supplier performance
                st.subheader("🚚 Supplier Performance")
                if supplier_stats:
                    for supplier, stats in supplier_stats.items():
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.write(f"**{supplier}**")
                        with col2:
                            st.metric("Orders Delivered", stats['orders'])
                        with col3:
                            st.metric("Total Revenue", f"€{stats['revenue']:.2f}")
                
                # Detailed metrics
                st.subheader("📊 Detailed Performance Metrics")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Delivery Fees", f"€{total_delivery_fees:.2f}")
                with col2:
                    avg_order_value = sum(order['total'] for order in all_orders) / len(all_orders)
                    st.metric("Avg Order Value", f"€{avg_order_value:.2f}")
                with col3:
                    prime_percentage = (len(prime_orders) / len(all_orders)) * 100
                    st.metric("Prime Order %", f"{prime_percentage:.1f}%")
                with col4:
                    if prime_orders:
                        avg_prime_value = sum(order['total'] for order in prime_orders) / len(prime_orders)
                        st.metric("Avg Prime Order", f"€{avg_prime_value:.2f}")
                
                # Prime savings analysis
                st.subheader("💰 Prime Savings Analysis")
                potential_prime_fees = len(prime_orders) * 3.99
                actual_prime_fees = sum(order['delivery_fee'] for order in prime_orders)
                total_savings = potential_prime_fees - actual_prime_fees
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Potential Prime Fees", f"€{potential_prime_fees:.2f}")
                with col2:
                    st.metric("Actual Prime Fees", f"€{actual_prime_fees:.2f}")
                with col3:
                    st.metric("Total Prime Savings", f"€{total_savings:.2f}")
                
            else:
                st.info("No order data available for analytics")
        else:
            st.error("Could not fetch analytics data")
    except Exception as e:
        st.error(f"Error loading analytics: {e}")

# Footer with refresh info
st.write("---")
st.write("💡 **Tip:** Enable auto-refresh in the sidebar for real-time order tracking updates!") 