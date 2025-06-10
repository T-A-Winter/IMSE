import datetime
from db import SessionLocal, engine, Base
from models import App, Restaurant, Dish, User, Address, VehicleType, Supplier, Cart, CartState, OrderItem
from sqlalchemy.exc import IntegrityError
import random

# Create all tables
Base.metadata.create_all(bind=engine)

def seed_db():
    session = SessionLocal()
    
    try:
        # Check if we already have data
        apps_count = session.query(App).count()
        if apps_count > 0:
            print("Database already seeded. Skipping...")
            return
            
        # Create App
        app = App(name="Food Delivery App", version=1)
        session.add(app)
        session.flush()  # Flush to get the ID
        
        # Create Suppliers
        suppliers = [
            Supplier(name="Speedy Delivery", vehicle_type=VehicleType.BIKE, app_id=app.id),
            Supplier(name="Quick Wheels", vehicle_type=VehicleType.CAR, app_id=app.id),
            Supplier(name="Urban Movers", vehicle_type=VehicleType.MOPED, app_id=app.id)
        ]
        session.add_all(suppliers)
        
        # Create Restaurants
        restaurants = [
            Restaurant(
                name="Pizza Palace",
                open_from=datetime.time(11, 0),
                open_till=datetime.time(22, 0),
                city="Vienna",
                street="Karlsplatz 13",
                zipcode=1040,
                app_id=app.id
            ),
            Restaurant(
                name="Burger Heaven",
                open_from=datetime.time(10, 0),
                open_till=datetime.time(23, 0),
                city="Vienna",
                street="Stephansplatz 1",
                zipcode=1010,
                app_id=app.id
            ),
            Restaurant(
                name="Sushi World",
                open_from=datetime.time(12, 0),
                open_till=datetime.time(22, 0),
                city="Vienna",
                street="Mariahilfer Straße 100",
                zipcode=1060,
                app_id=app.id
            ),
            Restaurant(
                name="Pasta Paradise",
                open_from=datetime.time(11, 30),
                open_till=datetime.time(21, 30),
                city="Vienna",
                street="Schönbrunner Schloßstraße 47",
                zipcode=1130,
                app_id=app.id
            ),
            Restaurant(
                name="Falafel Factory",
                open_from=datetime.time(10, 0),
                open_till=datetime.time(20, 0),
                city="Vienna",
                street="Naschmarkt 36",
                zipcode=1060,
                app_id=app.id
            )
        ]
        session.add_all(restaurants)
        session.flush()
        
        # Create Dishes for each restaurant
        dishes = []
        
        # Pizza Palace dishes
        dishes.extend([
            Dish(name="Margherita Pizza", price=10.99, restaurant_id=restaurants[0].id),
            Dish(name="Pepperoni Pizza", price=12.99, restaurant_id=restaurants[0].id),
            Dish(name="Vegetarian Pizza", price=11.99, restaurant_id=restaurants[0].id),
            Dish(name="Hawaiian Pizza", price=13.99, restaurant_id=restaurants[0].id),
            Dish(name="Garlic Bread", price=4.99, restaurant_id=restaurants[0].id),
            Dish(name="Caesar Salad", price=8.99, restaurant_id=restaurants[0].id)
        ])
        
        # Burger Heaven dishes
        dishes.extend([
            Dish(name="Classic Burger", price=9.99, restaurant_id=restaurants[1].id),
            Dish(name="Cheeseburger", price=10.99, restaurant_id=restaurants[1].id),
            Dish(name="Bacon Burger", price=12.99, restaurant_id=restaurants[1].id),
            Dish(name="Veggie Burger", price=11.99, restaurant_id=restaurants[1].id),
            Dish(name="French Fries", price=3.99, restaurant_id=restaurants[1].id),
            Dish(name="Onion Rings", price=4.99, restaurant_id=restaurants[1].id)
        ])
        
        # Sushi World dishes
        dishes.extend([
            Dish(name="California Roll", price=8.99, restaurant_id=restaurants[2].id),
            Dish(name="Salmon Nigiri", price=9.99, restaurant_id=restaurants[2].id),
            Dish(name="Tuna Maki", price=7.99, restaurant_id=restaurants[2].id),
            Dish(name="Vegetable Roll", price=6.99, restaurant_id=restaurants[2].id),
            Dish(name="Miso Soup", price=3.99, restaurant_id=restaurants[2].id),
            Dish(name="Edamame", price=4.99, restaurant_id=restaurants[2].id)
        ])
        
        # Pasta Paradise dishes
        dishes.extend([
            Dish(name="Spaghetti Bolognese", price=11.99, restaurant_id=restaurants[3].id),
            Dish(name="Fettuccine Alfredo", price=12.99, restaurant_id=restaurants[3].id),
            Dish(name="Lasagna", price=13.99, restaurant_id=restaurants[3].id),
            Dish(name="Ravioli", price=10.99, restaurant_id=restaurants[3].id),
            Dish(name="Garlic Bread", price=4.99, restaurant_id=restaurants[3].id),
            Dish(name="Tiramisu", price=6.99, restaurant_id=restaurants[3].id)
        ])
        
        # Falafel Factory dishes
        dishes.extend([
            Dish(name="Falafel Wrap", price=7.99, restaurant_id=restaurants[4].id),
            Dish(name="Hummus Plate", price=6.99, restaurant_id=restaurants[4].id),
            Dish(name="Shawarma", price=9.99, restaurant_id=restaurants[4].id),
            Dish(name="Tabouleh Salad", price=5.99, restaurant_id=restaurants[4].id),
            Dish(name="Baba Ghanoush", price=6.99, restaurant_id=restaurants[4].id),
            Dish(name="Baklava", price=3.99, restaurant_id=restaurants[4].id)
        ])
        
        session.add_all(dishes)
        
        # Create Users
        users = [
            User(
                first_name="John",
                last_name="Doe",
                email="john.doe@example.com",
                city="Vienna",
                street="Teststrasse 1",
                zipcode=1010,
                free_delivery=False
            ),
            User(
                first_name="Jane",
                last_name="Smith",
                email="jane.smith@example.com",
                city="Vienna",
                street="Testgasse 2",
                zipcode=1020,
                free_delivery=True
            ),
            User(
                first_name="Bob",
                last_name="Johnson",
                email="bob.johnson@example.com",
                city="Vienna",
                street="Testplatz 3",
                zipcode=1030,
                free_delivery=False
            )
        ]
        
        # Set passwords
        for user in users:
            user.set_password("password123")
            
        session.add_all(users)
        session.flush()
        
        # Create some carts and order items
        for i in range(3):
            user = users[i]
            restaurant = random.choice(restaurants)
            
            # Create cart
            cart = Cart(
                created_at=datetime.datetime.now(),
                restaurant_id=restaurant.id,
                state=CartState.DELIVERED if i < 2 else CartState.OPEN
            )
            session.add(cart)
            session.flush()
            
            # Add user's cart_id
            user.cart_id = cart.id
            
            # Get restaurant dishes
            restaurant_dishes = [d for d in dishes if d.restaurant_id == restaurant.id]
            
            # Add 2-4 random dishes to cart
            for _ in range(random.randint(2, 4)):
                dish = random.choice(restaurant_dishes)
                quantity = random.randint(1, 3)
                
                order_item = OrderItem(
                    warenkorb_id=cart.id,
                    gericht_id=dish.id,
                    quantity=quantity,
                    total_price=float(dish.price) * quantity,
                    restaurant_address=f"{restaurant.street}, {restaurant.city}, {restaurant.zipcode}"
                )
                session.add(order_item)
        
        session.commit()
        print("Database seeded successfully!")
        
    except IntegrityError as e:
        session.rollback()
        print(f"Seeding failed: {e}")
    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    seed_db() 