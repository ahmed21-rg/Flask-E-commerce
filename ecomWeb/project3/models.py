from .init import db 
from flask_login import UserMixin 
from datetime import datetime  
from flask_bcrypt import generate_password_hash, check_password_hash 

class Customer(db.Model, UserMixin): 
    id = db.Column(db.Integer, primary_key=True) 
    username = db.Column(db.String(50), nullable=False)  
    email = db.Column(db.String(100), unique=True, nullable=False) 
    password = db.Column(db.String(150), nullable=False)  
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)  
    cart_items = db.relationship('Cart', backref=db.backref('user', lazy=True)) 
    orders = db.relationship('Order', backref=db.backref('customer', lazy=True)) 

    def __repr__(self): 

        return f"Customer('{self.username}', '{self.email}')"

    def verify_password (self, password):
        return check_password_hash(self.password, password)  
class Product(db.Model): 
    id = db.Column(db.Integer, primary_key=True)  
    product_name = db.Column(db.String(100), nullable=False)  
    description = db.Column(db.String(500), nullable=True)  
    current_price = db.Column(db.Float, nullable=False)
    previous_price = db.Column(db.Float, nullable=False) 
    product_picture = db.Column(db.String(1500), nullable=True) 
    in_stock = db.Column(db.Integer, default=0) 
    flash_sale = db.Column(db.Boolean, default=False) 
    date_added = db.Column(db.DateTime, default=datetime.utcnow)  
    carts = db.relationship('Cart', backref=db.backref('product', lazy=True)) 
    orders = db.relationship('Order',backref=db.backref('product', lazy=True)) 


    def __repr__(self):  
        return f"Product('{self.product_name}', '{self.current_price}')"


class Cart(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, default=0) 
    customer_link = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False) 
    product_link = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)  

    def __repr__(self):
        return f'(Cart {self.id} - {self.product_link})'

class Order(db.Model): 
    id = db.Column(db.Integer, primary_key=True) 
    price = db.Column(db.Float, nullable=False)
    payment_id = db.Column(db.String(1000), nullable=False)
    quantity = db.Column(db.Integer, default=1) 
    status = db.Column(db.String(50), nullable=False)

    customer_link = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False) 
    product_link = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False) 

    def __repr__(self): 

        return f"Order('{self.id}', '{self.price}', '{self.status}')"
