from .init import db  # Import db from init.py
from flask_login import UserMixin  # Import UserMixin to add Flask-Login support for user authentication
from datetime import datetime  # Import datetime for handling date and time fields
from flask_bcrypt import generate_password_hash, check_password_hash  # Import generate_password_hash for secure password hashing

class Customer(db.Model, UserMixin):  # Define the Customer table/model, also supports Flask-Login
    id = db.Column(db.Integer, primary_key=True)  # Unique identifier for each customer (primary key)
    username = db.Column(db.String(50), nullable=False)  # Customer's username, required field
    email = db.Column(db.String(100), unique=True, nullable=False)  # Customer's email, must be unique and required
    password = db.Column(db.String(150), nullable=False)  # Hashed password for authentication, required
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp when the customer joined, defaults to now
    cart_items = db.relationship('Cart', backref=db.backref('user', lazy=True))  # One-to-many relationship: customer can have multiple cart items
    orders = db.relationship('Order', backref=db.backref('customer', lazy=True))  # One-to-many relationship: customer can have multiple orders

    def __repr__(self):  # String representation for debugging and logging
        # Shows username and email for easy identification in logs and shell
        return f"Customer('{self.username}', '{self.email}')"

    def verify_password (self, password):
        return check_password_hash(self.password, password)  # Verify the provided password against the stored hash

class Product(db.Model):  # Define the Product table/model
    id = db.Column(db.Integer, primary_key=True)  # Unique identifier for each product (primary key)
    product_name = db.Column(db.String(100), nullable=False)  # Name of the product, required
    description = db.Column(db.String(500), nullable=True)  # Description of the product, optional
    current_price = db.Column(db.Float, nullable=False)  # Current price of the product, required
    previous_price = db.Column(db.Float, nullable=False)  # Previous price of the product, required (for showing discounts)
    product_picture = db.Column(db.String(1500), nullable=True)  # URL or path to the product image, optional
    in_stock = db.Column(db.Integer, default=0)  # Number of items in stock, defaults to 0
    flash_sale = db.Column(db.Boolean, default=False)  # Boolean flag for flash sale status, defaults to False
    date_added = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp when the product was added, defaults to now
    carts = db.relationship('Cart', backref=db.backref('product', lazy=True))  # One-to-many relationship: product can be in multiple carts
    orders = db.relationship('Order',backref=db.backref('product', lazy=True))  # One-to-many relationship: product can be in multiple orders


    def __repr__(self):  # String representation for debugging and logging
        # Shows product name and current price for easy identification in logs and shell
        return f"Product('{self.product_name}', '{self.current_price}')"


class Cart(db.Model):  # Define the Cart table/model
    id = db.Column(db.Integer, primary_key=True)  # Unique identifier for each cart item (primary key)
    quantity = db.Column(db.Integer, default=0)  # Number of products in this cart item, defaults to 0
    customer_link = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)  # Foreign key linking to the customer who owns this cart item
    product_link = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)  # Foreign key linking to the product in this cart item

    def __repr__(self):  # String representation for debugging and logging
        # Shows cart id and product link for easy identification
        return f'(Cart {self.id} - {self.product_link})'

class Order(db.Model):  # Define the Order table/model
    id = db.Column(db.Integer, primary_key=True)  # Unique identifier for each order (primary key)
    price = db.Column(db.Float, nullable=False)  # Total price for the order, required
    payment_id = db.Column(db.String(1000), nullable=False)  # Payment transaction ID, required for tracking payments
    quantity = db.Column(db.Integer, default=1)  # Number of products ordered, defaults to 1
    status = db.Column(db.String(50), nullable=False)  # Status of the order (e.g., pending, shipped), required

    customer_link = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)  # Foreign key linking to the customer who placed the order
    product_link = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)  # Foreign key linking to the product ordered

    def __repr__(self):  # String representation for debugging and logging
        # Shows order id, price, and status for easy identification
        return f"Order('{self.id}', '{self.price}', '{self.status}')"