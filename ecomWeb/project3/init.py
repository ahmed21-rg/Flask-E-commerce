from flask_bcrypt import Bcrypt  # Only import from flask_bcrypt
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import stripe  # Import stripe for payment processing
import os
from dotenv import load_dotenv





db = SQLAlchemy()  # Create the SQLAlchemy database object
bcrypt = Bcrypt()  # Create the Bcrypt object

def create_app():

    load_dotenv()    

    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    bcrypt.init_app(app) # Initialize Bcrypt with the Flask app
    app.config['STRIPE_PUBLIC_KEY'] = ("STRIPE_PUBLIC_KEY")
    stripe.api_key = os.getenv("STRIPE_API_KEY")
    
    db.init_app(app)  # Bind SQLAlchemy to your Flask app

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('404.html')


    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Set the login view for Flask-Login

    @login_manager.user_loader
    def load_user(id):
        return Customer.query.get(int(id))


    from .views import views
    from .authen import auth
    from .admin import admin 
    from .models import Customer, Product, Cart, Order

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(admin, url_prefix='/admin')

    with app.app_context():
        db.create_all()

    return app