from flask_bcrypt import check_password_hash
from flask import Blueprint, render_template, flash, redirect
from .forms import Signup_Form, Login_Form, ChangePassword
from .models import Customer, db
from .init import bcrypt  
from flask_login import login_user, logout_user, current_user, login_required

auth = Blueprint("auth", __name__)  

@auth.route("/login", methods=['GET', 'POST'])
def login():
    form = Login_Form()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        customer = Customer.query.filter_by(email=email).first()
        if customer and check_password_hash(customer.password, password):
            login_user(customer) 
            flash('Login successful!', 'success')
            return redirect('/home')
    return render_template('login.html', form=form)

@auth.route("/Signup", methods=['GET', 'POST'])
def Signup():
    form = Signup_Form()
    if form.validate_on_submit():
        email = form.email.data
        username = form.username.data
        password = form.password.data
        confirm_password = form.confirm_password.data
        
        existing_email = Customer.query.filter_by(email=email).first()
        if existing_email:
            flash('Email already exists. Please use a different email.', 'danger')
            return redirect('/Signup')

        if password == confirm_password:
            password_h = bcrypt.generate_password_hash(password).decode('utf-8')  
            new_customer = Customer(username=username, email=email, password=password_h)            
        
            db.session.add(new_customer)
            db.session.commit() 
            flash('Account created successfully! You can now log in.', 'success')
            return redirect('/home')

        else:
            flash("Passwords do not match!", 'danger')

    return render_template('signup.html', form=form)

@auth.route("/logout", methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect('/home')

@auth.route('/profile/<int:id>')
@login_required
def profile(id):
  
    customer = Customer.query.get(id)
   
    return render_template('profile.html', customer=customer)

@auth.route('/change_password/<int:id>' ,methods=['GET', 'POST'])
@login_required
def change_password(id):
    form  = ChangePassword()
    customer = Customer.query.get_or_404(id)
    if current_user.id != customer.id:
        flash('You do not have permission to change this password.', 'danger')
        return redirect('/home')
    
    if form.validate_on_submit():

        current_password = form.current_password.data
        new_password = form.new_password.data
        confirm_new_password = form.confirm_new_password.data
        
            
        if customer.verify_password(current_password):
            if new_password == confirm_new_password:
                customer.set_password(new_password)  
                db.session.commit()
                flash('Password changed successfully!', 'success')
                return redirect('/home')
            else:
                flash('New passwords do not match!', 'danger')
        else: 
            flash('Current password is incorrect!', 'danger')
    return render_template('change_password.html', form=form)



