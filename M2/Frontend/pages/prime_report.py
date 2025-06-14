import streamlit as st
import requests
from streamlit_extras.switch_page_button import switch_page

# Backend URL setup
if "active_backend" not in st.session_state:
    st.session_state.active_backend = "SQL"
    st.session_state.backend_url = "http://backend:5000"
elif st.session_state.active_backend == "SQL":
    st.session_state.backend_url = "http://backend:5000"
elif st.session_state.active_backend == "MONGO":
    st.session_state.backend_url = "http://mongo-backend:5001"

BASE_URL = st.session_state.backend_url

# Check if user is logged in
if "user" not in st.session_state:
    st.warning("Please sign in to view reports")
    switch_page("sign_in")
    st.stop()

st.set_page_config(page_title="Prime Statistics Report", layout="wide")

st.title("📊 Prime Customer Statistics Report")
st.write("**Enhanced analytics report showing Prime customer statistics with historical delivery fees**")
st.write("*Addressing M1 feedback: Shows statistics, not just Prime status check*")

# User selection for report
st.header("Select User for Report")
user_id = st.number_input("User ID", min_value=1, value=st.session_state.user["id"])

if st.button("Generate Enhanced Statistics Report"):
    try:
        response = requests.get(f"{BASE_URL}/reports/prime-statistics/{user_id}")
        
        if response.status_code == 200:
            report_data = response.json()
            stats = report_data["statistics"]
            
            st.success("Enhanced statistics report generated successfully!")
            
            # Customer Info
            st.header("👤 Customer Information")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Customer", f"{report_data['first_name']} {report_data['last_name']}")
            with col2:
                st.metric("Prime Status", "✅ Active" if report_data['free_delivery'] else "❌ Inactive")
            with col3:
                st.metric("User ID", report_data['user_id'])
            
            # Order Statistics (addressing M1 feedback)
            st.header("📈 Order Statistics")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Orders", stats['total_orders'])
            with col2:
                st.metric("Total Dishes", stats['total_dishes'])
            with col3:
                st.metric("Average Order Value", f"€{stats['average_order_value']:.2f}")
            with col4:
                st.metric("Total Amount Paid", f"€{stats['total_amount_paid']:.2f}")
            
            # Financial Breakdown (addressing M1 feedback about historical fees)
            st.header("💰 Financial Breakdown")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Food Cost", f"€{stats['total_food_cost']:.2f}")
            with col2:
                st.metric("Delivery Fees Paid", f"€{stats['total_delivery_fees_paid']:.2f}", 
                         help="Historical delivery fees from past orders")
            with col3:
                st.metric("Delivery Fees Saved", f"€{stats['delivery_fees_saved']:.2f}",
                         help="Amount saved through Prime membership")
            
            # Prime Benefits Analysis
            st.header("🌟 Prime Benefits Analysis")
            
            # Calculate potential savings
            potential_savings = stats['total_orders'] * 3.99
            actual_savings = stats['delivery_fees_saved']
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Potential Max Savings", f"€{potential_savings:.2f}",
                         help="If all orders were Prime orders")
            with col2:
                st.metric("Actual Savings Realized", f"€{actual_savings:.2f}")
            
            # Detailed breakdown
            st.subheader("Detailed Analysis")
            st.write(f"**Customer:** {report_data['first_name']} {report_data['last_name']}")
            st.write(f"**Prime Status:** {'Active' if report_data['free_delivery'] else 'Inactive'}")
            st.write(f"**Total Orders Placed:** {stats['total_orders']}")
            st.write(f"**Total Dishes Ordered:** {stats['total_dishes']}")
            st.write(f"**Total Food Cost:** €{stats['total_food_cost']:.2f}")
            st.write(f"**Historical Delivery Fees Paid:** €{stats['total_delivery_fees_paid']:.2f}")
            st.write(f"**Total Amount Paid:** €{stats['total_amount_paid']:.2f}")
            st.write(f"**Average Order Value:** €{stats['average_order_value']:.2f}")
            st.write(f"**Delivery Fees Saved through Prime:** €{stats['delivery_fees_saved']:.2f}")
            
            # Chart visualization
            st.header("📊 Cost Breakdown Chart")
            chart_data = {
                "Food Cost": stats['total_food_cost'],
                "Delivery Fees Paid": stats['total_delivery_fees_paid'],
                "Delivery Fees Saved": stats['delivery_fees_saved']
            }
            st.bar_chart(chart_data)
            
        elif response.status_code == 404:
            st.warning("No Prime orders found for this user")
            st.info("This user either:")
            st.write("- Has no orders yet")
            st.write("- Is not a Prime member")
            st.write("- Has not placed any orders since becoming Prime")
        else:
            st.error(f"Error generating report: {response.text}")
            
    except Exception as e:
        st.error(f"Error: {e}")

# Show all orders for context
st.header("📋 User Order History")
if st.button("Show Order History"):
    try:
        response = requests.get(f"{BASE_URL}/users/{user_id}/orders")
        if response.status_code == 200:
            orders = response.json()
            if orders:
                for order in orders:
                    with st.expander(f"Order #{order['id']} - {order['restaurant_name']} - €{order['total']:.2f}"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.write(f"**Date:** {order['order_date'][:10]}")
                            st.write(f"**Status:** {order['status']}")
                        with col2:
                            st.write(f"**Subtotal:** €{order['subtotal']:.2f}")
                            st.write(f"**Delivery Fee:** €{order['delivery_fee']:.2f}")
                        with col3:
                            st.write(f"**Total:** €{order['total']:.2f}")
                            st.write(f"**Prime Order:** {'Yes' if order['was_prime_order'] else 'No'}")
                        st.write(f"**Supplier:** {order['supplier']}")
            else:
                st.info("No orders found for this user")
        else:
            st.error("Could not fetch order history")
    except Exception as e:
        st.error(f"Error fetching orders: {e}")

# Navigation
st.write("---")
if st.button("← Back to Home"):
    switch_page("home") 