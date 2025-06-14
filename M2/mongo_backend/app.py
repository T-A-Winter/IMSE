from flask import Flask, request, jsonify
from pymongo import MongoClient
import os
from flask_cors import CORS
import datetime
import subprocess
import threading

app = Flask(__name__)
CORS(app)

# MongoDB connection
mongo_uri = os.environ.get("MONGO_URI", "mongodb://mongodb:27017/")
client = MongoClient(mongo_uri)
db = client.food_delivery

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy", 
        "backend": "MongoDB",
        "timestamp": datetime.datetime.now().isoformat()
    })

@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    restaurants = list(db.restaurants.find({}, {"_id": 0}))
    # Add formatted address for frontend display
    for restaurant in restaurants:
        if all(k in restaurant for k in ["street", "city", "zipcode"]):
            restaurant["address"] = f"{restaurant['street']}, {restaurant['city']}, {restaurant['zipcode']}"
    return jsonify(restaurants)

@app.route("/restaurants/<restaurant_id>", methods=["GET"])
def get_restaurant(restaurant_id):
    restaurant = db.restaurants.find_one({"id": int(restaurant_id)}, {"_id": 0})
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404
    return jsonify(restaurant)

@app.route("/restaurants/<restaurant_id>/dishes", methods=["GET"])
def get_dishes(restaurant_id):
    dishes = list(db.dishes.find({"restaurant_id": int(restaurant_id)}, {"_id": 0}))
    return jsonify(dishes)

@app.route("/users", methods=["GET"])
def get_users():
    users = list(db.users.find({}, {"_id": 0, "password_hash": 0}))
    return jsonify(users)

@app.route("/users/<user_id>", methods=["GET"])
def get_user(user_id):
    user = db.users.find_one({"id": int(user_id)}, {"_id": 0, "password_hash": 0})
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user)

@app.route("/carts", methods=["POST"])
def create_cart():
    data = request.get_json()
    
    if "restaurant_id" not in data:
        return jsonify({"error": "Missing restaurant_id"}), 400
    
    # Get the next available ID using consistent ID management
    cart_id = get_next_id("carts")
    
    # Create a new cart
    new_cart = {
        "id": cart_id,
        "restaurant_id": data["restaurant_id"],
        "created_at": datetime.datetime.now().isoformat(),
        "state": "open"
    }
    
    # Insert into MongoDB
    db.carts.insert_one(new_cart)
    
    # Remove _id field for response
    new_cart.pop("_id", None)
    
    return jsonify(new_cart), 201

@app.route("/carts/<cart_id>/items", methods=["POST"])
def add_cart_item(cart_id):
    data = request.get_json()
    
    if not all(k in data for k in ("dish_id", "quantity")):
        return jsonify({"error": "Missing dish_id or quantity"}), 400
    
    # Check if cart exists
    cart = db.carts.find_one({"id": int(cart_id)})
    if not cart:
        return jsonify({"error": "Cart not found"}), 404
    
    # Check if dish exists
    dish = db.dishes.find_one({"id": int(data["dish_id"])})
    if not dish:
        return jsonify({"error": "Dish not found"}), 404
    
    # Get restaurant address
    restaurant = db.restaurants.find_one({"id": int(dish["restaurant_id"])})
    restaurant_address = "Unknown"
    if restaurant and all(k in restaurant for k in ["street", "city", "zipcode"]):
        restaurant_address = f"{restaurant['street']}, {restaurant['city']}, {restaurant['zipcode']}"
    
    # Calculate total price
    price = dish.get("price", 0)
    total_price = price * data["quantity"]
    
    # Check if item already exists in cart
    item = db.order_items.find_one({
        "cart_id": int(cart_id),
        "dish_id": int(data["dish_id"])
    })
    
    if item:
        # Update quantity and total price if item exists
        new_quantity = item["quantity"] + data["quantity"]
        new_total_price = price * new_quantity
        
        db.order_items.update_one(
            {"id": item["id"], "cart_id": int(cart_id)},
            {"$set": {"quantity": new_quantity, "total_price": new_total_price}}
        )
        
        # Get updated item
        updated_item = db.order_items.find_one({"id": item["id"], "cart_id": int(cart_id)}, {"_id": 0})
        return jsonify(updated_item), 201
    else:
        # Get next ID for order item
        item_id = get_next_id("order_items")
        
        # Create new item
        new_item = {
            "id": item_id,
            "cart_id": int(cart_id),
            "dish_id": int(data["dish_id"]),
            "quantity": data["quantity"],
            "total_price": total_price,
            "restaurant_address": restaurant_address
        }
        
        # Insert into MongoDB
        db.order_items.insert_one(new_item)
        
        # Remove _id field for response
        new_item.pop("_id", None)
        
        return jsonify(new_item), 201

