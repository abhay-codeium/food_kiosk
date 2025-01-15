from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import Order, MenuItem
from app import db
from functools import wraps

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Access denied: Admin privileges required')
            return redirect(url_for('menu.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/admin')
@admin_required
def admin_dashboard():
    orders = Order.query.all()
    menu_items = MenuItem.query.all()
    return render_template('admin/dashboard.html', orders=orders, menu_items=menu_items)

@admin_bp.route('/admin/menu/add', methods=['POST'])
@admin_required
def add_menu_item():
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

@admin_bp.route('/admin/menu/update/<int:item_id>', methods=['PUT'])
@admin_required
def update_menu_item(item_id):
    item = MenuItem.query.get_or_404(item_id)
    data = request.get_json()
    item.name = data.get('name', item.name)
    item.price = data.get('price', item.price)
    item.category = data.get('category', item.category)
    item.description = data.get('description', item.description)
    item.available = data.get('available', item.available)
    db.session.commit()
    return jsonify({'message': 'Menu item updated successfully'})

@admin_bp.route('/admin/order/<int:order_id>/status', methods=['PUT'])
@admin_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    data = request.get_json()
    order.status = data['status']
    db.session.commit()
    return jsonify({'message': 'Order status updated successfully'})
