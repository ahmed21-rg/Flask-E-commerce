from flask import Blueprint, render_template, flash, redirect, request, jsonify, url_for, current_app
from .models import Product, Cart, Order
import stripe
from flask_login import login_required, current_user
from .init import db



views = Blueprint("views",__name__)



@views.route('/')
@views.route('/home')
def home():
    items= Product.query.filter_by(flash_sale=True)      # Fetch items with flash sale
    return render_template('home.html', items=items, cart= Cart.query.filter_by(customer_link=current_user.id).all()  # Pass cart items if user is authenticated
                           if current_user.is_authenticated else [])  # Pass cart items if user is authenticated


@views.route('/add-to-cart/<int:id>')
@login_required
def add_to_cart(id):
    # Get the product with the given id from the Product table.
    # If no product exists with that id, Flask will return a 404 page.
    item_to_add = Product.query.get_or_404(id)

    # Check if the current user already has this product in their cart.
    # filter_by returns a query; .first() returns the first matching row or None.
    item_exists = Cart.query.filter_by(product_link=id, customer_link=current_user.id).first()

    # If the item is already in the cart, increase its quantity
    if item_exists:
        try:
            # Increment the quantity field on the existing cart row
            item_exists.quantity += 1
            # Save the change to the database
            db.session.commit()
            # Show a success message to the user
            flash('Item quantity updated in cart.', 'success')
        except Exception as e:
            # If something goes wrong, print/log the exception (for debugging)
            print(e)
            # Roll back the transaction so the session stays consistent
            db.session.rollback()
            flash('Failed to update item in cart.', 'danger')

    # If the item is not in the cart yet, create a new Cart row
    else:
        new_cart_item = Cart()                 # Create a new Cart model instance
        new_cart_item.quantity = 1            # First time adding, so quantity = 1
        new_cart_item.product_link = item_to_add.id   # Link the cart row to this product
        new_cart_item.customer_link = current_user.id # Link the cart row to the logged-in user

        try:
            # Add the new cart row to the session and commit it to the DB
            db.session.add(new_cart_item)
            db.session.commit()
            # Notify the user of success
            flash('Item added to cart.', 'success')
        except Exception as e:
            # Log/print the error for debugging
            print('Error adding item to cart:', e)
            # Roll back the failed transaction
            db.session.rollback()
            # Notify the user of failure
            flash('Failed to add item to cart.', 'danger')

    # Redirect the user back to the homepage (or change this to redirect('/cart') if you prefer)
    return redirect('/')


@views.route('/cart')
@login_required
def cart():
    cart = Cart.query.filter_by(customer_link=current_user.id).all()
    
    amount = 0
    for item in cart:

        amount += item.product.current_price * item.quantity
    return render_template('cart.html', cart=cart, amount=amount, total=amount + 100)  # Assuming a flat shipping fee of 100

@views.route('/pluscart')
@login_required
def plus_cart():
    if request.method == 'GET':
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)
        cart_item.quantity = cart_item.quantity + 1
        db.session.commit()

        cart = Cart.query.filter_by(product_link=current_user.id).all()

        amount = 0
        for item in cart:
            amount+= item.product.current_price * item.quantity

        data = {
            'quantity': cart_item.quantity,
            'amount': amount,
            'total': amount + 200
        }

        return jsonify(data)
    

@views.route('/minuscart')
@login_required
def minus_cart():
    if request.method == 'GET':
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)
        cart_item.quantity = cart_item.quantity - 1
        db.session.commit()

        cart = Cart.query.filter_by(product_link=current_user.id).all()

        amount = 0
        for item in cart:
            amount+= item.product.current_price * item.quantity

        data = {
            'quantity': cart_item.quantity,
            'amount': amount,
            'total': amount + 200
        }

        return jsonify(data)

@views.route('/removecart/<int:id>')
@login_required
def remove_item(id):

        cart_item = Cart.query.get(id)            # gets the item id
        if cart_item and cart_item.customer_link == current_user.id:    #if cart item and customer id are same as curruser id 
            quantity = cart_item.quantity    
            db.session.delete(cart_item)
            db.session.commit()

        cart = Cart.query.filter_by(customer_link=current_user.id).all()

        amount = 0
        for item in cart:
            amount+= item.product.current_price * item.quantity

        data = {
            'quantity': quantity,
            'amount': amount,
            'total': amount + 200
        }

        return jsonify(data)



@views.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    try:
        # Fetch all the cart items for this user
        cart_items = Cart.query.filter_by(customer_link=current_user.id).all()

        # If cart is empty
        if not cart_items:
            flash('Your cart is empty!', 'warning')
            return redirect(url_for('views.cart'))

        # Build Stripe line items
        line_items = []
        for cart_item in cart_items:
            product = Product.query.get(cart_item.product_link)  # <-- fetch product
            if not product:
                flash('One of your products no longer exists.', 'danger')
                return redirect(url_for('views.cart'))

            line_items.append({
                "price_data": {
                    "currency": "usd",  # or your currency code
                    "product_data": {
                        "name": product.product_name,
                        "description": product.description or "NO Description Available",
                    },
                    "unit_amount": int(product.current_price *100),  # Stripe expects amount in cents, so multiply by 100
                },
                "quantity": cart_item.quantity,
            })

        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],  # correct key name is plural
            line_items=line_items,
            mode='payment',
            success_url=url_for('views.payment_success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('views.cart', _external=True),
        )

        return redirect(checkout_session.url, code=303)

    except Exception as e:
        print(e)
        flash('Payment failed. Please contact support.', 'danger')
        return redirect(url_for('views.cart'))

@views.route("/payment-success")
@login_required
def payment_success():
    session_id = request.args.get("id")
    if session_id:
        session = stripe.checkout.Session.retrieve(id)
        payment_intent = stripe.PaymentIntent.retrieve(session.payment_intent)

        # Save order details in DB
        cart_items = Cart.query.filter_by(customer_link=current_user.id).all()
        for cart_item in cart_items:
            order = Order(
                price=cart_item.product.current_price * cart_item.quantity,
                payment_id=payment_intent.id,
                quantity=cart_item.quantity,
                status="Paid",
                customer_link=current_user.id,
                product_link=cart_item.product.id,          
            )
            db.session.add(order)

        product = Cart.query.filter_by(customer_link=current_user.id).all()
        for item in product:
            db.session.delete(item)


        # Clear cart
        
        db.session.commit()

        flash("Payment successful! Your order has been placed.", "success")

    return render_template("success.html")

@views.route('/orders')
@login_required
def orders():
    user_orders = Order.query.filter_by(customer_link=current_user.id).all()
    return render_template('orders.html', orders=user_orders)