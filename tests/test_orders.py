import pytest
from flask import url_for
from app.models import MenuItem, Order, OrderItem, User
from app import db
import json
from datetime import datetime

@pytest.fixture
def test_user(app):
    """Create a test user"""
    with app.app_context():
        user = User(username='test_user', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        user_id = user.id
    return user_id

@pytest.fixture
def menu_items(app):
    """Create test menu items"""
    with app.app_context():
        items = [
            MenuItem(
                name='Burger',
                price=10.99,
                category='Main Course',
                description='Classic burger',
                available=True
            ),
            MenuItem(
                name='Fries',
                price=4.99,
                category='Sides',
                description='Crispy fries',
                available=True
            ),
            MenuItem(
                name='Unavailable Item',
                price=7.99,
                category='Main Course',
                description='Not available',
                available=False
            )
        ]
        db.session.bulk_save_objects(items)
        db.session.commit()
        return [item.id for item in MenuItem.query.all()]

def login_user(client, username, password):
    """Helper function to login a user"""
    return client.post('/login', data={
        'username': username,
        'password': password,
        'remember_me': False
    }, follow_redirects=True)

def test_place_order(client, test_user, menu_items, app):
    """Test placing a valid order"""
    login_user(client, 'test_user', 'password123')
    
    with app.app_context():
        # Get menu items
        burger = MenuItem.query.filter_by(name='Burger').first()
        fries = MenuItem.query.filter_by(name='Fries').first()
        
        order_data = {
            str(burger.id): {'quantity': 2},
            str(fries.id): {'quantity': 1}
        }
        
        response = client.post('/order',
                             data=json.dumps(order_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['message'] == 'Order placed successfully!'
        
        # Verify order in database
        order = Order.query.first()
        assert order is not None
        assert order.user_id == test_user
        assert order.status == 'pending'
        assert order.total_amount == (burger.price * 2 + fries.price)
        
        # Verify order items
        order_items = OrderItem.query.filter_by(order_id=order.id).all()
        assert len(order_items) == 2

def test_place_order_with_unavailable_item(client, test_user, menu_items, app):
    """Test placing an order with an unavailable item"""
    login_user(client, 'test_user', 'password123')
    
    with app.app_context():
        unavailable_item = MenuItem.query.filter_by(name='Unavailable Item').first()
        order_data = {
            str(unavailable_item.id): {'quantity': 1}
        }
        
        response = client.post('/order',
                             data=json.dumps(order_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        
        # Verify no order was created with items
        order = Order.query.first()
        assert order is not None
        assert order.total_amount == 0

def test_place_order_unauthenticated(client, menu_items):
    """Test placing an order without authentication"""
    with client.application.app_context():
        burger = MenuItem.query.filter_by(name='Burger').first()
        order_data = {
            str(burger.id): {'quantity': 1}
        }
        
        response = client.post('/order',
                             data=json.dumps(order_data),
                             content_type='application/json')
        
        assert response.status_code == 302  # Redirect to login
        
        # Verify no order was created
        order = Order.query.first()
        assert order is None

def test_view_my_orders(client, test_user, menu_items, app):
    """Test viewing user's orders"""
    login_user(client, 'test_user', 'password123')
    
    with app.app_context():
        burger = MenuItem.query.filter_by(name='Burger').first()
        
        # Create two orders
        for _ in range(2):
            order = Order(
                user_id=test_user,
                total_amount=burger.price,
                status='pending',
                timestamp=datetime.utcnow()
            )
            db.session.add(order)
            db.session.commit()
            
            order_item = OrderItem(
                order_id=order.id,
                menu_item_id=burger.id,
                quantity=1,
                price_at_time=burger.price
            )
            db.session.add(order_item)
            db.session.commit()
    
    response = client.get('/my-orders')
    assert response.status_code == 200
    assert b'pending' in response.data
    
    # Verify correct number of orders shown
    with app.app_context():
        orders = Order.query.filter_by(user_id=test_user).all()
        assert len(orders) == 2

def test_view_my_orders_unauthenticated(client):
    """Test viewing orders without authentication"""
    response = client.get('/my-orders')
    assert response.status_code == 302  # Redirect to login

def test_place_order_with_invalid_item_id(client, test_user, app):
    """Test placing an order with an invalid item ID"""
    login_user(client, 'test_user', 'password123')
    
    order_data = {
        '999': {'quantity': 1}  # Non-existent item ID
    }
    
    response = client.post('/order',
                          data=json.dumps(order_data),
                          content_type='application/json')
    
    assert response.status_code == 200
    
    # Verify no order was created with items
    with app.app_context():
        order = Order.query.first()
        assert order is not None
        assert order.total_amount == 0

@pytest.fixture
def cleanup(app):
    """Clean up the database after each test"""
    yield
    with app.app_context():
        OrderItem.query.delete()
        Order.query.delete()
        MenuItem.query.delete()
        User.query.filter_by(username='test_user').delete()
        db.session.commit()
