from flask import Flask, request, jsonify
from db import SessionLocal, engine
from models import User, Restaurant, Dish, Cart, OrderItem, CartState, PrimeUser, Member, Order, Supplier, Payment, PaymentMethod, PaymentStatus, PrimeSubscription, PrimePayment
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
from db import Base
import datetime
import random
import requests

app = Flask(__name__)
Base.metadata.create_all(bind=engine)

@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()

    if not all(k in data for k in ("first_name", "last_name", "email", "password")):
        return jsonify({"error": "Missing required fields"}), 400
    
    if data["password"] != data["confirm_password"]:
        return jsonify({"error" : "Passwords do not math"}), 400

    new_user = User(
        first_name=data["first_name"],
        last_name=data["last_name"],
        email=data["email"],
        city=data.get("city"),
        street=data.get("street"),
        zipcode=data.get("zipcode"),
    )

    new_user.set_password(data["password"])


    session = SessionLocal()
    try:
        session.add(new_user)
        session.commit()
        return jsonify({"message": "User created successfully"}), 201
    except IntegrityError:
        session.rollback()
        return jsonify({"error": "Email already registered"}), 409
    finally:
        session.close()

@app.route("/signin", methods=["POST"])
def signin():
    data = request.get_json()

    if not all(k in data for k in ("email", "password")):
        return jsonify({"error": "Missing email or password"}), 400

    session = SessionLocal()
    
    try:
        user = session.query(User).filter_by(email=data["email"]).first()
        if user is None:
            return jsonify({"error": "User not found"}), 404

        if not user.check_password(data["password"]):
            return jsonify({"error": "Incorrect password"}), 401

        return jsonify({
            "message": "Login successful",
            "user": {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email
            }
        }), 200
    finally:
        session.close()

@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    session = SessionLocal()
    try:
        restaurants = session.query(Restaurant).all()
        result = []
        for restaurant in restaurants:
            result.append({
                "id": restaurant.id,
                "name": restaurant.name,
                "open_from": restaurant.open_from.strftime("%H:%M"),
                "open_till": restaurant.open_till.strftime("%H:%M"),
                "city": restaurant.city,
                "street": restaurant.street,
                "zipcode": restaurant.zipcode,
                "address": f"{restaurant.street}, {restaurant.city}, {restaurant.zipcode}"  # Keep for backward compatibility
            })
        return jsonify(result), 200
    finally:
        session.close()

@app.route("/restaurants/<int:restaurant_id>", methods=["GET"])
def get_restaurant(restaurant_id):
    session = SessionLocal()
    try:
        restaurant = session.query(Restaurant).filter_by(id=restaurant_id).first()
        if restaurant is None:
            return jsonify({"error": "Restaurant not found"}), 404
        
        return jsonify({
            "id": restaurant.id,
            "name": restaurant.name,
            "open_from": restaurant.open_from.strftime("%H:%M"),
            "open_till": restaurant.open_till.strftime("%H:%M"),
            "city": restaurant.city,
            "street": restaurant.street,
            "zipcode": restaurant.zipcode
        }), 200
    finally:
        session.close()

@app.route("/restaurants/<int:restaurant_id>/dishes", methods=["GET"])
def get_restaurant_dishes(restaurant_id):
    session = SessionLocal()
    try:
        dishes = session.query(Dish).filter_by(restaurant_id=restaurant_id).all()
        result = []
        for dish in dishes:
            result.append({
                "id": dish.id,
                "name": dish.name,
                "price": float(dish.price)
            })
        return jsonify(result), 200
    finally:
        session.close()

@app.route("/carts", methods=["POST"])
def create_cart():
    data = request.get_json()
    
    if "restaurant_id" not in data:
        return jsonify({"error": "Missing restaurant_id"}), 400
    
    session = SessionLocal()
    try:
        restaurant = session.query(Restaurant).filter_by(id=data["restaurant_id"]).first()
        if restaurant is None:
            return jsonify({"error": "Restaurant not found"}), 404
        
        new_cart = Cart(
            created_at=datetime.datetime.now(),
            restaurant_id=data["restaurant_id"],
            state=CartState.OPEN
        )
        
        session.add(new_cart)
        session.commit()
        
        return jsonify({
            "id": new_cart.id,
            "restaurant_id": new_cart.restaurant_id,
            "created_at": new_cart.created_at.isoformat(),
            "state": new_cart.state.value
        }), 201
    finally:
        session.close()

