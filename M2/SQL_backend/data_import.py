#!/usr/bin/env python3
"""
Data Import Script for Food Delivery Application
Generates randomized data for use cases and reports as required by M2 guidelines (2.2.1)
"""

import random
import datetime
from faker import Faker
from db import SessionLocal, engine
from models import (
    User, Restaurant, Dish, Cart, OrderItem, CartState, PrimeUser, Member, 
    Order, Supplier, App, Payment, PaymentMethod, PaymentStatus, 
    PrimeSubscription, PrimePayment, VehicleType
)
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

fake = Faker()

def clear_all_data(session):
    """Clear existing test data from the database but preserve manually created users"""
    print("Clearing existing test data...")
    
    # Get manually created users (those not from test data)
    # We'll preserve users that don't have fake emails or specific test patterns
    manual_users = session.query(User).filter(
        ~User.email.like('%@example.com'),
        ~User.email.like('%fake%'),
        ~User.email.like('%test%')
    ).all()
    
    manual_user_ids = [user.id for user in manual_users]
    print(f"Preserving {len(manual_users)} manually created users")
    
    # Delete in reverse order of dependencies, but preserve manual users
    session.query(PrimePayment).delete()
    session.query(Payment).delete()
    session.query(PrimeSubscription).delete()
    session.query(OrderItem).delete()
    session.query(Order).delete()
    session.query(Cart).delete()
    session.query(Dish).delete()
    session.query(Member).filter(~Member.user_id.in_(manual_user_ids)).delete(synchronize_session=False)
    session.query(PrimeUser).filter(~PrimeUser.user_id.in_(manual_user_ids)).delete(synchronize_session=False)
    
    # Delete test users (but preserve manual ones)
    session.query(User).filter(~User.id.in_(manual_user_ids)).delete(synchronize_session=False)
    
    session.query(Restaurant).delete()
    session.query(Supplier).delete()
    session.query(App).delete()
    
    session.commit()
    print("✅ Test data cleared, manual users preserved")

def create_apps(session, count=3):
    """Create app records"""
    print(f"Creating {count} apps...")
    
    apps = []
    app_names = ["FoodDelivery Pro", "QuickEats", "DeliveryMaster"]
    
    for i in range(count):
        app = App(
            name=app_names[i] if i < len(app_names) else f"App {i+1}",
            version=random.randint(1, 5)
        )
        apps.append(app)
        session.add(app)
    
    session.commit()
    print(f"✅ Created {len(apps)} apps")
    return apps

def create_suppliers(session, apps, count=10):
    """Create supplier records"""
    print(f"Creating {count} suppliers...")
    
    suppliers = []
    vehicle_types = list(VehicleType)
    
    for i in range(count):
        supplier = Supplier(
            name=fake.name(),
            vehicle_type=random.choice(vehicle_types),
            app_id=random.choice(apps).id
        )
        suppliers.append(supplier)
        session.add(supplier)
    
    session.commit()
    print(f"✅ Created {len(suppliers)} suppliers")
    return suppliers

def create_restaurants(session, apps, count=15):
    """Create restaurant records"""
    print(f"Creating {count} restaurants...")
    
    restaurants = []
    restaurant_names = [
        "Pizza Palace", "Burger Heaven", "Sushi World", "Pasta Paradise", "Taco Fiesta",
        "Indian Spice", "Thai Garden", "Greek Corner", "French Bistro", "Chinese Dragon",
        "Mexican Cantina", "Italian Villa", "American Diner", "Korean BBQ", "Vietnamese Pho"
    ]
    
    for i in range(count):
        # Generate random opening hours
        open_hour = random.randint(8, 12)
        close_hour = random.randint(20, 23)
        
        restaurant = Restaurant(
            name=restaurant_names[i] if i < len(restaurant_names) else f"Restaurant {i+1}",
            open_from=datetime.time(open_hour, 0),
            open_till=datetime.time(close_hour, 0),
            city=fake.city(),
            street=fake.street_address(),
            zipcode=random.randint(1000, 9999),
            app_id=random.choice(apps).id
        )
        restaurants.append(restaurant)
        session.add(restaurant)
    
    session.commit()
    print(f"✅ Created {len(restaurants)} restaurants")
    return restaurants