@app.route("/carts/<cart_id>", methods=["GET"])
def get_cart(cart_id):
    cart = db.carts.find_one({"id": int(cart_id)}, {"_id": 0})
    if not cart:
        return jsonify({"error": "Cart not found"}), 404
    
    # Get cart items
    items = list(db.order_items.find({"cart_id": int(cart_id)}, {"_id": 0}))
    cart["items"] = items
    
    return jsonify(cart)

@app.route("/carts/<cart_id>/checkout", methods=["POST"])
def checkout_cart(cart_id):
    data = request.get_json()
    
    if "user_id" not in data:
        return jsonify({"error": "Missing user_id"}), 400
    
    # Check if cart exists
    cart = db.carts.find_one({"id": int(cart_id)})
    if not cart:
        return jsonify({"error": "Cart not found"}), 404
    
    # Check if user exists
    user = db.users.find_one({"id": int(data["user_id"])})
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Get cart items
    cart_items = list(db.order_items.find({"cart_id": int(cart_id)}))
    if not cart_items:
        return jsonify({"error": "Cart is empty"}), 400
    
    # Calculate subtotal (only dish prices, no delivery fee)
    subtotal = 0.0
    for item in cart_items:
        item_total = float(item.get("total_price", 0))
        subtotal += item_total
    
    # Round subtotal to avoid floating point precision issues
    subtotal = round(subtotal, 2)
    
    # Check Prime status
    prime_user = db.prime_users.find_one({"user_id": int(data["user_id"])})
    is_prime = prime_user is not None
    delivery_fee = 0.0 if is_prime else 3.99
    
    # Calculate total (subtotal + delivery fee)
    total = round(subtotal + delivery_fee, 2)
    
    # Debug logging
    print(f"DEBUG - Checkout calculation:")
    print(f"  Cart items count: {len(cart_items)}")
    print(f"  Subtotal: {subtotal}")
    print(f"  Is Prime: {is_prime}")
    print(f"  Delivery fee: {delivery_fee}")
    print(f"  Total: {total}")
    
    # Get next order ID
    order_id = get_next_id("orders")
    if not order_id:
        return jsonify({"error": "Failed to generate order ID"}), 500
    
    # Assign supplier
    suppliers = list(db.suppliers.find({}))
    assigned_supplier = None
    if suppliers:
        assigned_supplier = suppliers[0]  # Simple assignment logic
    
    # Calculate estimated delivery time
    estimated_delivery = datetime.datetime.now() + datetime.timedelta(minutes=30)
    
    # Create Order record with validated calculations
    order_data = {
        "id": order_id,
        "user_id": int(data["user_id"]),
        "restaurant_id": cart.get("restaurant_id"),
        "cart_id": int(cart_id),
        "supplier_id": assigned_supplier.get("id") if assigned_supplier else None,
        "order_date": datetime.datetime.now().isoformat(),
        "delivery_fee": round(delivery_fee, 2),
        "subtotal": round(subtotal, 2),
        "total": round(total, 2),
        "was_prime_order": is_prime,
        "status": "in preparation",
        "estimated_delivery": estimated_delivery.isoformat(),
        "actual_delivery": None
    }
    
    # Insert order
    db.orders.insert_one(order_data)
    
    # Update cart state
    db.carts.update_one(
        {"id": int(cart_id)},
        {"$set": {"state": "in preparation"}}
    )
    
    return jsonify({
        "message": "Order placed successfully",
        "order_id": order_id,
        "cart_id": int(cart_id),
        "subtotal": round(subtotal, 2),
        "delivery_fee": round(delivery_fee, 2),
        "total": round(total, 2),
        "is_prime_order": is_prime,
        "supplier": assigned_supplier.get("name") if assigned_supplier else "Assigning...",
        "estimated_delivery": estimated_delivery.strftime("%H:%M"),
        "state": "in preparation"
    }), 200

