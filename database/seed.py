from faker import Faker
import random

from app import app
from database.database import db, bcrypt
from database.models import User, Customer, Sale, Competitor, Location

fake = Faker()

cities = ["Nagpur", "Pune", "Mumbai", "Nashik", "Amravati", "Aurangabad"]

areas = [
    "Dharampeth",
    "Sitabuldi",
    "Civil Lines",
    "Sadar",
    "Wardha Road",
    "Manish Nagar",
    "Trimurti Nagar",
    "Andheri",
    "Kothrud",
    "Gangapur"
]

products = [
    "Laptop",
    "Smartphone",
    "Headphones",
    "Shoes",
    "Watch",
    "Keyboard",
    "Mouse",
    "Printer",
    "Tablet",
    "Backpack"
]

payment_methods = [
    "Cash",
    "UPI",
    "Credit Card",
    "Debit Card",
    "Net Banking"
]

categories = [
    "Electronics",
    "Fashion",
    "Restaurant",
    "Medical",
    "Furniture",
    "Grocery"
]

business_names = [
    "Vision Mart",
    "Tech World",
    "Metro Store",
    "Retail King",
    "Prime Outlet",
    "Urban Market",
    "Digital Hub",
    "Mega Store",
    "Business Point",
    "City Electronics"
]

with app.app_context():

    db.drop_all()
    db.create_all()

    users = []

    # ---------------- Users ----------------

    for i in range(5):
        user = User(
            name=fake.name(),
            email=fake.unique.email(),
            password=bcrypt.generate_password_hash("password123").decode("utf-8")
        )
        db.session.add(user)
        users.append(user)

    db.session.commit()

    # ---------------- Customers ----------------

    customers = []

    for i in range(50):

        city = random.choice(cities)
        area = random.choice(areas)

        customer = Customer(
            user_id=random.choice(users).id,
            customer_name=fake.name(),
            age=random.randint(18, 65),
            gender=random.choice(["Male", "Female"]),
            city=city,
            area=area,
            latitude=round(random.uniform(18.5, 21.5), 6),
            longitude=round(random.uniform(73.0, 79.5), 6),
            purchase_frequency=random.randint(1, 30),
            total_spent=round(random.uniform(1000, 50000), 2)
        )

        db.session.add(customer)
        customers.append(customer)

    db.session.commit()

    # ---------------- Sales ----------------

    for i in range(100):

        sale = Sale(
            customer_id=random.choice(customers).customer_id,
            product=random.choice(products),
            quantity=random.randint(1, 5),
            amount=round(random.uniform(500, 50000), 2),
            sale_date=fake.date_time_between(start_date="-2y", end_date="now"),
            payment_method=random.choice(payment_methods)
        )

        db.session.add(sale)

    db.session.commit()

    # ---------------- Competitors ----------------

    for i in range(20):

        competitor = Competitor(
            business_name=random.choice(business_names),
            category=random.choice(categories),
            city=random.choice(cities),
            area=random.choice(areas),
            latitude=round(random.uniform(18.5, 21.5), 6),
            longitude=round(random.uniform(73.0, 79.5), 6),
            rating=round(random.uniform(3.0, 5.0), 1)
        )

        db.session.add(competitor)

    db.session.commit()

    # ---------------- Locations ----------------

    for i in range(15):

        location = Location(
            city=random.choice(cities),
            area=random.choice(areas),
            latitude=round(random.uniform(18.5, 21.5), 6),
            longitude=round(random.uniform(73.0, 79.5), 6),
            population=random.randint(10000, 150000),
            average_rent=round(random.uniform(12000, 70000), 2),
            customer_density=round(random.uniform(100, 1200), 2),
            competitor_count=random.randint(0, 20)
        )

        db.session.add(location)

    db.session.commit()

    print("Database seeded successfully!")