from flask import Flask, request, jsonify
from db import SessionLocal, engine
from models import User, Restaurant, Dish, Cart, OrderItem, CartState
from sqlalchemy.exc import IntegrityError
from db import Base
import datetime

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
                "address": f"{restaurant.street}, {restaurant.city}, {restaurant.zipcode}"
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
        
        # Update cart state
        cart.state = CartState.IN_PREPARATION
        
        # TODO: Create Order entity

        session.commit()
        
        return jsonify({
            "message": "Order placed successfully",
            "cart_id": cart.id,
            "state": cart.state.value
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
            "order_items": session.query(OrderItem).count()
        }
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")