@app.route("/migrate", methods=["POST"])
def migrate_data():
    """Migrate data from SQL to MongoDB"""
    try:
        # Import requests here to avoid module import issues
        import requests
        import threading
        
        def run_migration():
            try:
                # Get data from SQL backend
                sql_base = "http://backend:5000"
                
                # Migrate restaurants
                try:
                    restaurants_response = requests.get(f"{sql_base}/restaurants", timeout=30)
                    if restaurants_response.status_code == 200:
                        restaurants = restaurants_response.json()
                        for restaurant in restaurants:
                            # Remove _id field if it exists
                            restaurant.pop("_id", None)
                            # Update or insert restaurant
                            db.restaurants.update_one(
                                {"id": restaurant["id"]},
                                {"$set": restaurant},
                                upsert=True
                            )
                        print(f"Migrated {len(restaurants)} restaurants")
                except Exception as e:
                    print(f"Error migrating restaurants: {e}")
                
                # Migrate users
                try:
                    users_response = requests.get(f"{sql_base}/users", timeout=30)
                    if users_response.status_code == 200:
                        users = users_response.json()
                        for user in users:
                            # Remove _id field if it exists
                            user.pop("_id", None)
                            # Update or insert user
                            db.users.update_one(
                                {"id": user["id"]},
                                {"$set": user},
                                upsert=True
                            )
                        print(f"Migrated {len(users)} users")
                except Exception as e:
                    print(f"Error migrating users: {e}")
                
                # Migrate orders
                try:
                    orders_response = requests.get(f"{sql_base}/orders", timeout=30)
                    if orders_response.status_code == 200:
                        orders = orders_response.json()
                        for order in orders:
                            # Remove _id field if it exists
                            order.pop("_id", None)
                            # Ensure proper order calculations
                            subtotal = float(order.get("subtotal", 0))
                            delivery_fee = float(order.get("delivery_fee", 3.99))
                            total = float(order.get("total", subtotal + delivery_fee))
                            
                            # Fix calculations if inconsistent
                            if abs(total - (subtotal + delivery_fee)) > 0.01:
                                if subtotal > 0:
                                    total = subtotal + delivery_fee
                                else:
                                    subtotal = max(0, total - delivery_fee)
                            
                            order["subtotal"] = round(subtotal, 2)
                            order["delivery_fee"] = round(delivery_fee, 2)
                            order["total"] = round(total, 2)
                            order["was_prime_order"] = bool(order.get("was_prime_order", False))
                            
                            # Update or insert order
                            db.orders.update_one(
                                {"id": order["id"]},
                                {"$set": order},
                                upsert=True
                            )
                        print(f"Migrated {len(orders)} orders")
                except Exception as e:
                    print(f"Error migrating orders: {e}")
                
                # Get dishes for each restaurant
                try:
                    restaurants = list(db.restaurants.find({}, {"id": 1, "_id": 0}))
                    total_dishes = 0
                    for restaurant in restaurants:
                        dishes_response = requests.get(f"{sql_base}/restaurants/{restaurant['id']}/dishes", timeout=10)
                        if dishes_response.status_code == 200:
                            dishes = dishes_response.json()
                            for dish in dishes:
                                # Remove _id field if it exists
                                dish.pop("_id", None)
                                # Add restaurant_id if not present
                                dish["restaurant_id"] = restaurant["id"]
                                # Update or insert dish
                                db.dishes.update_one(
                                    {"id": dish["id"]},
                                    {"$set": dish},
                                    upsert=True
                                )
                                total_dishes += 1
                    print(f"Migrated {total_dishes} dishes")
                except Exception as e:
                    print(f"Error migrating dishes: {e}")
                
                print("Migration completed successfully!")
                
            except Exception as e:
                print(f"Migration error: {e}")
        
        # Run migration in a separate thread to avoid blocking
        thread = threading.Thread(target=run_migration)
        thread.start()
        
        return jsonify({"message": "Migration started successfully"}), 200
        
    except Exception as e:
        return jsonify({"error": f"Migration failed: {str(e)}"}), 500

