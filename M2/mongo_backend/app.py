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
    return jsonify({"status": "healthy", "timestamp": datetime.datetime.now().isoformat()})

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
    
    # Get the next available ID
    max_id = 1
    existing_carts = list(db.carts.find({}, {"id": 1, "_id": 0}))
    if existing_carts:
        max_id = max([cart.get("id", 0) for cart in existing_carts]) + 1
    
    # Create a new cart
    new_cart = {
        "id": max_id,
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
    
    # Get the next available ID
    max_id = 1
    existing_items = list(db.order_items.find({}, {"id": 1, "_id": 0}))
    if existing_items:
        max_id = max([item.get("id", 0) for item in existing_items]) + 1
    
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
        # Create new item
        new_item = {
            "id": max_id,
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
    
    # Update cart state
    db.carts.update_one(
        {"id": int(cart_id)},
        {"$set": {"state": "in preparation"}}
    )
    
    return jsonify({
        "message": "Order placed successfully",
        "cart_id": int(cart_id),
        "state": "in preparation"
    }), 200

@app.route("/migrate", methods=["POST"])
def migrate_data():
    try:
        # Run migration script in a separate thread to avoid blocking
        def run_migration():
            from migrate import run_migration
            run_migration()
        
        thread = threading.Thread(target=run_migration)
        thread.start()
        
        return jsonify({"status": "Migration started successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/stats", methods=["GET"])
def get_stats():
    try:
        stats = {
            "users": db.users.count_documents({}),
            "restaurants": db.restaurants.count_documents({}),
            "dishes": db.dishes.count_documents({}),
            "carts": db.carts.count_documents({}),
            "order_items": db.order_items.count_documents({})
        }
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001) 