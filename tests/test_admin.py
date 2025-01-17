import pytest
from flask import url_for
from app.models import MenuItem, Order, User
from app import db
import json

@pytest.fixture
def admin_user(app):
    """Create an admin user"""
    with app.app_context():
        admin = User(username='admin_test', email='admin@test.com', is_admin=True)
        admin.set_password('password123')
        db.session.add(admin)
        db.session.commit()
        return admin

@pytest.fixture
def regular_user(app):
    """Create a regular user"""
    with app.app_context():
        user = User(username='user_test', email='user@test.com', is_admin=False)
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return user

def login_user(client, username, password):
    """Helper function to login a user"""
    return client.post('/login', data={
        'username': username,
        'password': password,
        'remember_me': False
    }, follow_redirects=True)

def test_admin_dashboard_access(client, admin_user):
    """Test that admin can access dashboard"""
    login_user(client, 'admin_test', 'password123')
    response = client.get('/admin')
    assert response.status_code == 200
    assert b'Dashboard' in response.data

def test_non_admin_dashboard_access(client, regular_user):
    """Test that non-admin users cannot access dashboard"""
    login_user(client, 'user_test', 'password123')
    response = client.get('/admin')
    assert response.status_code == 302  # Redirect
    assert b'Access denied' in client.get('/').data

def test_unauthenticated_dashboard_access(client):
    """Test that unauthenticated users cannot access dashboard"""
    response = client.get('/admin')
    assert response.status_code == 302  # Redirect to login

def test_add_menu_item(client, admin_user):
    """Test adding a new menu item"""
    login_user(client, 'admin_test', 'password123')
    
    menu_item = {
        'name': 'Test Item',
        'price': 9.99,
        'category': 'Test Category',
        'description': 'Test Description'
    }
    
    response = client.post('/admin/menu/add',
                          data=json.dumps(menu_item),
                          content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'Menu item added successfully'
    
    # Verify item was added to database
    item = MenuItem.query.filter_by(name='Test Item').first()
    assert item is not None
    assert item.price == 9.99
    assert item.category == 'Test Category'
    assert item.description == 'Test Description'
    assert item.available == True

def test_update_menu_item(client, admin_user):
    """Test updating a menu item."""
    login_user(client, 'admin_test', 'password123')
    
    # Create a menu item
    with client.session_transaction() as session:
        item = MenuItem(name='Test Item', description='Test Description',
                       price=10.0, category='Test Category')
        db.session.add(item)
        db.session.commit()
        item_id = item.id

    # Update the item
    response = client.put(f'/admin/menu/update/{item_id}', json={
        'name': 'Updated Item',
        'description': 'Updated Description',
        'price': 15.0,
        'category': 'Updated Category'
    })
    assert response.status_code == 200

    # Verify the update
    updated_item = db.session.get(MenuItem, item_id)
    assert updated_item.name == 'Updated Item'
    assert updated_item.price == 15.0
    assert updated_item.category == 'Updated Category'
    assert updated_item.description == 'Updated Description'

def test_update_nonexistent_menu_item(client, admin_user):
    """Test updating a menu item that doesn't exist"""
    login_user(client, 'admin_test', 'password123')
    
    response = client.put('/admin/menu/update/999',
                         data=json.dumps({'name': 'Test'}),
                         content_type='application/json')
    
    assert response.status_code == 404

def test_non_admin_add_menu_item(client, regular_user):
    """Test that non-admin users cannot add menu items"""
    login_user(client, 'user_test', 'password123')
    
    menu_item = {
        'name': 'Test Item',
        'price': 9.99,
        'category': 'Test Category'
    }
    
    response = client.post('/admin/menu/add',
                          data=json.dumps(menu_item),
                          content_type='application/json')
    
    assert response.status_code == 302  # Redirect
    
    # Verify item was not added
    item = MenuItem.query.filter_by(name='Test Item').first()
    assert item is None

def test_non_admin_update_menu_item(client, regular_user, app):
    """Test that non-admin users cannot update menu items"""
    login_user(client, 'user_test', 'password123')
    
    # Create a menu item
    with app.app_context():
        item = MenuItem(
            name='Test Item',
            price=10.99,
            category='Test Category'
        )
        db.session.add(item)
        db.session.commit()
        item_id = item.id

    update_data = {'name': 'Updated Item'}
    
    response = client.put('/admin/menu/update/%s' % item_id,
                         data=json.dumps(update_data),
                         content_type='application/json')
    
    assert response.status_code == 302  # Redirect
    
    # Verify item was not updated
    item = MenuItem.query.get(item_id)
    assert item.name == 'Test Item'

@pytest.fixture
def cleanup(app):
    """Clean up the database after each test"""
    yield
    with app.app_context():
        MenuItem.query.delete()
        Order.query.delete()
        User.query.filter(User.username.in_(['admin_test', 'user_test'])).delete()
        db.session.commit()