@app.route("/stats", methods=["GET"])
def get_stats():
    try:
        stats = {
            "users": db.users.count_documents({}),
            "restaurants": db.restaurants.count_documents({}),
            "dishes": db.dishes.count_documents({}),
            "carts": db.carts.count_documents({}),
            "orders": db.orders.count_documents({})
        }
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/users/<user_id>/prime/activate", methods=["POST"])
def activate_prime(user_id):
    """Activate Prime membership for a user"""
    data = request.get_json()
    
    # Check if user exists
    user = db.users.find_one({"id": int(user_id)})
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Check if user is already a Prime member
    existing_prime = db.prime_users.find_one({"user_id": int(user_id)})
    if existing_prime:
        return jsonify({"error": "User is already a Prime member"}), 409
    
    # Create PrimeUser record
    prime_user = {
        "user_id": int(user_id),
        "fee": data.get("fee", 9.99),
        "free_delivery": True
    }
    db.prime_users.insert_one(prime_user)
    
    # Create Member record
    member = {
        "user_id": int(user_id)
    }
    db.members.insert_one(member)
    
    # Create Prime subscription
    subscription_id = get_next_id("prime_subscriptions")
    subscription = {
        "id": subscription_id,
        "user_id": int(user_id),
        "start_date": datetime.datetime.now(),
        "monthly_fee": data.get("fee", 9.99),
        "is_active": True,
        "auto_renew": True
    }
    db.prime_subscriptions.insert_one(subscription)
    
    # Create initial payment record
    payment_id = get_next_id("payments")
    payment = {
        "id": payment_id,
        "user_id": int(user_id),
        "amount": data.get("fee", 9.99),
        "payment_method": "credit_card",  # Default method
        "payment_status": "completed",
        "payment_date": datetime.datetime.now(),
        "transaction_id": f"PRIME_{user_id}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
        "payment_description": "Prime Membership Activation"
    }
    db.payments.insert_one(payment)
    
    # Create Prime payment record
    prime_payment_id = get_next_id("prime_payments")
    prime_payment = {
        "id": prime_payment_id,
        "subscription_id": subscription_id,
        "payment_id": payment_id,
        "billing_period_start": datetime.datetime.now(),
        "billing_period_end": datetime.datetime.now() + datetime.timedelta(days=30),
        "due_date": datetime.datetime.now(),
        "paid_date": datetime.datetime.now()
    }
    db.prime_payments.insert_one(prime_payment)
    
    # Update user's free_delivery flag
    db.users.update_one(
        {"id": int(user_id)},
        {"$set": {"free_delivery": True, "is_prime": True}}
    )
    
    return jsonify({
        "message": "Prime membership activated successfully",
        "user_id": int(user_id),
        "subscription_id": subscription_id,
        "fee": prime_user["fee"],
        "free_delivery": True,
        "next_billing_date": (datetime.datetime.now() + datetime.timedelta(days=30)).isoformat()
    }), 201

@app.route("/users/<user_id>/prime/status", methods=["GET"])
def get_prime_status(user_id):
    user = db.users.find_one({"id": int(user_id)})
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    prime_user = db.prime_users.find_one({"user_id": int(user_id)})
    member = db.members.find_one({"user_id": int(user_id)})
    
    # Get active subscription
    subscription = db.prime_subscriptions.find_one({
        "user_id": int(user_id), 
        "is_active": True
    })
    
    return jsonify({
        "user_id": int(user_id),
        "is_prime": prime_user is not None,
        "is_member": member is not None,
        "free_delivery": user.get("free_delivery", False),
        "fee": prime_user.get("fee") if prime_user else None,
        "has_active_subscription": subscription is not None,
        "subscription_id": subscription.get("id") if subscription else None
    })

