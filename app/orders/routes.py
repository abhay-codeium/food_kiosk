from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from app.models import Order, OrderItem, MenuItem
from app import db
from datetime import datetime

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/order', methods=['POST'])
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
    db.session.commit()  # Commit to get the order ID
    
    total_amount = 0
    for item_id, details in data.items():
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

@orders_bp.route('/my-orders')
@login_required
def my_orders():
    orders = Order.query.filter_by(user_id=current_user.id).all()
    return render_template('orders/my_orders.html', orders=orders)
