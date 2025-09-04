from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField, SubmitField, EmailField, IntegerField, FloatField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange
from flask_wtf.file import FileField, FileRequired


class Signup_Form(FlaskForm):
    email = EmailField('email', validators=[DataRequired(), Email()])
    username = StringField('username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Enter your password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    

class Login_Form(FlaskForm):
     email = EmailField('email', validators=[DataRequired(), Email()])
     password = PasswordField('Enter your password', validators=[DataRequired(), Length(min=6)])
     remember = BooleanField('Remember Me')
     submit = SubmitField('Login')
     submit = SubmitField('Login')
    
class ChangePassword(FlaskForm):
     current_password = PasswordField('current_password', validators=[DataRequired()])
     new_password = PasswordField('new_password', validators=[DataRequired(), Length(min=6)])
     confirm_new_password = PasswordField('confirm_new_password', validators=[DataRequired(), EqualTo('new_password')]) 
     change_password = SubmitField('Change Password')

class ShopItems(FlaskForm):
     product_name = StringField('Product Name', validators=[DataRequired()])
     current_price = FloatField('Current_Price', validators=[DataRequired()])
     previous_price = FloatField('previous_price', validators=[DataRequired()])
     in_stock = IntegerField('In Stock', validators=[DataRequired()])
     product_picture = FileField('Product picture', validators=[FileRequired()])
     flash_sale = BooleanField('sale')

     add_product = SubmitField('Add Product')
     update_product = SubmitField('Update Product')


class OrdersForm(FlaskForm):
    order_status = SelectField('Order Status',choices=[("Pending", "Pending"), ("Accepted", "Accepted"),
                                                                                 ("Out for delivery", "Out for delivery"),
                                                                                 ("Delivered", "Delivered"),
                                                                                   ("Canceled", "Canceled")])
    update = SubmitField('Update Status')