@app.route("/carts/<int:cart_id>/items", methods=["POST"])
def add_cart_item(cart_id):
    data = request.get_json()
    
    if not all(k in data for k in ("dish_id", "quantity")):
        return jsonify({"error": "Missing dish_id or quantity"}), 400
    
    session = SessionLocal()
    try:
        cart = session.query(Cart).filter_by(id=cart_id).first()
        if cart is None:
            return jsonify({"error": "Cart not found"}), 404
        
        dish = session.query(Dish).filter_by(id=data["dish_id"]).first()
        if dish is None:
            return jsonify({"error": "Dish not found"}), 404
        
        # Check if item already exists in cart
        item = session.query(OrderItem).filter_by(
            warenkorb_id=cart_id, 
            gericht_id=data["dish_id"]
        ).first()
        
        if item:
            # Update quantity if item exists
            item.quantity += data["quantity"]
            item.total_price = float(dish.price) * item.quantity
        else:
            # Create new item
            item = OrderItem(
                warenkorb_id=cart_id,
                gericht_id=data["dish_id"],
                quantity=data["quantity"],
                total_price=float(dish.price) * data["quantity"],
                restaurant_address=f"{dish.restaurant.street}, {dish.restaurant.city}, {dish.restaurant.zipcode}"
            )
            session.add(item)
        
        session.commit()
        
        return jsonify({
            "id": item.id,
            "cart_id": item.warenkorb_id,
            "dish_id": item.gericht_id,
            "quantity": item.quantity,
            "total_price": float(item.total_price)
        }), 201
    finally:
        session.close()

@app.route("/carts/<int:cart_id>", methods=["GET"])
def get_cart(cart_id):
    session = SessionLocal()
    try:
        cart = session.query(Cart).filter_by(id=cart_id).first()
        if cart is None:
            return jsonify({"error": "Cart not found"}), 404
        
        items = session.query(OrderItem).filter_by(warenkorb_id=cart_id).all()
        items_data = []
        
        total = 0.0
        for item in items:
            dish = session.query(Dish).filter_by(id=item.gericht_id).first()
            item_data = {
                "id": item.id,
                "dish_id": item.gericht_id,
                "dish_name": dish.name if dish else "Unknown",
                "quantity": item.quantity,
                "price": float(dish.price) if dish else 0.0,
                "total_price": float(item.total_price)
            }
            items_data.append(item_data)
            total += float(item.total_price)
        
        return jsonify({
            "id": cart.id,
            "restaurant_id": cart.restaurant_id,
            "created_at": cart.created_at.isoformat(),
            "state": cart.state.value,
            "items": items_data,
            "total": total
        }), 200
    finally:
        session.close()

@app.route("/carts/<int:cart_id>/checkout", methods=["POST"])
def checkout_cart(cart_id):
    data = request.get_json()
    
    if "user_id" not in data:
        return jsonify({"error": "Missing user_id"}), 400
    
    session = SessionLocal()
    try:
        cart = session.query(Cart).filter_by(id=cart_id).first()
        if cart is None:
            return jsonify({"error": "Cart not found"}), 404
        
        user = session.query(User).filter_by(id=data["user_id"]).first()
        if user is None:
            return jsonify({"error": "User not found"}), 404
        
        # Check Prime status for delivery fee calculation
        prime_user = session.query(PrimeUser).filter_by(user_id=data["user_id"]).first()
        is_prime = prime_user is not None
        delivery_fee = 0.0 if is_prime else 3.99  # Free delivery for Prime members
        
        # Calculate total with delivery fee
        items = session.query(OrderItem).filter_by(warenkorb_id=cart_id).all()
        subtotal = sum(float(item.total_price) for item in items)
        total = subtotal + delivery_fee
        
        # Assign random supplier
        suppliers = session.query(Supplier).all()
        assigned_supplier = random.choice(suppliers) if suppliers else None
        
        # Create Order record with proper tracking
        order = Order(
            user_id=data["user_id"],
            restaurant_id=cart.restaurant_id,
            cart_id=cart_id,
            supplier_id=assigned_supplier.id if assigned_supplier else None,
            order_date=datetime.datetime.now(),
            delivery_fee=delivery_fee,
            subtotal=subtotal,
            total=total,
            was_prime_order=is_prime,
            status=CartState.IN_PREPARATION,
            estimated_delivery=datetime.datetime.now() + datetime.timedelta(minutes=30)
        )
        session.add(order)
        
        # Update cart state
        cart.state = CartState.IN_PREPARATION
        
        session.commit()
        
        return jsonify({
            "message": "Order placed successfully",
            "order_id": order.id,
            "cart_id": cart.id,
            "state": cart.state.value,
            "subtotal": subtotal,
            "delivery_fee": delivery_fee,
            "total": total,
            "is_prime_order": is_prime,
            "supplier": assigned_supplier.name if assigned_supplier else "Unassigned",
            "estimated_delivery": order.estimated_delivery.isoformat()
        }), 200
    finally:
        session.close()

@app.route("/stats", methods=["GET"])
def get_stats():
    session = SessionLocal()
    try:
        stats = {
            "users": session.query(User).count(),
            "restaurants": session.query(Restaurant).count(),
            "dishes": session.query(Dish).count(),
            "carts": session.query(Cart).count(),
            "orders": session.query(Order).count()
        }
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

