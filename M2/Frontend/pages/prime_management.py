import streamlit as st
import requests
from streamlit_extras.switch_page_button import switch_page
from datetime import datetime
from session import ensure_backend_consistency, check_backend_health, handle_backend_error

# Page configuration - MUST be first Streamlit command
st.set_page_config(page_title="Prime Management", layout="wide")

# Ensure backend consistency
ensure_backend_consistency()
BASE_URL = st.session_state.backend_url

# Check if user is logged in
if "user" not in st.session_state:
    st.warning("Please sign in to access Prime management")
    switch_page("sign_in")
    st.stop()
st.title("🌟 Prime Membership Management")

# Check backend health
if not check_backend_health():
    handle_backend_error("Backend is not responding")
    st.stop()

# Sidebar navigation
st.sidebar.write(f"Welcome, {st.session_state.user['first_name']} {st.session_state.user['last_name']}")
if st.sidebar.button("🏠 Home"):
    switch_page("home")
if st.sidebar.button("📦 My Orders"):
    switch_page("orders")
if st.sidebar.button("Logout"):
    del st.session_state.user
    switch_page("landing_page")

def format_datetime(dt_string):
    """Format datetime string for display"""
    if not dt_string:
        return "Not available"
    try:
        dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return dt_string

# Check Prime status
try:
    response = requests.get(f"{BASE_URL}/users/{st.session_state.user['id']}/prime/status")
    if response.status_code == 200:
        prime_status = response.json()
    else:
        st.error("Could not check Prime status")
        st.stop()
except Exception as e:
    st.error(f"Error checking Prime status: {e}")
    st.stop()

# Tabs for different views
tab1, tab2, tab3 = st.tabs(["📊 Subscription Overview", "💳 Payment History", "⚙️ Account Settings"])

with tab1:
    st.header("📊 Prime Subscription Overview")
    
    if prime_status["is_prime"]:
        st.success("🎉 You are a Prime member!")
        
        # Get subscription details
        try:
            sub_response = requests.get(f"{BASE_URL}/users/{st.session_state.user['id']}/prime/subscription")
            if sub_response.status_code == 200:
                subscription = sub_response.json()
                
                # Subscription status
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Monthly Fee", f"€{subscription['monthly_fee']:.2f}")
                with col2:
                    st.metric("Status", "Active" if subscription['is_active'] else "Cancelled")
                with col3:
                    st.metric("Auto Renew", "Yes" if subscription['auto_renew'] else "No")
                with col4:
                    if subscription['end_date']:
                        st.metric("End Date", format_datetime(subscription['end_date']))
                    else:
                        st.metric("Next Billing", "Monthly")
                
                # Subscription details
                st.subheader("📋 Subscription Details")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Start Date:** {format_datetime(subscription['start_date'])}")
                    st.write(f"**Subscription ID:** #{subscription['id']}")
                    if subscription['cancelled_date']:
                        st.write(f"**Cancelled Date:** {format_datetime(subscription['cancelled_date'])}")
                        st.write(f"**Cancellation Reason:** {subscription['cancellation_reason']}")
                
                with col2:
                    st.write("**Prime Benefits:**")
                    st.write("✅ Free delivery on all orders")
                    st.write("✅ Priority customer support")
                    st.write("✅ Exclusive member deals")
                    st.write("✅ No minimum order amount")
                
                # Payment history summary
                if subscription['payment_history']:
                    st.subheader("💰 Recent Payments")
                    for payment in subscription['payment_history'][-3:]:  # Last 3 payments
                        with st.expander(f"Payment - {format_datetime(payment['payment_date'])} - €{payment['amount']:.2f}"):
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.write(f"**Amount:** €{payment['amount']:.2f}")
                                st.write(f"**Status:** {payment['status'].title()}")
                            with col2:
                                st.write(f"**Billing Period:**")
                                st.write(f"From: {format_datetime(payment['billing_period']['start'])}")
                                st.write(f"To: {format_datetime(payment['billing_period']['end'])}")
                            with col3:
                                if payment['status'] == 'completed':
                                    st.success("✅ Paid")
                                elif payment['status'] == 'pending':
                                    st.warning("⏳ Pending")
                                else:
                                    st.error("❌ Failed")
            else:
                st.error("Could not load subscription details")
                
        except Exception as e:
            st.error(f"Error loading subscription: {e}")
    else:
        st.info("You are not currently a Prime member")
        st.write("**Benefits of Prime membership:**")
        st.write("🚚 Free delivery on all orders (save €3.99 per order)")
        st.write("⚡ Priority customer support")
        st.write("🎯 Exclusive deals and discounts")
        st.write("💰 Monthly fee: €9.99")
        
        if st.button("🌟 Activate Prime Membership", key="activate_prime_main"):
            switch_page("prime_activation")

