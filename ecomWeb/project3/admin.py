from flask import Blueprint, render_template, flash, current_app, send_from_directory,redirect, request
from flask_login import login_required, current_user
from .forms import ShopItems, OrdersForm
from werkzeug.utils import secure_filename
from .models import Product, Order, Customer
from .init import db  # Import the db object to interact with the database
import os

admin = Blueprint("admin", '__name__')


@admin.route('/media/<path:filename>')    
def get_image(filename):
    return send_from_directory('static/media', filename) 
@admin.route('/add-shop-items', methods=['GET', 'POST'])
def add_shop_items():
    if current_user.id == 1:
        form = ShopItems()
        if form.validate_on_submit():
            product_name = form.product_name.data 
            current_price = form.current_price.data
            previous_price = form.previous_price.data
            in_stock = form.in_stock.data
            flash_sale = form.flash_sale.data

            file = form.product_picture.data
            file_name = secure_filename(file.filename)
           
            save_path = os.path.join(current_app.root_path, 'static', 'media', file_name)

           
            file_path = f'/static/media/{file_name}'
            file.save(save_path)

            new_shop_items = Product()
            new_shop_items.product_name = product_name
            new_shop_items.current_price = current_price
            new_shop_items.previous_price = previous_price
            new_shop_items.in_stock = in_stock
            new_shop_items.product_picture = file_path 

            
            try:
                db.session.add(new_shop_items) 
                db.session.commit()
                flash(f'{product_name} Product added successfully!', 'success')
                print('product added successfully')
                return render_template('add-shop-items.html', form=form)
            except Exception as e:
                print(e)
                flash('item not added', 'danger')
            


        return render_template('add-shop-items.html', form=form)
    return render_template('404.html')

@admin.route('/shop-items', methods=['GET', 'POST'])
@login_required
def shop_items():
    if current_user.id == 1:
        items = Product.query.order_by(Product.date_added).all()

        return render_template('shop_items.html', items=items)
    return render_template('404.html')

@admin.route('/update-item/<int:id>', methods=['GET', 'POST'])
@login_required
def update_item(id):
    if current_user.id == 1:
        form = ShopItems()
        item = Product.query.get(id)        
        if request.method == 'GET':
            form.product_name.data = item.product_name    
            form.current_price.data = item.current_price
            form.previous_price.data = item.previous_price
            form.in_stock.data = item.in_stock
            form.flash_sale.data = item.flash_sale

        if form.validate_on_submit():
            product_name = form.product_name.data  
            current_price = form.current_price.data
            previous_price = form.previous_price.data   
            in_stock = form.in_stock.data
            flash_sale = form.flash_sale.data

            file = form.product_picture.data
            save_path = os.path.join(current_app.root_path, 'static', 'media', file.filename)
            file_name = secure_filename(file.filename)
            file_path = (f'/static/media/{file_name}')

            file.save(save_path) 
            try:      
                Product.query.filter_by(id=id).update(dict( product_name=product_name,          
                                                            current_price=current_price,
                                                            previous_price=previous_price,
                                                            in_stock=in_stock,
                                                            flash_sale=flash_sale,
                                                            product_picture=file_path))    
                db.session.commit()  
                flash(f'{product_name} Product updated successfully!', 'success')
                print('product updated successfully')
                return redirect('/admin/shop-items')  
            except Exception as e:
                print(e)
                flash('item not updated', 'danger')

        return render_template('update_item.html', form=form)
    return render_template('404.html')

    
@admin.route('/delete-item/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_item(id):
    if current_user.id == 1:
        try:
            item = Product.query.get(id)
                
            db.session.delete(item)  
            db.session.commit()
            flash(f' Product deleted successfully!', 'success')
            return redirect('/admin/shop-items')
        except Exception as e:
            print(e)
            flash('item not deleted', 'danger')
        return redirect('/admin/shop-items')
    return render_template('404.html')


@admin.route('/view_orders')
def view_orders():
    if current_user.id == 1:
        orders = Order.query.all()
        return render_template('view_order.html', orders=orders)
    return render_template('404.html')


@admin.route('/update_order/<int:id>', methods=['GET', 'POST'])
@login_required
def update_order(id):
    if current_user.id == 1:
        form = OrdersForm()
        order = Order.query.get(id) 

        if request.method == 'GET':
            form.order_status.data = order.status   

        if form.validate_on_submit():
            status = form.order_status.data
            order.status = status  
            
            try:
                db.session.commit() 

                flash(f' Order status updated successfully!', 'success')
                return redirect('/admin/view_orders')

            except Exception as e:
                print(e)
                flash('Order status not updated', 'danger')
                return redirect('/admin/view_orders')
            


        return render_template('order_update.html', form=form)
    return render_template('404.html')


@admin.route('/customers')
@login_required
def customers():
    if current_user.id == 1:
        customers = Customer.query.all()
        return render_template('customers.html', customers=customers)
    return render_template('404.html')


@admin.route('/admin_home')
@login_required
def admin_home():
    if current_user.id == 1:
        return render_template('admin_home.html')

    return render_template('404.html')
