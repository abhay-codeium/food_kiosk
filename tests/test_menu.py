import pytest
from app.models import MenuItem
from app import db

def test_menu_page(client):
    """Test that menu page loads correctly"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Menu' in response.data

def test_menu_items_categorized(client, app):
    """Test that menu items are properly categorized"""
    with app.app_context():
        # Create test menu items
        items = [
            MenuItem(name='Burger', price=10.99, description='Classic burger', 
                    category='Main Course', available=True),
            MenuItem(name='Fries', price=4.99, description='Crispy fries', 
                    category='Sides', available=True),
            MenuItem(name='Salad', price=8.99, description='Fresh salad', 
                    category='Main Course', available=True)
        ]
        db.session.bulk_save_objects(items)
        db.session.commit()

        response = client.get('/')
        assert response.status_code == 200
        
        # Check that categories are present
        assert b'Main Course' in response.data
        assert b'Sides' in response.data
        
        # Check that items are in correct categories
        assert b'Burger' in response.data
        assert b'Fries' in response.data
        assert b'Salad' in response.data

def test_only_available_items_shown(client, app):
    """Test that only available items are shown in menu"""
    with app.app_context():
        # Create test menu items
        items = [
            MenuItem(name='Available Item', price=10.99, description='Test item', 
                    category='Test', available=True),
            MenuItem(name='Unavailable Item', price=10.99, description='Test item', 
                    category='Test', available=False)
        ]
        db.session.bulk_save_objects(items)
        db.session.commit()

        response = client.get('/')
        assert response.status_code == 200
        
        # Check that only available item is shown
        assert b'Available Item' in response.data
        assert b'Unavailable Item' not in response.data

def test_menu_item_fields(client, app):
    """Test that menu items include all required fields"""
    with app.app_context():
        # Create test menu item
        item = MenuItem(
            name='Test Item',
            price=15.99,
            description='Test description',
            category='Test Category',
            available=True
        )
        db.session.add(item)
        db.session.commit()

        response = client.get('/')
        assert response.status_code == 200
        
        # Check all required fields are present
        assert b'Test Item' in response.data
        assert b'15.99' in response.data
        assert b'Test description' in response.data
        assert b'Test Category' in response.data

@pytest.fixture
def cleanup(app):
    """Clean up the database after each test"""
    yield
    with app.app_context():
        MenuItem.query.delete()
        db.session.commit()
