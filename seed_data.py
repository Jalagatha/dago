"""
Seed data script for Dago Food & Parcel Delivery App

This script populates the database with sample data for testing:
- 1 Admin user
- 3 Driver users (with profiles)
- 5 Customer users (with profiles)
- 5 Restaurants with menu categories and items
- Sample food orders
- Sample parcel deliveries
- Sample reviews

Run with: python seed_data.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models.user import User, UserProfile, DriverProfile, UserRole
from app.models.restaurant import Restaurant, MenuCategory, MenuItem
from app.models.food_order import FoodOrder, OrderItem, OrderStatus
from app.models.parcel import ParcelDelivery, ParcelSize, ParcelStatus
from app.models.review import Review, TargetType
from decimal import Decimal
from datetime import datetime, timedelta
import random


def clear_data(db):
    """Clear existing data"""
    print("Clearing existing data...")
    db.query(Review).delete()
    db.query(OrderItem).delete()
    db.query(FoodOrder).delete()
    db.query(ParcelDelivery).delete()
    db.query(MenuItem).delete()
    db.query(MenuCategory).delete()
    db.query(Restaurant).delete()
    db.query(DriverProfile).delete()
    db.query(UserProfile).delete()
    db.query(User).delete()
    db.commit()
    print("Data cleared successfully!")


def create_users(db):
    """Create admin, driver, and customer users"""
    print("Creating users...")
    users = {}

    # Admin user
    admin = User(
        email="admin@dago.com",
        password_hash=get_password_hash("admin123"),
        phone_number="+1234567890",
        role=UserRole.ADMIN,
        is_verified=True,
    )
    db.add(admin)
    db.flush()

    admin_profile = UserProfile(
        user_id=admin.id,
        full_name="Admin User",
        city="New York",
        state="NY",
    )
    db.add(admin_profile)
    users['admin'] = admin
    print(f"  Created admin: admin@dago.com / admin123")

    # Driver users
    driver_data = [
        {"email": "john.driver@dago.com", "name": "John Smith", "vehicle": "Motorcycle", "license": "DRV001"},
        {"email": "jane.driver@dago.com", "name": "Jane Doe", "vehicle": "Car", "license": "DRV002"},
        {"email": "mike.driver@dago.com", "name": "Mike Johnson", "vehicle": "Bicycle", "license": "DRV003"},
    ]

    users['drivers'] = []
    for d in driver_data:
        driver = User(
            email=d["email"],
            password_hash=get_password_hash("driver123"),
            phone_number=f"+1555{random.randint(1000000, 9999999)}",
            role=UserRole.DRIVER,
            is_verified=True,
        )
        db.add(driver)
        db.flush()

        driver_profile_data = UserProfile(
            user_id=driver.id,
            full_name=d["name"],
            city="New York",
            state="NY",
        )
        db.add(driver_profile_data)

        driver_profile = DriverProfile(
            user_id=driver.id,
            vehicle_type=d["vehicle"],
            license_number=d["license"],
            is_available=random.choice([True, False]),
            rating_average=round(random.uniform(4.0, 5.0), 1),
            total_deliveries=random.randint(10, 100),
        )
        db.add(driver_profile)
        users['drivers'].append(driver)
        print(f"  Created driver: {d['email']} / driver123")

    # Customer users
    customer_data = [
        {"email": "alice@example.com", "name": "Alice Williams", "address": "123 Main St"},
        {"email": "bob@example.com", "name": "Bob Brown", "address": "456 Oak Ave"},
        {"email": "charlie@example.com", "name": "Charlie Davis", "address": "789 Pine Rd"},
        {"email": "diana@example.com", "name": "Diana Miller", "address": "321 Elm St"},
        {"email": "evan@example.com", "name": "Evan Wilson", "address": "654 Maple Dr"},
    ]

    users['customers'] = []
    for c in customer_data:
        customer = User(
            email=c["email"],
            password_hash=get_password_hash("customer123"),
            phone_number=f"+1555{random.randint(1000000, 9999999)}",
            role=UserRole.CUSTOMER,
            is_verified=True,
        )
        db.add(customer)
        db.flush()

        customer_profile = UserProfile(
            user_id=customer.id,
            full_name=c["name"],
            address_line1=c["address"],
            city="New York",
            state="NY",
            postal_code="10001",
            latitude=40.7128 + random.uniform(-0.05, 0.05),
            longitude=-74.0060 + random.uniform(-0.05, 0.05),
        )
        db.add(customer_profile)
        users['customers'].append(customer)
        print(f"  Created customer: {c['email']} / customer123")

    db.commit()
    return users


def create_restaurants(db):
    """Create restaurants with menu categories and items"""
    print("Creating restaurants...")
    restaurants = []

    restaurant_data = [
        {
            "name": "Bella Italia",
            "description": "Authentic Italian cuisine with homemade pasta and wood-fired pizzas",
            "cuisine_type": "Italian",
            "address": "100 Little Italy Way",
            "delivery_fee": 3.99,
            "categories": [
                {
                    "name": "Appetizers",
                    "items": [
                        {"name": "Bruschetta", "description": "Toasted bread with tomatoes and basil", "price": 8.99},
                        {"name": "Calamari Fritti", "description": "Crispy fried squid with marinara", "price": 12.99},
                        {"name": "Caprese Salad", "description": "Fresh mozzarella with tomatoes and basil", "price": 10.99},
                    ]
                },
                {
                    "name": "Pasta",
                    "items": [
                        {"name": "Spaghetti Carbonara", "description": "Creamy pasta with bacon and egg", "price": 16.99},
                        {"name": "Fettuccine Alfredo", "description": "Fettuccine in creamy parmesan sauce", "price": 15.99},
                        {"name": "Lasagna Bolognese", "description": "Layered pasta with meat sauce", "price": 18.99},
                    ]
                },
                {
                    "name": "Pizza",
                    "items": [
                        {"name": "Margherita", "description": "Classic tomato, mozzarella, and basil", "price": 14.99},
                        {"name": "Pepperoni", "description": "Loaded with pepperoni and cheese", "price": 16.99},
                        {"name": "Quattro Formaggi", "description": "Four cheese pizza", "price": 17.99},
                    ]
                },
            ]
        },
        {
            "name": "Sakura Sushi",
            "description": "Premium Japanese sushi and sashimi prepared by master chefs",
            "cuisine_type": "Japanese",
            "address": "200 Japan Town Plaza",
            "delivery_fee": 4.99,
            "categories": [
                {
                    "name": "Sushi Rolls",
                    "items": [
                        {"name": "California Roll", "description": "Crab, avocado, cucumber", "price": 8.99},
                        {"name": "Spicy Tuna Roll", "description": "Fresh tuna with spicy mayo", "price": 10.99},
                        {"name": "Dragon Roll", "description": "Eel, avocado, cucumber with eel sauce", "price": 14.99},
                    ]
                },
                {
                    "name": "Sashimi",
                    "items": [
                        {"name": "Salmon Sashimi", "description": "5 pieces of fresh salmon", "price": 12.99},
                        {"name": "Tuna Sashimi", "description": "5 pieces of bluefin tuna", "price": 15.99},
                        {"name": "Mixed Sashimi", "description": "Chef's selection of 12 pieces", "price": 24.99},
                    ]
                },
                {
                    "name": "Entrees",
                    "items": [
                        {"name": "Teriyaki Chicken", "description": "Grilled chicken with teriyaki glaze", "price": 16.99},
                        {"name": "Beef Udon", "description": "Thick noodles with sliced beef", "price": 14.99},
                        {"name": "Tempura Combo", "description": "Shrimp and vegetable tempura", "price": 18.99},
                    ]
                },
            ]
        },
        {
            "name": "Taco Fiesta",
            "description": "Vibrant Mexican flavors with fresh ingredients",
            "cuisine_type": "Mexican",
            "address": "300 Cinco de Mayo St",
            "delivery_fee": 2.99,
            "categories": [
                {
                    "name": "Tacos",
                    "items": [
                        {"name": "Carnitas Tacos", "description": "Slow-cooked pork with cilantro", "price": 10.99},
                        {"name": "Carne Asada Tacos", "description": "Grilled steak with onions", "price": 12.99},
                        {"name": "Fish Tacos", "description": "Beer-battered fish with slaw", "price": 11.99},
                    ]
                },
                {
                    "name": "Burritos",
                    "items": [
                        {"name": "Chicken Burrito", "description": "Grilled chicken with rice and beans", "price": 11.99},
                        {"name": "Veggie Burrito", "description": "Grilled veggies with guacamole", "price": 10.99},
                        {"name": "Burrito Bowl", "description": "All the burrito toppings in a bowl", "price": 12.99},
                    ]
                },
                {
                    "name": "Sides",
                    "items": [
                        {"name": "Chips & Guacamole", "description": "Fresh-made guacamole with crispy chips", "price": 6.99},
                        {"name": "Mexican Rice", "description": "Seasoned rice with tomatoes", "price": 3.99},
                        {"name": "Refried Beans", "description": "Creamy pinto beans", "price": 3.99},
                    ]
                },
            ]
        },
        {
            "name": "Golden Dragon",
            "description": "Traditional Chinese cuisine with authentic recipes",
            "cuisine_type": "Chinese",
            "address": "400 Chinatown Square",
            "delivery_fee": 3.49,
            "categories": [
                {
                    "name": "Appetizers",
                    "items": [
                        {"name": "Spring Rolls", "description": "Crispy rolls with vegetables", "price": 6.99},
                        {"name": "Dumplings", "description": "Steamed pork dumplings (8 pcs)", "price": 8.99},
                        {"name": "Wonton Soup", "description": "Pork wontons in clear broth", "price": 7.99},
                    ]
                },
                {
                    "name": "Main Dishes",
                    "items": [
                        {"name": "Kung Pao Chicken", "description": "Spicy chicken with peanuts", "price": 14.99},
                        {"name": "Sweet & Sour Pork", "description": "Crispy pork in tangy sauce", "price": 15.99},
                        {"name": "Beef with Broccoli", "description": "Tender beef with fresh broccoli", "price": 16.99},
                        {"name": "General Tso's Chicken", "description": "Crispy chicken in spicy sauce", "price": 14.99},
                    ]
                },
                {
                    "name": "Noodles & Rice",
                    "items": [
                        {"name": "Fried Rice", "description": "Wok-fried rice with egg and vegetables", "price": 10.99},
                        {"name": "Lo Mein", "description": "Stir-fried noodles with vegetables", "price": 11.99},
                        {"name": "Chow Fun", "description": "Wide rice noodles with beef", "price": 13.99},
                    ]
                },
            ]
        },
        {
            "name": "Burger Barn",
            "description": "Gourmet burgers made with premium beef and fresh ingredients",
            "cuisine_type": "American",
            "address": "500 Main Street USA",
            "delivery_fee": 2.49,
            "categories": [
                {
                    "name": "Burgers",
                    "items": [
                        {"name": "Classic Burger", "description": "Beef patty with lettuce, tomato, onion", "price": 10.99},
                        {"name": "Bacon Cheeseburger", "description": "Beef, bacon, cheddar cheese", "price": 13.99},
                        {"name": "Mushroom Swiss", "description": "Sautéed mushrooms with swiss cheese", "price": 12.99},
                        {"name": "BBQ Burger", "description": "BBQ sauce, onion rings, bacon", "price": 14.99},
                    ]
                },
                {
                    "name": "Sides",
                    "items": [
                        {"name": "French Fries", "description": "Crispy golden fries", "price": 4.99},
                        {"name": "Onion Rings", "description": "Beer-battered onion rings", "price": 5.99},
                        {"name": "Coleslaw", "description": "Creamy homemade coleslaw", "price": 3.99},
                    ]
                },
                {
                    "name": "Drinks",
                    "items": [
                        {"name": "Milkshake", "description": "Chocolate, vanilla, or strawberry", "price": 5.99},
                        {"name": "Soft Drink", "description": "Coke, Sprite, or Fanta", "price": 2.99},
                        {"name": "Iced Tea", "description": "Fresh-brewed sweet tea", "price": 2.99},
                    ]
                },
            ]
        },
    ]

    for r_data in restaurant_data:
        restaurant = Restaurant(
            name=r_data["name"],
            description=r_data["description"],
            cuisine_type=r_data["cuisine_type"],
            address=r_data["address"],
            city="New York",
            state="NY",
            postal_code="10001",
            latitude=40.7128 + random.uniform(-0.05, 0.05),
            longitude=-74.0060 + random.uniform(-0.05, 0.05),
            phone_number=f"+1555{random.randint(1000000, 9999999)}",
            is_active=True,
            rating_average=round(random.uniform(3.5, 5.0), 1),
            delivery_fee=Decimal(str(r_data["delivery_fee"])),
            estimated_delivery_time=random.randint(20, 45),
        )
        db.add(restaurant)
        db.flush()

        for idx, cat_data in enumerate(r_data["categories"]):
            category = MenuCategory(
                restaurant_id=restaurant.id,
                name=cat_data["name"],
                display_order=idx,
            )
            db.add(category)
            db.flush()

            for item_data in cat_data["items"]:
                menu_item = MenuItem(
                    restaurant_id=restaurant.id,
                    category_id=category.id,
                    name=item_data["name"],
                    description=item_data["description"],
                    price=Decimal(str(item_data["price"])),
                    is_available=True,
                    preparation_time=random.randint(10, 25),
                )
                db.add(menu_item)

        restaurants.append(restaurant)
        print(f"  Created restaurant: {r_data['name']} with {len(r_data['categories'])} categories")

    db.commit()
    return restaurants


def create_orders(db, users, restaurants):
    """Create sample food orders"""
    print("Creating food orders...")

    orders = []
    statuses = list(OrderStatus)

    for i in range(10):
        customer = random.choice(users['customers'])
        restaurant = random.choice(restaurants)
        driver = random.choice(users['drivers']) if random.random() > 0.3 else None
        status = random.choice(statuses)

        # Get some menu items from the restaurant
        menu_items = db.query(MenuItem).filter(MenuItem.restaurant_id == restaurant.id).all()
        selected_items = random.sample(menu_items, min(random.randint(1, 4), len(menu_items)))

        subtotal = sum(item.price for item in selected_items)
        delivery_fee = restaurant.delivery_fee
        total = subtotal + delivery_fee

        order = FoodOrder(
            customer_id=customer.id,
            restaurant_id=restaurant.id,
            driver_id=driver.id if driver and status not in [OrderStatus.PENDING, OrderStatus.CONFIRMED] else None,
            status=status,
            delivery_address=f"{random.randint(100, 999)} {random.choice(['Main', 'Oak', 'Pine', 'Elm'])} St, New York, NY 10001",
            delivery_latitude=40.7128 + random.uniform(-0.05, 0.05),
            delivery_longitude=-74.0060 + random.uniform(-0.05, 0.05),
            subtotal=subtotal,
            delivery_fee=delivery_fee,
            total_amount=total,
            special_instructions=random.choice([None, "Please ring doorbell", "Leave at door", "Extra napkins please"]),
            created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
        )
        db.add(order)
        db.flush()

        for item in selected_items:
            quantity = random.randint(1, 3)
            order_item = OrderItem(
                order_id=order.id,
                menu_item_id=item.id,
                quantity=quantity,
                unit_price=item.price,
                total_price=item.price * quantity,
            )
            db.add(order_item)

        orders.append(order)

    db.commit()
    print(f"  Created {len(orders)} food orders")
    return orders


def create_parcels(db, users):
    """Create sample parcel deliveries"""
    print("Creating parcel deliveries...")

    parcels = []
    statuses = list(ParcelStatus)
    sizes = list(ParcelSize)

    for i in range(8):
        sender = random.choice(users['customers'])
        driver = random.choice(users['drivers']) if random.random() > 0.3 else None
        status = random.choice(statuses)
        size = random.choice(sizes)

        # Calculate fee based on size
        base_fee = {"small": 5.99, "medium": 9.99, "large": 14.99}
        delivery_fee = Decimal(str(base_fee.get(size.value, 9.99)))

        parcel = ParcelDelivery(
            sender_id=sender.id,
            driver_id=driver.id if driver and status not in [ParcelStatus.PENDING] else None,
            recipient_name=f"{random.choice(['John', 'Jane', 'Bob', 'Alice'])} {random.choice(['Smith', 'Doe', 'Johnson', 'Williams'])}",
            recipient_phone=f"+1555{random.randint(1000000, 9999999)}",
            pickup_address=f"{random.randint(100, 999)} {random.choice(['Main', 'Oak', 'Pine'])} St, New York, NY",
            pickup_latitude=40.7128 + random.uniform(-0.05, 0.05),
            pickup_longitude=-74.0060 + random.uniform(-0.05, 0.05),
            delivery_address=f"{random.randint(100, 999)} {random.choice(['Elm', 'Maple', 'Cedar'])} Ave, New York, NY",
            delivery_latitude=40.7128 + random.uniform(-0.05, 0.05),
            delivery_longitude=-74.0060 + random.uniform(-0.05, 0.05),
            parcel_description=random.choice([
                "Documents", "Small package", "Gift box", "Electronics", "Books", "Clothing"
            ]),
            parcel_size=size,
            status=status,
            delivery_fee=delivery_fee,
            estimated_distance_km=round(random.uniform(1.0, 15.0), 1),
            created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
        )
        db.add(parcel)
        parcels.append(parcel)

    db.commit()
    print(f"  Created {len(parcels)} parcel deliveries")
    return parcels


def create_reviews(db, users, restaurants):
    """Create sample reviews"""
    print("Creating reviews...")

    reviews = []

    # Restaurant reviews
    for restaurant in restaurants:
        num_reviews = random.randint(2, 5)
        reviewers = random.sample(users['customers'], min(num_reviews, len(users['customers'])))

        for reviewer in reviewers:
            review = Review(
                reviewer_id=reviewer.id,
                target_type=TargetType.RESTAURANT,
                target_id=restaurant.id,
                rating=random.randint(3, 5),
                comment=random.choice([
                    "Great food! Highly recommend!",
                    "Delicious meals, fast delivery",
                    "Good quality, will order again",
                    "Amazing flavors!",
                    "Very satisfied with my order",
                    None,
                ]),
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 60)),
            )
            db.add(review)
            reviews.append(review)

    # Driver reviews
    for driver in users['drivers']:
        num_reviews = random.randint(1, 3)
        reviewers = random.sample(users['customers'], min(num_reviews, len(users['customers'])))

        for reviewer in reviewers:
            review = Review(
                reviewer_id=reviewer.id,
                target_type=TargetType.DRIVER,
                target_id=driver.id,
                rating=random.randint(4, 5),
                comment=random.choice([
                    "Very fast delivery!",
                    "Friendly and professional",
                    "Great service",
                    "On time delivery",
                    None,
                ]),
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 60)),
            )
            db.add(review)
            reviews.append(review)

    db.commit()
    print(f"  Created {len(reviews)} reviews")
    return reviews


def main():
    print("=" * 50)
    print("Dago Food & Parcel Delivery - Database Seeding")
    print("=" * 50)

    db = SessionLocal()

    try:
        # Clear existing data
        clear_data(db)

        # Create data
        users = create_users(db)
        restaurants = create_restaurants(db)
        orders = create_orders(db, users, restaurants)
        parcels = create_parcels(db, users)
        reviews = create_reviews(db, users, restaurants)

        print("\n" + "=" * 50)
        print("Database seeding completed successfully!")
        print("=" * 50)
        print("\nTest Accounts:")
        print("-" * 50)
        print("Admin:    admin@dago.com / admin123")
        print("Driver:   john.driver@dago.com / driver123")
        print("Customer: alice@example.com / customer123")
        print("-" * 50)

    except Exception as e:
        print(f"\nError during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