def create_dishes(session, restaurants, count_per_restaurant=8):
    """Create dish records for each restaurant"""
    print(f"Creating ~{count_per_restaurant} dishes per restaurant...")
    
    dishes = []
    dish_categories = {
        "Pizza": ["Margherita", "Pepperoni", "Hawaiian", "Quattro Stagioni", "Diavola"],
        "Burger": ["Classic Burger", "Cheeseburger", "Bacon Burger", "Veggie Burger", "Double Burger"],
        "Sushi": ["California Roll", "Salmon Nigiri", "Tuna Sashimi", "Dragon Roll", "Philadelphia Roll"],
        "Pasta": ["Spaghetti Carbonara", "Penne Arrabbiata", "Lasagna", "Fettuccine Alfredo", "Ravioli"],
        "Asian": ["Pad Thai", "Fried Rice", "Spring Rolls", "Dumplings", "Ramen"],
        "Mexican": ["Tacos", "Burritos", "Quesadillas", "Nachos", "Enchiladas"],
        "Indian": ["Chicken Curry", "Biryani", "Naan Bread", "Samosas", "Tandoori Chicken"]
    }
    
    for restaurant in restaurants:
        # Choose a category based on restaurant name
        category = "Asian"  # Default
        for cat in dish_categories:
            if cat.lower() in restaurant.name.lower():
                category = cat
                break
        
        dish_names = dish_categories.get(category, dish_categories["Asian"])
        
        for i in range(count_per_restaurant):
            dish_name = dish_names[i % len(dish_names)]
            if i >= len(dish_names):
                dish_name += f" Special {i - len(dish_names) + 1}"
            
            dish = Dish(
                name=dish_name,
                price=round(random.uniform(8.99, 24.99), 2),
                restaurant_id=restaurant.id
            )
            dishes.append(dish)
            session.add(dish)
    
    session.commit()
    print(f"✅ Created {len(dishes)} dishes")
    return dishes

def create_users(session, count=50):
    """Create user records"""
    print(f"Creating {count} users...")
    
    users = []
    
    for i in range(count):
        user = User(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.unique.email(),
            password_hash=generate_password_hash("password123"),
            city=fake.city(),
            street=fake.street_address(),
            zipcode=random.randint(1000, 9999),
            promo_code=fake.lexify(text="PROMO????") if random.random() < 0.3 else None,
            free_delivery=False
        )
        users.append(user)
        session.add(user)
    
    session.commit()
    print(f"✅ Created {len(users)} users")
    return users

def create_prime_users(session, users, percentage=0.3):
    """Create Prime users (30% of users)"""
    prime_count = int(len(users) * percentage)
    print(f"Creating {prime_count} Prime users...")
    
    prime_users = []
    selected_users = random.sample(users, prime_count)
    
    for user in selected_users:
        # Create PrimeUser
        prime_user = PrimeUser(
            user_id=user.id,
            fee=9.99,
            free_delivery=True
        )
        session.add(prime_user)
        prime_users.append(prime_user)
        
        # Create Member
        member = Member(user_id=user.id)
        session.add(member)
        
        # Update user's free_delivery flag
        user.free_delivery = True
        
        # Create Prime subscription
        start_date = fake.date_between(start_date='-1y', end_date='today')
        subscription = PrimeSubscription(
            user_id=user.id,
            start_date=start_date,
            monthly_fee=9.99,
            is_active=random.choice([True, True, True, False]),  # 75% active
            auto_renew=True,
            cancelled_date=None
        )
        session.add(subscription)
        session.flush()  # Get subscription ID
        
        # Create Prime payments (monthly payments)
        current_date = start_date
        while current_date <= datetime.date.today():
            payment = Payment(
                user_id=user.id,
                amount=9.99,
                payment_method=random.choice(list(PaymentMethod)),
                payment_status=PaymentStatus.COMPLETED,
                payment_date=current_date,
                transaction_id=f"PRIME_{user.id}_{current_date.strftime('%Y%m%d')}",
                payment_description="Prime Monthly Subscription"
            )
            session.add(payment)
            session.flush()  # Get payment ID
            
            # Create Prime payment record
            prime_payment = PrimePayment(
                subscription_id=subscription.id,
                payment_id=payment.id,
                billing_period_start=current_date,
                billing_period_end=current_date + datetime.timedelta(days=30),
                due_date=current_date,
                paid_date=current_date
            )
            session.add(prime_payment)
            
            # Move to next month
            current_date = current_date + datetime.timedelta(days=30)
    
    session.commit()
    print(f"✅ Created {len(prime_users)} Prime users with subscriptions and payments")
    return prime_users