with tab2:
    st.header("💳 Payment History")
    st.write("**Complete payment history for your account**")
    
    try:
        payments_response = requests.get(f"{BASE_URL}/users/{st.session_state.user['id']}/payments")
        if payments_response.status_code == 200:
            payments = payments_response.json()
            
            if payments:
                # Payment filters
                col1, col2, col3 = st.columns(3)
                with col1:
                    payment_filter = st.selectbox("Filter by Type", ["All", "Prime Payments", "Order Payments"])
                with col2:
                    status_filter = st.selectbox("Filter by Status", ["All", "completed", "pending", "failed", "refunded"])
                with col3:
                    sort_order = st.selectbox("Sort by", ["Newest First", "Oldest First", "Highest Amount", "Lowest Amount"])
                
                # Apply filters
                filtered_payments = payments.copy()
                
                if payment_filter == "Prime Payments":
                    filtered_payments = [p for p in filtered_payments if p['is_prime_payment']]
                elif payment_filter == "Order Payments":
                    filtered_payments = [p for p in filtered_payments if not p['is_prime_payment']]
                
                if status_filter != "All":
                    filtered_payments = [p for p in filtered_payments if p['payment_status'] == status_filter]
                
                # Sort payments
                if sort_order == "Newest First":
                    filtered_payments.sort(key=lambda x: x['payment_date'], reverse=True)
                elif sort_order == "Oldest First":
                    filtered_payments.sort(key=lambda x: x['payment_date'])
                elif sort_order == "Highest Amount":
                    filtered_payments.sort(key=lambda x: x['amount'], reverse=True)
                elif sort_order == "Lowest Amount":
                    filtered_payments.sort(key=lambda x: x['amount'])
                
                st.write(f"Showing {len(filtered_payments)} payments")
                
                # Display payments
                for payment in filtered_payments:
                    status_icon = "✅" if payment['payment_status'] == 'completed' else "⏳" if payment['payment_status'] == 'pending' else "❌"
                    payment_type = "🌟 Prime" if payment['is_prime_payment'] else "🛒 Order"
                    
                    with st.expander(f"{status_icon} {payment_type} - €{payment['amount']:.2f} - {format_datetime(payment['payment_date'])}"):
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.write("**Payment Details**")
                            st.write(f"Amount: €{payment['amount']:.2f}")
                            st.write(f"Method: {payment['payment_method'].replace('_', ' ').title()}")
                            st.write(f"Status: {payment['payment_status'].title()}")
                        
                        with col2:
                            st.write("**Transaction Info**")
                            st.write(f"Date: {format_datetime(payment['payment_date'])}")
                            st.write(f"ID: {payment['transaction_id'] or 'N/A'}")
                            st.write(f"Description: {payment['description']}")
                        
                        with col3:
                            st.write("**Type & Reference**")
                            if payment['is_prime_payment']:
                                st.write("Type: Prime Subscription")
                                if 'billing_period' in payment:
                                    st.write(f"Billing: {format_datetime(payment['billing_period']['start'])} - {format_datetime(payment['billing_period']['end'])}")
                            else:
                                st.write("Type: Order Payment")
                                if payment['order_id']:
                                    st.write(f"Order: #{payment['order_id']}")
                        
                        with col4:
                            if payment['payment_status'] == 'completed':
                                st.success("✅ Payment Successful")
                            elif payment['payment_status'] == 'pending':
                                st.warning("⏳ Payment Pending")
                            elif payment['payment_status'] == 'failed':
                                st.error("❌ Payment Failed")
                            elif payment['payment_status'] == 'refunded':
                                st.info("🔄 Payment Refunded")
                
                # Payment summary
                st.subheader("📊 Payment Summary")
                total_spent = sum(p['amount'] for p in payments if p['payment_status'] == 'completed')
                prime_spent = sum(p['amount'] for p in payments if p['is_prime_payment'] and p['payment_status'] == 'completed')
                order_spent = sum(p['amount'] for p in payments if not p['is_prime_payment'] and p['payment_status'] == 'completed')
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Spent", f"€{total_spent:.2f}")
                with col2:
                    st.metric("Prime Payments", f"€{prime_spent:.2f}")
                with col3:
                    st.metric("Order Payments", f"€{order_spent:.2f}")
                with col4:
                    st.metric("Total Transactions", len([p for p in payments if p['payment_status'] == 'completed']))
                
            else:
                st.info("No payment history found")
        else:
            st.error("Could not load payment history")
            
    except Exception as e:
        st.error(f"Error loading payments: {e}")

