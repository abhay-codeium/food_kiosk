from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime
import os
from models import db, User, MenuItem, Order, OrderItem
from forms import LoginForm, RegistrationForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this to a secure secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kiosk.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

# Admin routes
@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash('Access denied: Admin privileges required')
        return redirect(url_for('index'))
    orders = Order.query.all()
    menu_items = MenuItem.query.all()
    return render_template('admin.html', orders=orders, menu_items=menu_items)

@app.route('/admin/menu/add', methods=['POST'])
@login_required
def add_menu_item():
    if not current_user.is_admin:
        return jsonify({'error': 'Admin privileges required'}), 403
    data = request.get_json()
    item = MenuItem(
        name=data['name'],
        price=data['price'],
        category=data['category'],
        description=data.get('description', ''),
        available=True
    )
    db.session.add(item)
    db.session.commit()
    return jsonify({'message': 'Menu item added successfully'})

@app.route('/admin/menu/update/<int:item_id>', methods=['PUT'])
@login_required
def update_menu_item(item_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Admin privileges required'}), 403
    item = MenuItem.query.get_or_404(item_id)
    data = request.get_json()
    item.name = data.get('name', item.name)
    item.price = data.get('price', item.price)
    item.category = data.get('category', item.category)
    item.description = data.get('description', item.description)
    item.available = data.get('available', item.available)
    db.session.commit()
    return jsonify({'message': 'Menu item updated successfully'})

# Customer routes
@app.route('/')
def index():
    menu_items = MenuItem.query.filter_by(available=True).all()
    menu = {}
    for item in menu_items:
        if item.category not in menu:
            menu[item.category] = []
        menu[item.category].append({
            'id': item.id,
            'name': item.name,
            'price': item.price,
            'description': item.description
        })
    return render_template('index.html', menu=menu)

@app.route('/menu')
def get_menu():
    menu_items = MenuItem.query.filter_by(available=True).all()
    menu = {}
    for item in menu_items:
        if item.category not in menu:
            menu[item.category] = []
        menu[item.category].append({
            'id': item.id,
            'name': item.name,
            'price': item.price,
            'description': item.description
        })
    return jsonify(menu)

@app.route('/order', methods=['POST'])
@login_required
def place_order():
    data = request.get_json()
    order = Order(
        user_id=current_user.id,
        total_amount=0,
        status='pending',
        timestamp=datetime.utcnow()
    )
    db.session.add(order)
    
    total_amount = 0
    for item_id, details in list(data.items()):
        menu_item = MenuItem.query.get(int(item_id))
        if menu_item and menu_item.available:
            order_item = OrderItem(
                order_id=order.id,
                menu_item_id=menu_item.id,
                quantity=details['quantity'],
                price_at_time=menu_item.price
            )
            total_amount += menu_item.price * details['quantity']
            db.session.add(order_item)
    
    order.total_amount = total_amount
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Order placed successfully!'})

@app.route('/my-orders')
@login_required
def my_orders():
    orders = Order.query.filter_by(user_id=current_user.id).all()
    return render_template('my_orders.html', orders=orders)

def init_db():
    with app.app_context():
        db.create_all()
        # Create admin user if it doesn't exist
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', email='admin@example.com', is_admin=True)
            admin.set_password('admin123')  # Change this password in production
            db.session.add(admin)
            db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5001)