@app.route("/users/<user_id>/prime/cancel", methods=["POST"])
def cancel_prime(user_id):
    """Cancel Prime membership for a user"""
    data = request.get_json()
    
    try:
        # Check if user exists
        user = db.users.find_one({"id": int(user_id)})
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Check if user has Prime membership
        prime_user = db.prime_users.find_one({"user_id": int(user_id)})
        if not prime_user:
            return jsonify({"error": "User is not a Prime member"}), 404
        
        # Get active subscription
        subscription = db.prime_subscriptions.find_one({
            "user_id": int(user_id), 
            "is_active": True
        })
        
        if not subscription:
            return jsonify({"error": "No active Prime subscription found"}), 404
        
        # Cancel subscription
        cancellation_date = datetime.datetime.now()
        grace_period_end = cancellation_date + datetime.timedelta(days=30)
        
        db.prime_subscriptions.update_one(
            {"id": subscription["id"]},
            {
                "$set": {
                    "is_active": False,
                    "auto_renew": False,
                    "cancelled_date": cancellation_date,
                    "cancellation_reason": data.get("reason", "User requested cancellation"),
                    "end_date": grace_period_end
                }
            }
        )
        
        # Update user's Prime status
        db.users.update_one(
            {"id": int(user_id)},
            {
                "$set": {
                    "is_prime": False,
                    "free_delivery": False
                }
            }
        )
        
        # Remove PrimeUser record
        db.prime_users.delete_one({"user_id": int(user_id)})
        
        # Remove Member record
        db.members.delete_one({"user_id": int(user_id)})
        
        return jsonify({
            "message": "Prime membership cancelled successfully",
            "user_id": int(user_id),
            "cancellation_date": cancellation_date.isoformat(),
            "grace_period_end": grace_period_end.isoformat(),
            "reason": data.get("reason", "User requested cancellation")
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/users/<user_id>/payments", methods=["GET"])
def get_user_payments(user_id):
    """Get payment history for a user"""
    try:
        user = db.users.find_one({"id": int(user_id)})
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        payments = list(db.payments.find({"user_id": int(user_id)}).sort("payment_date", -1))
        
        payment_list = []
        for payment in payments:
            payment_data = {
                "id": payment["id"],
                "amount": payment["amount"],
                "payment_method": payment["payment_method"],
                "payment_status": payment["payment_status"],
                "payment_date": payment["payment_date"].isoformat() if isinstance(payment["payment_date"], datetime.datetime) else payment["payment_date"],
                "transaction_id": payment.get("transaction_id"),
                "description": payment["payment_description"],
                "order_id": payment.get("order_id")
            }
            
            # Check if this is a Prime payment
            prime_payment = db.prime_payments.find_one({"payment_id": payment["id"]})
            if prime_payment:
                payment_data["is_prime_payment"] = True
                payment_data["billing_period"] = {
                    "start": prime_payment["billing_period_start"].isoformat() if isinstance(prime_payment["billing_period_start"], datetime.datetime) else prime_payment["billing_period_start"],
                    "end": prime_payment["billing_period_end"].isoformat() if isinstance(prime_payment["billing_period_end"], datetime.datetime) else prime_payment["billing_period_end"]
                }
            else:
                payment_data["is_prime_payment"] = False
            
            payment_list.append(payment_data)
        
        return jsonify(payment_list), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/users/<user_id>/prime/subscription", methods=["GET"])
def get_prime_subscription(user_id):
    """Get Prime subscription details for a user"""
    try:
        user = db.users.find_one({"id": int(user_id)})
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        subscription = db.prime_subscriptions.find_one(
            {"user_id": int(user_id)}, 
            sort=[("start_date", -1)]
        )
        
        if not subscription:
            return jsonify({"error": "No Prime subscription found"}), 404
        
        # Get payment history for this subscription
        prime_payments = list(db.prime_payments.find({"subscription_id": subscription["id"]}))
        
        payment_history = []
        for pp in prime_payments:
            payment = db.payments.find_one({"id": pp["payment_id"]})
            if payment:
                payment_history.append({
                    "payment_date": payment["payment_date"].isoformat() if isinstance(payment["payment_date"], datetime.datetime) else payment["payment_date"],
                    "amount": payment["amount"],
                    "status": payment["payment_status"],
                    "billing_period": {
                        "start": pp["billing_period_start"].isoformat() if isinstance(pp["billing_period_start"], datetime.datetime) else pp["billing_period_start"],
                        "end": pp["billing_period_end"].isoformat() if isinstance(pp["billing_period_end"], datetime.datetime) else pp["billing_period_end"]
                    }
                })
        
        subscription_data = {
            "id": subscription["id"],
            "start_date": subscription["start_date"].isoformat() if isinstance(subscription["start_date"], datetime.datetime) else subscription["start_date"],
            "end_date": subscription["end_date"].isoformat() if subscription.get("end_date") and isinstance(subscription["end_date"], datetime.datetime) else subscription.get("end_date"),
            "monthly_fee": subscription["monthly_fee"],
            "is_active": subscription["is_active"],
            "auto_renew": subscription["auto_renew"],
            "cancelled_date": subscription["cancelled_date"].isoformat() if subscription.get("cancelled_date") and isinstance(subscription["cancelled_date"], datetime.datetime) else subscription.get("cancelled_date"),
            "cancellation_reason": subscription.get("cancellation_reason"),
            "payment_history": payment_history
        }
        
        return jsonify(subscription_data), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/payments", methods=["GET"])
def get_all_payments():
    """Get all payments for admin dashboard"""
    try:
        payments = list(db.payments.find().sort("payment_date", -1).limit(100))
        
        payment_list = []
        for payment in payments:
            user = db.users.find_one({"id": payment["user_id"]})
            
            payment_data = {
                "id": payment["id"],
                "user_name": f"{user['first_name']} {user['last_name']}" if user else "Unknown",
                "amount": payment["amount"],
                "payment_method": payment["payment_method"],
                "payment_status": payment["payment_status"],
                "payment_date": payment["payment_date"].isoformat() if isinstance(payment["payment_date"], datetime.datetime) else payment["payment_date"],
                "description": payment["payment_description"],
                "order_id": payment.get("order_id")
            }
            
            # Check if this is a Prime payment
            prime_payment = db.prime_payments.find_one({"payment_id": payment["id"]})
            payment_data["is_prime_payment"] = prime_payment is not None
            
            payment_list.append(payment_data)
        
        return jsonify(payment_list), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/reports/prime-statistics/<user_id>", methods=["GET"])
def get_prime_statistics_report(user_id):
    """Enhanced analytics report for Prime customer with statistics"""
    try:
        # Get user data
        user = db.users.find_one({"id": int(user_id)})
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        prime_user = db.prime_users.find_one({"user_id": int(user_id)})
        if not prime_user:
            return jsonify({"error": "User is not a Prime member"}), 404
        
        # Get orders for this user
        orders = list(db.orders.find({"user_id": int(user_id)}))
        
        if not orders:
            return jsonify({"message": "No orders found for this user"}), 404
        
        # Calculate statistics
        total_orders = len(orders)
        total_paid = sum(order.get("total", 0) for order in orders)
        total_delivery_fees = sum(order.get("delivery_fee", 0) for order in orders)
        saved_fees = sum(order.get("delivery_fee", 0) for order in orders if not order.get("was_prime_order", False))
        avg_order = total_paid / total_orders if total_orders > 0 else 0
        
        # Get order items count
        order_items_count = 0
        total_food_price = 0
        for order in orders:
            items = list(db.order_items.find({"cart_id": order.get("cart_id")}))
            order_items_count += len(items)
            total_food_price += sum(item.get("total_price", 0) for item in items)
        
        return jsonify({
            "user_id": int(user_id),
            "first_name": user.get("first_name"),
            "last_name": user.get("last_name"),
            "free_delivery": prime_user.get("free_delivery", True),
            "statistics": {
                "total_orders": total_orders,
                "total_dishes": order_items_count,
                "total_food_price": total_food_price,
                "total_delivery_fees": total_delivery_fees,
                "total_paid": total_paid,
                "average_order": avg_order,
                "saved_fees": saved_fees
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/orders", methods=["GET"])
def get_all_orders():
    """Get all orders with details"""
    try:
        orders = list(db.orders.find({}, {"_id": 0}))
        
        # Enrich orders with additional details
        for order in orders:
            # Get user details
            user = db.users.find_one({"id": order.get("user_id")}, {"_id": 0})
            if user:
                order["user_name"] = f"{user.get('first_name', '')} {user.get('last_name', '')}"
            
            # Get restaurant details
            restaurant = db.restaurants.find_one({"id": order.get("restaurant_id")}, {"_id": 0})
            if restaurant:
                order["restaurant_name"] = restaurant.get("name")
            
            # Get supplier details - return as 'supplier' for frontend compatibility
            supplier_name = "Unassigned"
            if order.get("supplier_id"):
                supplier = db.suppliers.find_one({"id": order.get("supplier_id")}, {"_id": 0})
                if supplier:
                    supplier_name = supplier.get("name")
            order["supplier"] = supplier_name
            
            # Ensure proper order calculations
            subtotal = order.get("subtotal", 0)
            delivery_fee = order.get("delivery_fee", 3.99)
            total = order.get("total", subtotal + delivery_fee)
            
            # Fix calculations if inconsistent
            if abs(total - (subtotal + delivery_fee)) > 0.01:  # Allow small floating point differences
                if subtotal > 0:
                    # If subtotal exists, recalculate total
                    total = subtotal + delivery_fee
                else:
                    # If no subtotal, calculate from total
                    subtotal = max(0, total - delivery_fee)
            
            order["subtotal"] = round(subtotal, 2)
            order["delivery_fee"] = round(delivery_fee, 2)
            order["total"] = round(total, 2)
            
            # Ensure boolean fields
            order["was_prime_order"] = bool(order.get("was_prime_order", False))
        
        return jsonify(orders), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/users/<user_id>/orders", methods=["GET"])
def get_user_orders(user_id):
    """Get orders for a specific user"""
    try:
        orders = list(db.orders.find({"user_id": int(user_id)}, {"_id": 0}))
        
        # Enrich orders with additional details
        for order in orders:
            # Get restaurant details
            restaurant = db.restaurants.find_one({"id": order.get("restaurant_id")}, {"_id": 0})
            if restaurant:
                order["restaurant_name"] = restaurant.get("name")
            
            # Get supplier details - return as 'supplier' for frontend compatibility
            supplier_name = "Unassigned"
            if order.get("supplier_id"):
                supplier = db.suppliers.find_one({"id": order.get("supplier_id")}, {"_id": 0})
                if supplier:
                    supplier_name = supplier.get("name")
            order["supplier"] = supplier_name
            
            # Ensure proper order calculations
            subtotal = order.get("subtotal", 0)
            delivery_fee = order.get("delivery_fee", 3.99)
            total = order.get("total", subtotal + delivery_fee)
            
            # Fix calculations if inconsistent
            if abs(total - (subtotal + delivery_fee)) > 0.01:  # Allow small floating point differences
                if subtotal > 0:
                    # If subtotal exists, recalculate total
                    total = subtotal + delivery_fee
                else:
                    # If no subtotal, calculate from total
                    subtotal = max(0, total - delivery_fee)
            
            order["subtotal"] = round(subtotal, 2)
            order["delivery_fee"] = round(delivery_fee, 2)
            order["total"] = round(total, 2)
            
            # Ensure boolean fields
            order["was_prime_order"] = bool(order.get("was_prime_order", False))
            
            # Get order items for additional validation
            items = list(db.order_items.find({"cart_id": order.get("cart_id")}, {"_id": 0}))
            order["items"] = items
            
            # Validate subtotal against items if available
            if items:
                calculated_subtotal = sum(item.get("total_price", 0) for item in items)
                if calculated_subtotal > 0 and abs(order["subtotal"] - calculated_subtotal) > 0.01:
                    # Update subtotal based on items
                    order["subtotal"] = round(calculated_subtotal, 2)
                    order["total"] = round(calculated_subtotal + order["delivery_fee"], 2)
        
        return jsonify(orders), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/signin", methods=["POST"])
def signin():
    """Sign in endpoint for MongoDB backend"""
    data = request.get_json()
    
    if not all(k in data for k in ("email", "password")):
        return jsonify({"error": "Missing email or password"}), 400
    
    user = db.users.find_one({"email": data["email"]})
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Simple password check (in production, use proper hashing)
    if user.get("password_hash") != data["password"]:  # Simplified for demo
        return jsonify({"error": "Incorrect password"}), 401
    
    return jsonify({
        "message": "Login successful",
        "user": {
            "id": user["id"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "email": user["email"]
        }
    }), 200

@app.route("/signup", methods=["POST"])
def signup():
    """Sign up endpoint for MongoDB backend"""
    data = request.get_json()
    
    if not all(k in data for k in ("first_name", "last_name", "email", "password")):
        return jsonify({"error": "Missing required fields"}), 400
    
    if data["password"] != data["confirm_password"]:
        return jsonify({"error": "Passwords do not match"}), 400
    
    # Check if user already exists
    existing_user = db.users.find_one({"email": data["email"]})
    if existing_user:
        return jsonify({"error": "Email already registered"}), 409
    
    # Get next user ID
    max_user_id = 1
    existing_users = list(db.users.find({}, {"id": 1, "_id": 0}))
    if existing_users:
        max_user_id = max([user.get("id", 0) for user in existing_users]) + 1
    
    # Create new user
    new_user = {
        "id": max_user_id,
        "first_name": data["first_name"],
        "last_name": data["last_name"],
        "email": data["email"],
        "password_hash": data["password"],  # Simplified for demo
        "city": data.get("city"),
        "street": data.get("street"),
        "zipcode": data.get("zipcode"),
        "promo_code": None,
        "free_delivery": False,
        "cart_id": None,
        "invited_by_id": None
    }
    
    db.users.insert_one(new_user)
    
    return jsonify({"message": "User created successfully"}), 201

# Enhanced ID management
def get_next_id(collection_name):
    """Get next available ID for a collection with consistency"""
    # Get ID from sequence collection
    sequence = db.id_sequences.find_one({"_id": "sequences"})
    
    if not sequence:
        # Initialize sequences
        max_ids = {}
        for coll in ["carts", "order_items", "orders"]:
            existing = list(db[coll].find({}, {"id": 1, "_id": 0}))
            max_ids[f"{coll}_id"] = max([item.get("id", 0) for item in existing]) + 1 if existing else 1
        
        db.id_sequences.insert_one({
            "_id": "sequences",
            **max_ids,
            "last_sync": datetime.datetime.now().isoformat()
        })
        sequence = db.id_sequences.find_one({"_id": "sequences"})
    
    # Get and increment the appropriate counter
    field_name = f"{collection_name}_id"
    current_id = sequence.get(field_name, 1)
    
    # Update the sequence
    db.id_sequences.update_one(
        {"_id": "sequences"},
        {"$inc": {field_name: 1}}
    )
    
    return current_id

@app.route("/admin/sync-user", methods=["POST"])
def sync_user():
    """Sync user from SQL to MongoDB"""
    data = request.get_json()
    try:
        # Update or insert user
        db.users.update_one(
            {"id": data["id"]},
            {"$set": data},
            upsert=True
        )
        return jsonify({"message": "User synced successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/admin/sync-order", methods=["POST"])
def sync_order():
    """Sync order from SQL to MongoDB"""
    data = request.get_json()
    try:
        # Ensure proper data types
        if "delivery_fee" in data:
            data["delivery_fee"] = float(data["delivery_fee"])
        if "subtotal" in data:
            data["subtotal"] = float(data["subtotal"])
        if "total" in data:
            data["total"] = float(data["total"])
        if "was_prime_order" in data:
            data["was_prime_order"] = bool(data["was_prime_order"])
        
        # Update or insert order
        db.orders.update_one(
            {"id": data["id"]},
            {"$set": data},
            upsert=True
        )
        return jsonify({"message": "Order synced successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/admin/sync-payment", methods=["POST"])
def sync_payment():
    """Sync payment from SQL to MongoDB"""
    data = request.get_json()
    try:
        # Ensure proper data types
        if "amount" in data:
            data["amount"] = float(data["amount"])
        
        # Update or insert payment
        db.payments.update_one(
            {"id": data["id"]},
            {"$set": data},
            upsert=True
        )
        return jsonify({"message": "Payment synced successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/admin/sync-cart", methods=["POST"])
def sync_cart():
    """Sync cart from SQL to MongoDB"""
    data = request.get_json()
    try:
        # Update or insert cart
        db.carts.update_one(
            {"id": data["id"]},
            {"$set": data},
            upsert=True
        )
        return jsonify({"message": "Cart synced successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/admin/migrate", methods=["POST"])
def admin_migrate():
    """Handle migration request from SQL backend (for compatibility)"""
    try:
        # This endpoint is called by SQL backend when switching to MongoDB
        # We don't need to do anything special here since the SQL backend
        # will send data via the sync endpoints
        return jsonify({"message": "Migration endpoint ready - SQL backend will sync data"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/admin/sync-restaurant", methods=["POST"])
def sync_restaurant():
    """Sync restaurant from SQL to MongoDB"""
    data = request.get_json()
    try:
        # Update or insert restaurant
        db.restaurants.update_one(
            {"id": data["id"]},
            {"$set": data},
            upsert=True
        )
        return jsonify({"message": "Restaurant synced successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/admin/sync-dish", methods=["POST"])
def sync_dish():
    """Sync dish from SQL to MongoDB"""
    data = request.get_json()
    try:
        # Ensure proper data types
        if "price" in data:
            data["price"] = float(data["price"])
        
        # Update or insert dish
        db.dishes.update_one(
            {"id": data["id"]},
            {"$set": data},
            upsert=True
        )
        return jsonify({"message": "Dish synced successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001) 