with tab3:
    st.header("⚙️ Prime Account Settings")
    
    if prime_status["is_prime"]:
        st.subheader("🚫 Cancel Prime Membership")

        # Warning box with detailed information
        st.error("""
        ⚠️ **IMPORTANT: Cancellation Impact**

        Cancelling your Prime membership will result in the **immediate loss** of the following benefits:
        """)

        # Create columns to show what will be lost
        loss_col1, loss_col2 = st.columns(2)

        with loss_col1:
            st.markdown("""
            **🚚 Delivery Benefits (Lost Immediately):**
            - ❌ Free delivery (€3.99 will be charged per order)
            - ❌ Priority delivery processing
            - ❌ No minimum order requirement
            - ❌ Weather protection guarantee
            
            **💰 Financial Benefits (Lost Immediately):**
            - ❌ Monthly delivery savings (avg. €15.96/month)
            - ❌ Exclusive discounts up to 20%
            - ❌ Birthday month free delivery
            - ❌ 2% cashback rewards on orders over €25
            """)

        with loss_col2:
            st.markdown("""
            **🎯 Exclusive Features (Lost Immediately):**
            - ❌ Early access to new restaurants
            - ❌ Prime-only deals and flash sales
            - ❌ Advanced order tracking with GPS
            - ❌ Priority customer support hotline
            
            **🏆 Premium Experience (Lost Immediately):**
            - ❌ Special Prime packaging
            - ❌ 100% satisfaction guarantee
            - ❌ Advanced order scheduling (7 days)
            - ❌ Group ordering coordination
            """)

        # Grace period information
        st.warning("""
        **📅 Grace Period:** You have a 30-day grace period after cancellation where you can reactivate your membership without losing your Prime history and preferences.
        """)

        # Cost impact calculator
        st.info("""
        **💡 Cost Impact Example:**
        - If you typically order 4 times per month: **+€15.96/month** in delivery fees
        - If you typically order 8 times per month: **+€31.92/month** in delivery fees
        - Plus loss of exclusive discounts and cashback rewards
        """)

        # Cancellation form
        with st.form("cancel_prime_form"):
            st.markdown("### Cancellation Details")
            
            cancellation_reason = st.selectbox(
                "Why are you cancelling? (Optional)",
                [
                    "Too expensive",
                    "Don't order frequently enough",
                    "Not satisfied with service",
                    "Found better alternative",
                    "Temporary financial constraints",
                    "Moving to area without coverage",
                    "Other"
                ]
            )
            
            if cancellation_reason == "Other":
                other_reason = st.text_area("Please specify:")
                final_reason = other_reason if other_reason else "Other"
            else:
                final_reason = cancellation_reason
            
            # Confirmation checkboxes
            st.markdown("**Please confirm you understand:**")
            
            confirm_loss = st.checkbox("✅ I understand I will immediately lose all Prime benefits listed above")
            confirm_charges = st.checkbox("✅ I understand delivery fees (€3.99) will be charged on future orders")
            confirm_discounts = st.checkbox("✅ I understand I will lose access to exclusive discounts and deals")
            confirm_final = st.checkbox("✅ I want to proceed with cancelling my Prime membership")
            
            # Submit button
            submitted = st.form_submit_button(
                "🚫 Cancel Prime Membership", 
                type="secondary",
                disabled=not all([confirm_loss, confirm_charges, confirm_discounts, confirm_final])
            )
            
            if submitted:
                if all([confirm_loss, confirm_charges, confirm_discounts, confirm_final]):
                    try:
                        cancel_response = requests.post(
                            f"{BASE_URL}/users/{st.session_state.user['id']}/prime/cancel",
                            json={"reason": final_reason}
                        )
                        
                        if cancel_response.status_code == 200:
                            cancel_data = cancel_response.json()
                            
                            st.success("✅ Prime membership cancelled successfully!")
                            
                            # Show cancellation details
                            st.info(f"""
                            **Cancellation Details:**
                            - **Cancelled on:** {cancel_data.get('cancellation_date', 'Now')}
                            - **Grace period ends:** {cancel_data.get('grace_period_end', '30 days from now')}
                            - **Reason:** {cancel_data.get('reason', final_reason)}
                            
                            **What happens now:**
                            1. 🚫 Prime benefits are **immediately disabled**
                            2. 💳 No further Prime charges will occur
                            3. 📅 You have 30 days to reactivate if you change your mind
                            4. 🔄 After 30 days, you'll need to sign up as a new Prime member
                            """)
                            
                            # Update session state to reflect cancellation
                            if "prime_status" in st.session_state:
                                st.session_state.prime_status["free_delivery"] = False
                            
                            st.balloons()
                            
                            # Offer alternatives
                            st.markdown("---")
                            st.subheader("🤔 Changed your mind?")
                            
                            alt_col1, alt_col2 = st.columns(2)
                            
                            with alt_col1:
                                if st.button("🔄 Reactivate Prime", type="primary", key="reactivate_prime_after_cancel"):
                                    switch_page("prime_activation")
                            
                            with alt_col2:
                                if st.button("🏠 Continue Shopping", key="continue_shopping_after_cancel"):
                                    switch_page("home")
                        
                        else:
                            st.error(f"Failed to cancel Prime: {cancel_response.text}")
                            
                    except Exception as e:
                        st.error(f"Error cancelling Prime: {e}")
                else:
                    st.warning("Please confirm all checkboxes to proceed with cancellation.")
        
        st.write("---")
        st.subheader("📞 Need Help?")
        st.write("If you're having issues with your Prime membership, please contact our support team:")
        st.write("📧 Email: prime-support@fooddelivery.com")
        st.write("📞 Phone: +43 1 234 5678")
        st.write("💬 Live Chat: Available 24/7 for Prime members")
        
    else:
        st.info("You don't have an active Prime membership to manage.")
        if st.button("🌟 Activate Prime Membership", key="activate_prime_top"):
            switch_page("prime_activation")

# Footer
st.write("---")
st.write("💡 **Tip:** Prime members save an average of €15.96 per month on delivery fees!") 