# Prime Membership Endpoints

@app.route("/users/<int:user_id>/prime/activate", methods=["POST"])
def activate_prime(user_id):
    """Activate Prime membership for a user"""
    data = request.get_json()
    
    session = SessionLocal()
    try:
        # Check if user exists
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Check if user is already a Prime member
        existing_prime = session.query(PrimeUser).filter_by(user_id=user_id).first()
        if existing_prime:
            return jsonify({"error": "User is already a Prime member"}), 409
        
        # Create PrimeUser record
        prime_user = PrimeUser(
            user_id=user_id,
            fee=data.get("fee", 9.99),
            free_delivery=True
        )
        session.add(prime_user)
        
        # Create Member record
        member = Member(user_id=user_id)
        session.add(member)
        
        # Create Prime subscription
        subscription = PrimeSubscription(
            user_id=user_id,
            monthly_fee=data.get("fee", 9.99),
            start_date=datetime.datetime.now(),
            is_active=True,
            auto_renew=True
        )
        session.add(subscription)
        
        # Create initial payment record
        payment = Payment(
            user_id=user_id,
            amount=data.get("fee", 9.99),
            payment_method=PaymentMethod.CREDIT_CARD,  # Default method
            payment_status=PaymentStatus.COMPLETED,
            payment_description="Prime Membership Activation",
            transaction_id=f"PRIME_{user_id}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        )
        session.add(payment)
        session.flush()  # Get payment ID
        
        # Create Prime payment record
        prime_payment = PrimePayment(
            subscription_id=subscription.id,
            payment_id=payment.id,
            billing_period_start=datetime.datetime.now(),
            billing_period_end=datetime.datetime.now() + datetime.timedelta(days=30),
            due_date=datetime.datetime.now(),
            paid_date=datetime.datetime.now()
        )
        session.add(prime_payment)
        
        # Update user's free_delivery flag
        user.free_delivery = True
        
        session.commit()
        
        return jsonify({
            "message": "Prime membership activated successfully",
            "user_id": user_id,
            "subscription_id": subscription.id,
            "fee": float(prime_user.fee),
            "free_delivery": True,
            "next_billing_date": (datetime.datetime.now() + datetime.timedelta(days=30)).isoformat()
        }), 201
        
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route("/users/<int:user_id>/prime/cancel", methods=["POST"])
def cancel_prime(user_id):
    """Cancel Prime membership for a user"""
    data = request.get_json()
    
    session = SessionLocal()
    try:
        # Check if user exists
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Check if user has Prime membership
        prime_user = session.query(PrimeUser).filter_by(user_id=user_id).first()
        if not prime_user:
            return jsonify({"error": "User is not a Prime member"}), 404
        
        # Get active subscription
        subscription = session.query(PrimeSubscription).filter_by(
            user_id=user_id, 
            is_active=True
        ).first()
        
        if not subscription:
            return jsonify({"error": "No active Prime subscription found"}), 404
        
        # Cancel subscription
        subscription.is_active = False
        subscription.auto_renew = False
        subscription.cancelled_date = datetime.datetime.now()
        subscription.cancellation_reason = data.get("reason", "User requested cancellation")
        subscription.end_date = datetime.datetime.now() + datetime.timedelta(days=30)  # Grace period
        
        # Update user's free_delivery flag (will be disabled after grace period)
        user.free_delivery = False
        
        # Remove PrimeUser record
        session.delete(prime_user)
        
        # Remove Member record
        member = session.query(Member).filter_by(user_id=user_id).first()
        if member:
            session.delete(member)
        
        session.commit()
        
        return jsonify({
            "message": "Prime membership cancelled successfully",
            "user_id": user_id,
            "cancellation_date": subscription.cancelled_date.isoformat(),
            "grace_period_end": subscription.end_date.isoformat(),
            "reason": subscription.cancellation_reason
        }), 200
        
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route("/users/<int:user_id>/payments", methods=["GET"])
def get_user_payments(user_id):
    """Get payment history for a user"""
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        payments = session.query(Payment).filter_by(user_id=user_id).order_by(Payment.payment_date.desc()).all()
        
        payment_list = []
        for payment in payments:
            payment_data = {
                "id": payment.id,
                "amount": float(payment.amount),
                "payment_method": payment.payment_method.value,
                "payment_status": payment.payment_status.value,
                "payment_date": payment.payment_date.isoformat(),
                "transaction_id": payment.transaction_id,
                "description": payment.payment_description,
                "order_id": payment.order_id
            }
            
            # Check if this is a Prime payment
            prime_payment = session.query(PrimePayment).filter_by(payment_id=payment.id).first()
            if prime_payment:
                payment_data["is_prime_payment"] = True
                payment_data["billing_period"] = {
                    "start": prime_payment.billing_period_start.isoformat(),
                    "end": prime_payment.billing_period_end.isoformat()
                }
            else:
                payment_data["is_prime_payment"] = False
            
            payment_list.append(payment_data)
        
        return jsonify(payment_list), 200
        
    finally:
        session.close()

@app.route("/users/<int:user_id>/prime/subscription", methods=["GET"])
def get_prime_subscription(user_id):
    """Get Prime subscription details for a user"""
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        subscription = session.query(PrimeSubscription).filter_by(user_id=user_id).order_by(PrimeSubscription.start_date.desc()).first()
        
        if not subscription:
            return jsonify({"error": "No Prime subscription found"}), 404
        
        # Get payment history for this subscription
        prime_payments = session.query(PrimePayment).filter_by(subscription_id=subscription.id).all()
        
        payment_history = []
        for pp in prime_payments:
            payment = session.query(Payment).filter_by(id=pp.payment_id).first()
            if payment:
                payment_history.append({
                    "payment_date": payment.payment_date.isoformat(),
                    "amount": float(payment.amount),
                    "status": payment.payment_status.value,
                    "billing_period": {
                        "start": pp.billing_period_start.isoformat(),
                        "end": pp.billing_period_end.isoformat()
                    }
                })
        
        subscription_data = {
            "id": subscription.id,
            "start_date": subscription.start_date.isoformat(),
            "end_date": subscription.end_date.isoformat() if subscription.end_date else None,
            "monthly_fee": float(subscription.monthly_fee),
            "is_active": subscription.is_active,
            "auto_renew": subscription.auto_renew,
            "cancelled_date": subscription.cancelled_date.isoformat() if subscription.cancelled_date else None,
            "cancellation_reason": subscription.cancellation_reason,
            "payment_history": payment_history
        }
        
        return jsonify(subscription_data), 200
        
    finally:
        session.close()

@app.route("/payments", methods=["GET"])
def get_all_payments():
    """Get all payments for admin dashboard"""
    session = SessionLocal()
    try:
        payments = session.query(Payment).order_by(Payment.payment_date.desc()).limit(100).all()
        
        payment_list = []
        for payment in payments:
            user = session.query(User).filter_by(id=payment.user_id).first()
            
            payment_data = {
                "id": payment.id,
                "user_name": f"{user.first_name} {user.last_name}" if user else "Unknown",
                "amount": float(payment.amount),
                "payment_method": payment.payment_method.value,
                "payment_status": payment.payment_status.value,
                "payment_date": payment.payment_date.isoformat(),
                "description": payment.payment_description,
                "order_id": payment.order_id
            }
            
            # Check if this is a Prime payment
            prime_payment = session.query(PrimePayment).filter_by(payment_id=payment.id).first()
            payment_data["is_prime_payment"] = prime_payment is not None
            
            payment_list.append(payment_data)
        
        return jsonify(payment_list), 200
        
    finally:
        session.close()

@app.route("/reports/prime-statistics/<int:user_id>", methods=["GET"])
def get_prime_statistics_report(user_id):
    """Enhanced analytics report for Prime customer with statistics (addressing M1 feedback)"""
    session = SessionLocal()
    try:
        # Enhanced query with statistics as requested in M1 feedback
        query = text("""
        SELECT
            u.first_name as Vorname,
            u.last_name as Nachname,
            pu.free_delivery as GratisLieferung,
            COUNT(DISTINCT o.id) as AnzahlBestellungen,
            COUNT(oi.id) as AnzahlGerichte,
            SUM(d.price * oi.quantity) as GesamtEssenPreis,
            SUM(o.delivery_fee) as GesamtLiefergebuehren,
            SUM(o.total) as GesamtBezahlt,
            AVG(o.total) as DurchschnittBestellung,
            SUM(CASE WHEN o.was_prime_order = 1 THEN 0 ELSE o.delivery_fee END) as ErsparteGebuehren
        FROM
            member m
        JOIN user u ON m.user_id = u.id
        JOIN primeUser pu ON m.user_id = pu.user_id
        JOIN `order` o ON u.id = o.user_id
        JOIN cart c ON o.cart_id = c.id
        JOIN orderitem oi ON c.id = oi.warenkorb_id
        JOIN dish d ON oi.gericht_id = d.id
        WHERE
            u.id = :user_id
        GROUP BY
            u.first_name, u.last_name, pu.free_delivery
        """)
        
        result = session.execute(query, {"user_id": user_id}).fetchone()
        
        if not result:
            return jsonify({"message": "No Prime orders found for this user"}), 404
        
        return jsonify({
            "user_id": user_id,
            "first_name": result.Vorname,
            "last_name": result.Nachname,
            "free_delivery": result.GratisLieferung,
            "statistics": {
                "total_orders": result.AnzahlBestellungen,
                "total_dishes": result.AnzahlGerichte,
                "total_food_cost": float(result.GesamtEssenPreis),
                "total_delivery_fees_paid": float(result.GesamtLiefergebuehren),  # Historical fees
                "total_amount_paid": float(result.GesamtBezahlt),
                "average_order_value": float(result.DurchschnittBestellung),
                "delivery_fees_saved": float(result.ErsparteGebuehren)
            }
        }), 200
        
    finally:
        session.close()

@app.route("/orders", methods=["GET"])
def get_all_orders():
    """Get all orders with delivery information"""
    session = SessionLocal()
    try:
        orders = session.query(Order).all()
        result = []
        
        for order in orders:
            # Get supplier info
            supplier_name = "Unassigned"
            if order.supplier_id:
                supplier = session.query(Supplier).filter_by(id=order.supplier_id).first()
                supplier_name = supplier.name if supplier else "Unknown"
            
            result.append({
                "id": order.id,
                "user_name": f"{order.user.first_name} {order.user.last_name}",
                "restaurant_name": order.restaurant.name,
                "order_date": order.order_date.isoformat(),
                "subtotal": float(order.subtotal),
                "delivery_fee": float(order.delivery_fee),
                "total": float(order.total),
                "was_prime_order": order.was_prime_order,
                "status": order.status.value,
                "supplier": supplier_name,
                "estimated_delivery": order.estimated_delivery.isoformat() if order.estimated_delivery else None,
                "actual_delivery": order.actual_delivery.isoformat() if order.actual_delivery else None
            })
        
        return jsonify(result), 200
    finally:
        session.close()

@app.route("/users/<int:user_id>/orders", methods=["GET"])
def get_user_orders(user_id):
    """Get orders for a specific user"""
    session = SessionLocal()
    try:
        orders = session.query(Order).filter_by(user_id=user_id).all()
        result = []
        
        for order in orders:
            # Get supplier info
            supplier_name = "Unassigned"
            if order.supplier_id:
                supplier = session.query(Supplier).filter_by(id=order.supplier_id).first()
                supplier_name = supplier.name if supplier else "Unknown"
            
            result.append({
                "id": order.id,
                "restaurant_name": order.restaurant.name,
                "order_date": order.order_date.isoformat(),
                "subtotal": float(order.subtotal),
                "delivery_fee": float(order.delivery_fee),
                "total": float(order.total),
                "was_prime_order": order.was_prime_order,
                "status": order.status.value,
                "supplier": supplier_name,
                "estimated_delivery": order.estimated_delivery.isoformat() if order.estimated_delivery else None
            })
        
        return jsonify(result), 200
    finally:
        session.close()

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    try:
        session = SessionLocal()
        # Simple query to test database connection
        session.execute(text("SELECT 1"))
        session.close()
        return jsonify({
            "status": "healthy", 
            "backend": "SQL",
            "timestamp": datetime.datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy", 
            "backend": "SQL",
            "error": str(e),
            "timestamp": datetime.datetime.now().isoformat()
        }), 500

@app.route("/migrate", methods=["POST"])
def trigger_migration():
    """Trigger migration from MongoDB to SQL"""
    try:
        # Import and run migration
        import subprocess
        import os
        
        # Change to mongo_backend directory and run migration
        mongo_backend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mongo_backend")
        result = subprocess.run(
            ["python", "migrate.py"],
            cwd=mongo_backend_path,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return jsonify({
                "message": "Migration completed successfully",
                "output": result.stdout
            }), 200
        else:
            return jsonify({
                "error": "Migration failed",
                "output": result.stderr
            }), 500
            
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Migration timed out"}), 500
    except Exception as e:
        return jsonify({"error": f"Migration error: {str(e)}"}), 500

@app.route("/users/<int:user_id>/prime/status", methods=["GET"])
def get_prime_status(user_id):
    """Check if user has Prime membership"""
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        prime_user = session.query(PrimeUser).filter_by(user_id=user_id).first()
        member = session.query(Member).filter_by(user_id=user_id).first()
        
        # Get active subscription
        subscription = session.query(PrimeSubscription).filter_by(
            user_id=user_id, 
            is_active=True
        ).first()
        
        return jsonify({
            "user_id": user_id,
            "is_prime": prime_user is not None,
            "is_member": member is not None,
            "free_delivery": user.free_delivery,
            "fee": float(prime_user.fee) if prime_user else None,
            "has_active_subscription": subscription is not None,
            "subscription_id": subscription.id if subscription else None
        }), 200
        
    finally:
        session.close()

@app.route("/admin/import-data", methods=["POST"])
def import_data():
    """Import randomized data for testing (M2 requirement 2.2.1)"""
    try:
        from data_import import generate_sample_data
        generate_sample_data()
        return jsonify({"message": "Data import completed successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Data import failed: {str(e)}"}), 500

@app.route("/admin/migrate", methods=["POST"])
def migrate_to_mongo():
    """Migrate data from SQL to MongoDB"""
    try:
        import requests
        
        session = SessionLocal()
        mongo_base = "http://mongo-backend:5001"
        
        try:
            # Migrate restaurants first
            restaurants = session.query(Restaurant).all()
            for restaurant in restaurants:
                restaurant_data = {
                    "id": restaurant.id,
                    "name": restaurant.name,
                    "street": restaurant.street,
                    "city": restaurant.city,
                    "zipcode": restaurant.zipcode,
                    "open_from": restaurant.open_from.strftime("%H:%M:%S") if restaurant.open_from else None,
                    "open_till": restaurant.open_till.strftime("%H:%M:%S") if restaurant.open_till else None
                }
                
                # Send to MongoDB
                try:
                    requests.post(f"{mongo_base}/admin/sync-restaurant", json=restaurant_data, timeout=10)
                except Exception as e:
                    print(f"Error syncing restaurant {restaurant.id}: {e}")
            
            # Migrate dishes
            dishes = session.query(Dish).all()
            for dish in dishes:
                dish_data = {
                    "id": dish.id,
                    "name": dish.name,
                    "price": float(dish.price),
                    "restaurant_id": dish.restaurant_id
                }
                
                # Send to MongoDB
                try:
                    requests.post(f"{mongo_base}/admin/sync-dish", json=dish_data, timeout=10)
                except Exception as e:
                    print(f"Error syncing dish {dish.id}: {e}")
            
            # Migrate users
            users = session.query(User).all()
            for user in users:
                user_data = {
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "password_hash": user.password_hash,
                    "city": user.city,
                    "street": user.street,
                    "zipcode": user.zipcode,
                    "promo_code": user.promo_code,
                    "free_delivery": user.free_delivery,
                    "cart_id": user.cart_id,
                    "invited_by_id": user.invited_by_id
                }
                
                # Send to MongoDB
                try:
                    requests.post(f"{mongo_base}/admin/sync-user", json=user_data, timeout=10)
                except Exception as e:
                    print(f"Error syncing user {user.id}: {e}")
            
            # Migrate orders
            orders = session.query(Order).all()
            for order in orders:
                order_data = {
                    "id": order.id,
                    "user_id": order.user_id,
                    "restaurant_id": order.restaurant_id,
                    "cart_id": order.cart_id,
                    "supplier_id": order.supplier_id,
                    "order_date": order.order_date.isoformat() if order.order_date else None,
                    "delivery_fee": float(order.delivery_fee),
                    "subtotal": float(order.subtotal),
                    "total": float(order.total),
                    "was_prime_order": order.was_prime_order,
                    "status": order.status.value if order.status else "open",
                    "estimated_delivery": order.estimated_delivery.isoformat() if order.estimated_delivery else None,
                    "actual_delivery": order.actual_delivery.isoformat() if order.actual_delivery else None
                }
                
                # Send to MongoDB
                try:
                    requests.post(f"{mongo_base}/admin/sync-order", json=order_data, timeout=10)
                except Exception as e:
                    print(f"Error syncing order {order.id}: {e}")
            
            # Migrate payments
            payments = session.query(Payment).all()
            for payment in payments:
                payment_data = {
                    "id": payment.id,
                    "user_id": payment.user_id,
                    "order_id": payment.order_id,
                    "amount": float(payment.amount),
                    "payment_method": payment.payment_method.value if payment.payment_method else "credit_card",
                    "payment_status": payment.payment_status.value if payment.payment_status else "completed",
                    "payment_date": payment.payment_date.isoformat() if payment.payment_date else None,
                    "transaction_id": payment.transaction_id,
                    "payment_description": payment.payment_description
                }
                
                # Send to MongoDB
                try:
                    requests.post(f"{mongo_base}/admin/sync-payment", json=payment_data, timeout=10)
                except Exception as e:
                    print(f"Error syncing payment {payment.id}: {e}")
            
            # Migrate carts
            carts = session.query(Cart).all()
            for cart in carts:
                cart_data = {
                    "id": cart.id,
                    "restaurant_id": cart.restaurant_id,
                    "created_at": cart.created_at.isoformat() if cart.created_at else None,
                    "state": cart.state.value if cart.state else "open"
                }
                
                # Send to MongoDB
                try:
                    requests.post(f"{mongo_base}/admin/sync-cart", json=cart_data, timeout=10)
                except Exception as e:
                    print(f"Error syncing cart {cart.id}: {e}")
            
            print(f"Migration completed: {len(restaurants)} restaurants, {len(dishes)} dishes, {len(users)} users, {len(orders)} orders, {len(payments)} payments, {len(carts)} carts")
            return jsonify({"message": "Migration to MongoDB completed successfully"}), 200
            
        except Exception as e:
            return jsonify({"error": f"Migration error: {str(e)}"}), 500
        finally:
            session.close()
            
    except Exception as e:
        return jsonify({"error": f"Migration error: {str(e)}"}), 500

@app.route("/admin/migrate-from-mongo", methods=["POST"])
def migrate_from_mongo():
    """Migrate data from MongoDB to SQL"""
    try:
        # Import the migration functions
        import requests
        
        # Get data from MongoDB
        mongo_base = "http://mongo-backend:5001"
        
        session = SessionLocal()
        try:
            # Migrate users
            users_response = requests.get(f"{mongo_base}/users")
            if users_response.status_code == 200:
                mongo_users = users_response.json()
                for user_data in mongo_users:
                    existing_user = session.query(User).filter_by(id=user_data['id']).first()
                    if not existing_user:
                        user = User(
                            id=user_data['id'],
                            first_name=user_data['first_name'],
                            last_name=user_data['last_name'],
                            email=user_data['email'],
                            password_hash=user_data.get('password_hash', 'default'),
                            city=user_data.get('city'),
                            street=user_data.get('street'),
                            zipcode=user_data.get('zipcode'),
                            promo_code=user_data.get('promo_code'),
                            free_delivery=user_data.get('free_delivery', False)
                        )
                        session.add(user)
            
            # Migrate orders
            orders_response = requests.get(f"{mongo_base}/orders")
            if orders_response.status_code == 200:
                mongo_orders = orders_response.json()
                for order_data in mongo_orders:
                    existing_order = session.query(Order).filter_by(id=order_data['id']).first()
                    if not existing_order:
                        order = Order(
                            id=order_data['id'],
                            user_id=order_data['user_id'],
                            restaurant_id=order_data['restaurant_id'],
                            cart_id=order_data['cart_id'],
                            supplier_id=order_data.get('supplier_id'),
                            order_date=datetime.datetime.fromisoformat(order_data['order_date'].replace('Z', '+00:00')) if isinstance(order_data['order_date'], str) else order_data['order_date'],
                            delivery_fee=order_data.get('delivery_fee', 3.99),
                            subtotal=order_data.get('subtotal', 0),
                            total=order_data.get('total', 0),
                            was_prime_order=order_data.get('was_prime_order', False),
                            status=CartState(order_data.get('status', 'open')),
                            estimated_delivery=datetime.datetime.fromisoformat(order_data['estimated_delivery'].replace('Z', '+00:00')) if order_data.get('estimated_delivery') and isinstance(order_data['estimated_delivery'], str) else order_data.get('estimated_delivery'),
                            actual_delivery=datetime.datetime.fromisoformat(order_data['actual_delivery'].replace('Z', '+00:00')) if order_data.get('actual_delivery') and isinstance(order_data['actual_delivery'], str) else order_data.get('actual_delivery')
                        )
                        session.add(order)
            
            # Migrate payments
            payments_response = requests.get(f"{mongo_base}/payments")
            if payments_response.status_code == 200:
                mongo_payments = payments_response.json()
                for payment_data in mongo_payments:
                    existing_payment = session.query(Payment).filter_by(id=payment_data['id']).first()
                    if not existing_payment:
                        payment = Payment(
                            id=payment_data['id'],
                            user_id=payment_data['user_id'],
                            order_id=payment_data.get('order_id'),
                            amount=payment_data['amount'],
                            payment_method=PaymentMethod(payment_data['payment_method']),
                            payment_status=PaymentStatus(payment_data['payment_status']),
                            payment_date=datetime.datetime.fromisoformat(payment_data['payment_date'].replace('Z', '+00:00')) if isinstance(payment_data['payment_date'], str) else payment_data['payment_date'],
                            transaction_id=payment_data.get('transaction_id'),
                            payment_description=payment_data['payment_description']
                        )
                        session.add(payment)
            
            session.commit()
            return jsonify({"message": "Migration from MongoDB completed successfully"}), 200
            
        except Exception as e:
            session.rollback()
            return jsonify({"error": f"Migration error: {str(e)}"}), 500
        finally:
            session.close()
            
    except Exception as e:
        return jsonify({"error": f"Migration error: {str(e)}"}), 500

@app.route("/admin/sync-user", methods=["POST"])
def sync_user():
    """Sync user from MongoDB to SQL"""
    data = request.get_json()
    session = SessionLocal()
    try:
        # Check if user already exists
        existing_user = session.query(User).filter_by(id=data["id"]).first()
        
        if existing_user:
            # Update existing user
            for key, value in data.items():
                if hasattr(existing_user, key) and key != 'id':
                    setattr(existing_user, key, value)
        else:
            # Create new user
            user = User(
                id=data["id"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                email=data["email"],
                password_hash=data.get("password_hash", "default"),
                city=data.get("city"),
                street=data.get("street"),
                zipcode=data.get("zipcode"),
                promo_code=data.get("promo_code"),
                free_delivery=data.get("free_delivery", False),
                cart_id=data.get("cart_id"),
                invited_by_id=data.get("invited_by_id")
            )
            session.add(user)
        
        session.commit()
        return jsonify({"message": "User synced successfully"}), 200
        
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route("/admin/sync-order", methods=["POST"])
def sync_order():
    """Sync order from MongoDB to SQL"""
    data = request.get_json()
    session = SessionLocal()
    try:
        # Check if order already exists
        existing_order = session.query(Order).filter_by(id=data["id"]).first()
        
        # Parse datetime fields
        order_date = datetime.datetime.fromisoformat(data["order_date"].replace('Z', '+00:00')) if isinstance(data["order_date"], str) else data["order_date"]
        estimated_delivery = None
        actual_delivery = None
        
        if data.get("estimated_delivery"):
            estimated_delivery = datetime.datetime.fromisoformat(data["estimated_delivery"].replace('Z', '+00:00')) if isinstance(data["estimated_delivery"], str) else data["estimated_delivery"]
        
        if data.get("actual_delivery"):
            actual_delivery = datetime.datetime.fromisoformat(data["actual_delivery"].replace('Z', '+00:00')) if isinstance(data["actual_delivery"], str) else data["actual_delivery"]
        
        if existing_order:
            # Update existing order
            existing_order.user_id = data["user_id"]
            existing_order.restaurant_id = data["restaurant_id"]
            existing_order.cart_id = data["cart_id"]
            existing_order.supplier_id = data.get("supplier_id")
            existing_order.order_date = order_date
            existing_order.delivery_fee = float(data.get("delivery_fee", 3.99))
            existing_order.subtotal = float(data.get("subtotal", 0))
            existing_order.total = float(data.get("total", 0))
            existing_order.was_prime_order = bool(data.get("was_prime_order", False))
            existing_order.status = CartState(data.get("status", "open"))
            existing_order.estimated_delivery = estimated_delivery
            existing_order.actual_delivery = actual_delivery
        else:
            # Create new order
            order = Order(
                id=data["id"],
                user_id=data["user_id"],
                restaurant_id=data["restaurant_id"],
                cart_id=data["cart_id"],
                supplier_id=data.get("supplier_id"),
                order_date=order_date,
                delivery_fee=float(data.get("delivery_fee", 3.99)),
                subtotal=float(data.get("subtotal", 0)),
                total=float(data.get("total", 0)),
                was_prime_order=bool(data.get("was_prime_order", False)),
                status=CartState(data.get("status", "open")),
                estimated_delivery=estimated_delivery,
                actual_delivery=actual_delivery
            )
            session.add(order)
        
        session.commit()
        return jsonify({"message": "Order synced successfully"}), 200
        
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route("/admin/sync-cart", methods=["POST"])
def sync_cart():
    """Sync cart from MongoDB to SQL"""
    data = request.get_json()
    session = SessionLocal()
    try:
        # Check if cart already exists
        existing_cart = session.query(Cart).filter_by(id=data["id"]).first()
        
        # Parse datetime field
        created_at = datetime.datetime.fromisoformat(data["created_at"].replace('Z', '+00:00')) if isinstance(data["created_at"], str) else data["created_at"]
        
        if existing_cart:
            # Update existing cart
            existing_cart.created_at = created_at
            existing_cart.restaurant_id = data["restaurant_id"]
            existing_cart.state = CartState(data.get("state", "open"))
        else:
            # Create new cart
            cart = Cart(
                id=data["id"],
                created_at=created_at,
                restaurant_id=data["restaurant_id"],
                state=CartState(data.get("state", "open"))
            )
            session.add(cart)
        
        session.commit()
        return jsonify({"message": "Cart synced successfully"}), 200
        
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route("/users", methods=["GET"])
def get_all_users():
    """Get all users for migration purposes"""
    session = SessionLocal()
    try:
        users = session.query(User).all()
        result = []
        
        for user in users:
            result.append({
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "password_hash": user.password_hash,
                "city": user.city,
                "street": user.street,
                "zipcode": user.zipcode,
                "promo_code": user.promo_code,
                "free_delivery": user.free_delivery,
                "cart_id": user.cart_id,
                "invited_by_id": user.invited_by_id
            })
        
        return jsonify(result), 200
    finally:
        session.close()

@app.route("/carts", methods=["GET"])
def get_all_carts():
    """Get all carts for migration purposes"""
    session = SessionLocal()
    try:
        carts = session.query(Cart).all()
        result = []
        
        for cart in carts:
            result.append({
                "id": cart.id,
                "created_at": cart.created_at.isoformat(),
                "restaurant_id": cart.restaurant_id,
                "state": cart.state.value
            })
        
        return jsonify(result), 200
    finally:
        session.close()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")