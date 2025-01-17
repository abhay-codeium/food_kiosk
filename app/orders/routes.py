from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from app.models import Order, OrderItem, MenuItem
from app import db
from datetime import datetime

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/place_order', methods=['POST'])
@login_required
def place_order():
    if not request.is_json:
        return jsonify({'error': 'Invalid request format'}), 400

    data = request.get_json()
    item_id = data.get('item_id')
    quantity = data.get('quantity', 1)

    if not item_id:
        return jsonify({'error': 'Missing item_id'}), 400

    menu_item = db.session.get(MenuItem, int(item_id))
    if not menu_item:
        return jsonify({'error': 'Item not found'}), 404

    if not menu_item.available:
        return jsonify({'error': 'Item not available'}), 400

    order = Order(
        user_id=current_user.id,
        total_amount=menu_item.price * quantity,
        status='pending',
        timestamp=datetime.utcnow()
    )
    db.session.add(order)
    db.session.commit()  # Commit to get the order ID
    
    order_item = OrderItem(
        order_id=order.id,
        menu_item_id=menu_item.id,
        quantity=quantity,
        price_at_time=menu_item.price
    )
    db.session.add(order_item)
    db.session.commit()

    return jsonify({'status': 'success', 'message': 'Order placed successfully!'})

@orders_bp.route('/my-orders')
@login_required
def my_orders():
    orders = Order.query.filter_by(user_id=current_user.id).all()
    return render_template('orders/my_orders.html', orders=orders)
