from datetime import datetime

from flask_login import UserMixin

from database.database import db
from database.database import login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    password = db.Column(db.String(255), nullable=False)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    customers = db.relationship(
    "Customer",
    backref="user",
    lazy=True
)
    
    def __repr__(self):
        return f"<User {self.email}>"

    # ------------------- Customer Table -------------------

class Customer(db.Model):
    __tablename__ = "customers"

    customer_id = db.Column(db.Integer, primary_key=True)



    customer_name = db.Column(db.String(100), nullable=False)

    age = db.Column(db.Integer)

    gender = db.Column(db.String(10))

    city = db.Column(db.String(100))

    area = db.Column(db.String(100))

    latitude = db.Column(db.Float)

    longitude = db.Column(db.Float)

    purchase_frequency = db.Column(db.Integer)

    total_spent = db.Column(db.Float)

    # Relationship with Sales
    sales = db.relationship("Sale", backref="customer", lazy=True)

    def __repr__(self):
        return f"<Customer {self.customer_name}>"



# ------------------- Sales Table -------------------

class Sale(db.Model):
    __tablename__ = "sales"

    sale_id = db.Column(db.Integer, primary_key=True)

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("customers.customer_id"),
        nullable=False
    )

    product = db.Column(db.String(100), nullable=False)

    quantity = db.Column(db.Integer, nullable=False)

    amount = db.Column(db.Float, nullable=False)

    sale_date = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    payment_method = db.Column(db.String(50))

    def __repr__(self):
        return f"<Sale {self.sale_id}>"



# ------------------- Competitor Table -------------------

class Competitor(db.Model):
    __tablename__ = "competitors"

    competitor_id = db.Column(db.Integer, primary_key=True)

    business_name = db.Column(db.String(150), nullable=False)

    category = db.Column(db.String(100))

    city = db.Column(db.String(100))

    area = db.Column(db.String(100))

    latitude = db.Column(db.Float)

    longitude = db.Column(db.Float)

    rating = db.Column(db.Float)

    def __repr__(self):
        return f"<Competitor {self.business_name}>"



# ------------------- Location Table -------------------

class Location(db.Model):
    __tablename__ = "locations"

    location_id = db.Column(db.Integer, primary_key=True)

    city = db.Column(db.String(100), nullable=False)

    area = db.Column(db.String(100), nullable=False)

    latitude = db.Column(db.Float)

    longitude = db.Column(db.Float)

    population = db.Column(db.Integer)

    average_rent = db.Column(db.Float)

    customer_density = db.Column(db.Float)

    competitor_count = db.Column(db.Integer)

    def __repr__(self):
        return f"<Location {self.city} - {self.area}>"

    