def create_orders_and_carts(session, users, restaurants, dishes, suppliers, count=200):
    """Create orders, carts, and order items"""
    print(f"Creating {count} orders with carts and items...")
    
    orders = []
    carts = []
    order_items = []
    
    for i in range(count):
        user = random.choice(users)
        restaurant = random.choice(restaurants)
        supplier = random.choice(suppliers)
        
        # Create cart
        cart_date = fake.date_time_between(start_date='-3m', end_date='now')
        cart = Cart(
            created_at=cart_date,
            restaurant_id=restaurant.id,
            state=random.choice(list(CartState))
        )
        session.add(cart)
        session.flush()  # Get cart ID
        carts.append(cart)
        
        # Create order items for this cart
        restaurant_dishes = [d for d in dishes if d.restaurant_id == restaurant.id]
        num_items = random.randint(1, 5)
        selected_dishes = random.sample(restaurant_dishes, min(num_items, len(restaurant_dishes)))
        
        subtotal = 0
        for dish in selected_dishes:
            quantity = random.randint(1, 3)
            total_price = dish.price * quantity
            subtotal += total_price
            
            order_item = OrderItem(
                warenkorb_id=cart.id,
                gericht_id=dish.id,
                quantity=quantity,
                total_price=total_price,
                restaurant_address=f"{restaurant.street}, {restaurant.city}, {restaurant.zipcode}"
            )
            session.add(order_item)
            order_items.append(order_item)
        
        # Check if user is Prime
        is_prime = session.query(PrimeUser).filter_by(user_id=user.id).first() is not None
        delivery_fee = 0.0 if is_prime else 3.99
        total = subtotal + delivery_fee
        
        # Create order
        order = Order(
            user_id=user.id,
            restaurant_id=restaurant.id,
            cart_id=cart.id,
            supplier_id=supplier.id,
            order_date=cart_date,
            delivery_fee=delivery_fee,
            subtotal=subtotal,
            total=total,
            was_prime_order=is_prime,
            status=cart.state,
            estimated_delivery=cart_date + datetime.timedelta(minutes=random.randint(20, 60)),
            actual_delivery=cart_date + datetime.timedelta(minutes=random.randint(25, 90)) if cart.state == CartState.DELIVERED else None
        )
        session.add(order)
        session.flush()  # Get order ID
        orders.append(order)
        
        # Create payment for order
        payment = Payment(
            user_id=user.id,
            order_id=order.id,
            amount=total,
            payment_method=random.choice(list(PaymentMethod)),
            payment_status=PaymentStatus.COMPLETED,
            payment_date=cart_date,
            transaction_id=f"ORDER_{order.id}_{cart_date.strftime('%Y%m%d%H%M%S')}",
            payment_description=f"Order #{order.id} - {restaurant.name}"
        )
        session.add(payment)
    
    session.commit()
    print(f"✅ Created {len(orders)} orders, {len(carts)} carts, {len(order_items)} order items, and payments")
    return orders, carts, order_items

def generate_sample_data():
    """Generate complete sample data for the application"""
    print("🚀 Starting data import process...")
    
    session = SessionLocal()
    try:
        # Clear existing data
        clear_all_data(session)
        
        # Create base data
        apps = create_apps(session, 3)
        suppliers = create_suppliers(session, apps, 10)
        restaurants = create_restaurants(session, apps, 15)
        dishes = create_dishes(session, restaurants, 8)
        users = create_users(session, 50)
        
        # Create Prime users and subscriptions
        prime_users = create_prime_users(session, users, 0.3)
        
        # Create orders and related data
        orders, carts, order_items = create_orders_and_carts(session, users, restaurants, dishes, suppliers, 200)
        
        print("\n📊 Data Import Summary:")
        print(f"✅ Apps: {len(apps)}")
        print(f"✅ Suppliers: {len(suppliers)}")
        print(f"✅ Restaurants: {len(restaurants)}")
        print(f"✅ Dishes: {len(dishes)}")
        print(f"✅ Users: {len(users)}")
        print(f"✅ Prime Users: {len(prime_users)}")
        print(f"✅ Orders: {len(orders)}")
        print(f"✅ Carts: {len(carts)}")
        print(f"✅ Order Items: {len(order_items)}")
        
        # Calculate some statistics
        total_payments = session.query(Payment).count()
        total_revenue = session.query(Payment).filter_by(payment_status=PaymentStatus.COMPLETED).with_entities(Payment.amount).all()
        total_revenue_amount = sum([p[0] for p in total_revenue])
        
        print(f"✅ Total Payments: {total_payments}")
        print(f"✅ Total Revenue: €{total_revenue_amount:.2f}")
        
        print("\n🎉 Data import completed successfully!")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error during data import: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    generate_sample_data() 