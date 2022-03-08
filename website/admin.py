
from distutils.command.config import config
from flask import Blueprint, render_template, flash, request, request_started, session, url_for, redirect
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import stripe
import os
# added import for 'Item' table
from .models import Employee, Item, Cart
from . import db, UPLOAD_FOLDER, ALLOWED_EXTENSIONS
from werkzeug.security import generate_password_hash, check_password_hash
from.menu import get_items


admin = Blueprint('admin', __name__)

@admin.route('/edititems', methods=['POST', 'GET'])
def website_admin():
  if request.method == 'POST':
    name = request.form.get('name')
    price = request.form.get('price')
    description = request.form.get('description')
    image = request.files['image']
    if image and allowed_file(image.filename):
      filename = secure_filename(image.filename)
      image.save(os.path.join(UPLOAD_FOLDER, filename))
    imagename = filename
    add_item = Item(name=name, price=price, description=description, item_image=imagename)
    db.session.add(add_item)
    db.session.commit()
    flash('Added to Menu', category='success')
    return redirect(url_for('admin.website_admin'))
  user_id = current_user.id
  if user_id != 1:
    return redirect(url_for('views.home'))
  else:
    rows = Cart.query.filter(Cart.id).count()
    return render_template('edititems.html', user=current_user, items=get_items(), rows=rows)


@admin.route('/editusers', methods=['POST', 'GET'])
def editusers():
  # if admin adds a new user
  if request.method == 'POST':
    # take all of this information entered by admin inside of html
    email = request.form.get('email')
    first_name = request.form.get('firstName')
    phone = request.form.get('phone')
    password1 = request.form.get('password1')
    password2 = request.form.get('password2')
    # search table by email entered
    employee = Employee.query.filter_by(email=email).first()
    # check if email is already inside of table and all info meets requirements below
    if employee:
      # if it is flask this message
      flash('Email already exists.', category='error')
    elif len(email) < 4:
      flash('Email must be greater than 3 characters.', category='error')
    elif len(first_name) < 2:
      flash('First name must be greater than 1 character.', category='error')
    elif password1 != password2:
      flash('Passwords don\'t match.', category='error')
    elif len(password1) < 7:
      flash('Password must be at least 7 characters.', category='error')
    else:
      # create new user by passing data into variable called 'new_user'
      new_user = Employee(email=email, first_name=first_name, phone=phone, password=generate_password_hash(
          password1, method='sha256'))
      # pass new_user into database
      db.session.add(new_user)
      # save database with new_user passed
      db.session.commit()
      flash('Account created!', category='success')
      # redirect to the same page admin was already on
      return redirect(url_for('admin.editusers'))
      # end of post request
  # rows to track cart quantity
  rows = Cart.query.filter(Cart.id).count()
  return render_template('editusers.html', user=current_user, account=getusers(), rows=rows)


@admin.route('/remove_menu_item/<int:id>')
def remove_menu_item(id):
  item_to_delete = Item.query.get_or_404(id)
  try:
    db.session.delete(item_to_delete)
    db.session.commit()
    ids = [id[0] for id in Item.query.with_entities(Item.id).all()] # fixed
    new_id = 1
    for i in ids:
      _id = Item.query.get(i)
      _id.id = new_id
      new_id += 1
      db.session.commit()
    flash('Item removed from menu')
    return redirect(url_for('views.admin'))
  except:
    flash('Problem removing item from cart')
    return redirect(url_for('views.admin'))


def getusers():
  ids = [id[0] for id in Employee.query.with_entities(Employee.id).all()]
  accounts = []
  for id in ids:
    employee = Employee.query.filter_by(id=id).first()
    grabber = {'id': 0, 'first_name': '', 'email': 0, 'password': '', 'phone': ''}
    grabber['id'] = employee.id
    grabber['first_name'] = employee.first_name
    grabber['email'] = employee.email
    grabber['password'] = employee.password
    grabber['phone'] = employee.phone
    accounts.append(grabber)
  return accounts


def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
