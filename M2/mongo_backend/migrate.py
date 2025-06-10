#!/usr/bin/env python3
import os
import datetime
from pymongo import MongoClient
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.automap import automap_base
import json
from enum import Enum

# MongoDB connection
mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
mongo_client = MongoClient(mongo_uri)
mongo_db = mongo_client.food_delivery

# SQL connection
sql_uri = os.environ.get("SQL_URI", "mysql+pymysql://root:example@mariadb:3306/fooddelivery")
sql_engine = sa.create_engine(sql_uri)
Session = sessionmaker(bind=sql_engine)
sql_session = Session()

# Use reflection to get the models
Base = automap_base()
Base.prepare(autoload_with=sql_engine)

# Get the model classes
User = Base.classes.user
Restaurant = Base.classes.restaurant
Dish = Base.classes.dish
Cart = Base.classes.cart
OrderItem = Base.classes.orderitem
App = Base.classes.app
Supplier = Base.classes.supplier

# Define enums similar to the ones in models.py
class CartState(Enum):
    OPEN = "open"
    IN_PREPARATION = "in preparation"
    IN_DELIVERY = "in delivery"
    DELIVERED = "delivered"

class VehicleType(Enum):
    BIKE = "bike"
    CAR = "car"
    MOPED = "moped"

def serialize_datetime(obj):
    if isinstance(obj, (datetime.datetime, datetime.time)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def migrate_restaurants():
    print("Migrating restaurants...")
    restaurants = sql_session.query(Restaurant).all()
    
    for restaurant in restaurants:
        restaurant_dict = {
            "id": restaurant.id,
            "name": restaurant.name,
            "open_from": restaurant.open_from.strftime("%H:%M"),
            "open_till": restaurant.open_till.strftime("%H:%M"),
            "city": restaurant.city,
            "street": restaurant.street,
            "zipcode": restaurant.zipcode,
            "app_id": restaurant.app_id
        }
        
        # Insert or update in MongoDB
        mongo_db.restaurants.update_one(
            {"id": restaurant.id}, 
            {"$set": restaurant_dict}, 
            upsert=True
        )
    
    print(f"Migrated {len(restaurants)} restaurants")

def migrate_dishes():
    print("Migrating dishes...")
    dishes = sql_session.query(Dish).all()
    
    for dish in dishes:
        dish_dict = {
            "id": dish.id,
            "name": dish.name,
            "price": float(dish.price),
            "restaurant_id": dish.restaurant_id
        }
        
        # Insert or update in MongoDB
        mongo_db.dishes.update_one(
            {"id": dish.id}, 
            {"$set": dish_dict}, 
            upsert=True
        )
    
    print(f"Migrated {len(dishes)} dishes")

def migrate_users():
    print("Migrating users...")
    users = sql_session.query(User).all()
    
    for user in users:
        user_dict = {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "password_hash": user.password_hash,
            "city": user.city,
            "street": user.street,
            "zipcode": user.zipcode,
            "promo_code": getattr(user, "promo_code", None),
            "free_delivery": getattr(user, "free_delivery", False),
            "cart_id": getattr(user, "cart_id", None),
            "invited_by_id": getattr(user, "invited_by_id", None)
        }
        
        # Insert or update in MongoDB
        mongo_db.users.update_one(
            {"id": user.id}, 
            {"$set": user_dict}, 
            upsert=True
        )
    
    print(f"Migrated {len(users)} users")

def migrate_carts():
    print("Migrating carts...")
    carts = sql_session.query(Cart).all()
    
    for cart in carts:
        cart_dict = {
            "id": cart.id,
            "created_at": cart.created_at.isoformat(),
            "restaurant_id": cart.restaurant_id,
            "state": cart.state
        }
        
        # Insert or update in MongoDB
        mongo_db.carts.update_one(
            {"id": cart.id}, 
            {"$set": cart_dict}, 
            upsert=True
        )
    
    print(f"Migrated {len(carts)} carts")

def migrate_order_items():
    print("Migrating order items...")
    order_items = sql_session.query(OrderItem).all()
    
    for item in order_items:
        item_dict = {
            "id": item.id,
            "cart_id": item.warenkorb_id,
            "restaurant_address": getattr(item, "restaurant_address", None),
            "total_price": float(item.total_price) if hasattr(item, "total_price") and item.total_price else None,
            "quantity": item.quantity,
            "dish_id": getattr(item, "gericht_id", None)
        }
        
        # Insert or update in MongoDB
        mongo_db.order_items.update_one(
            {"id": item.id, "cart_id": item.warenkorb_id}, 
            {"$set": item_dict}, 
            upsert=True
        )
    
    print(f"Migrated {len(order_items)} order items")

def migrate_suppliers():
    print("Migrating suppliers...")
    suppliers = sql_session.query(Supplier).all()
    
    for supplier in suppliers:
        supplier_dict = {
            "id": supplier.id,
            "name": supplier.name,
            "vehicle_type": supplier.vehicle_type,
            "app_id": getattr(supplier, "app_id", None)
        }
        
        # Insert or update in MongoDB
        mongo_db.suppliers.update_one(
            {"id": supplier.id}, 
            {"$set": supplier_dict}, 
            upsert=True
        )
    
    print(f"Migrated {len(suppliers)} suppliers")

def migrate_apps():
    print("Migrating apps...")
    apps = sql_session.query(App).all()
    
    for app in apps:
        app_dict = {
            "id": app.id,
            "name": app.name,
            "version": app.version
        }
        
        # Insert or update in MongoDB
        mongo_db.apps.update_one(
            {"id": app.id}, 
            {"$set": app_dict}, 
            upsert=True
        )
    
    print(f"Migrated {len(apps)} apps")

def run_migration():
    print("Starting migration from SQL to MongoDB...")
    
    # Create collections if they don't exist
    collections = ["restaurants", "dishes", "users", "carts", "order_items", "suppliers", "apps"]
    existing_collections = mongo_db.list_collection_names()
    
    for collection in collections:
        if collection not in existing_collections:
            mongo_db.create_collection(collection)
    
    # Run migration functions
    try:
        migrate_apps()
    except Exception as e:
        print(f"Error migrating apps: {e}")
    
    try:
        migrate_suppliers()
    except Exception as e:
        print(f"Error migrating suppliers: {e}")
    
    try:
        migrate_restaurants()
    except Exception as e:
        print(f"Error migrating restaurants: {e}")
    
    try:
        migrate_dishes()
    except Exception as e:
        print(f"Error migrating dishes: {e}")
    
    try:
        migrate_users()
    except Exception as e:
        print(f"Error migrating users: {e}")
    
    try:
        migrate_carts()
    except Exception as e:
        print(f"Error migrating carts: {e}")
    
    try:
        migrate_order_items()
    except Exception as e:
        print(f"Error migrating order items: {e}")
    
    print("Migration completed successfully!")

if __name__ == "__main__":
    run_migration() 