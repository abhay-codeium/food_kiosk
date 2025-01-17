import pytest
from app import create_app, db, login_manager
from app.models import User
from config import Config
from flask import current_app

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = 'test-secret-key'

def test_create_app():
    """Test application factory."""
    app = create_app(TestConfig)
    
    assert app.config['TESTING'] == True
    assert app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///:memory:'
    assert app.config['SECRET_KEY'] == 'test-secret-key'

def test_blueprints_registered():
    """Test that all blueprints are registered."""
    app = create_app(TestConfig)
    
    # Check if all blueprints are registered
    assert 'auth' in app.blueprints
    assert 'menu' in app.blueprints
    assert 'orders' in app.blueprints
    assert 'admin' in app.blueprints

def test_extensions_initialized():
    """Test that Flask extensions are properly initialized."""
    app = create_app(TestConfig)
    
    with app.app_context():
        # Test SQLAlchemy initialization
        assert current_app == app
        assert db.engine is not None
        
        # Test Login Manager initialization
        assert login_manager.login_view == 'auth.login'

def test_database_created():
    """Test that database tables are created."""
    app = create_app(TestConfig)
    
    with app.app_context():
        # Check if the User table exists and can be queried
        assert User.query.count() is not None

def test_admin_user_creation():
    """Test that admin user is created during initialization."""
    app = create_app(TestConfig)
    
    with app.app_context():
        admin = User.query.filter_by(username='admin').first()
        assert admin is not None
        assert admin.username == 'admin'
        assert admin.email == 'admin@example.com'
        assert admin.is_admin == True
        assert admin.check_password('admin') == True

def test_user_loader():
    """Test the user loader function."""
    app = create_app(TestConfig)
    
    with app.app_context():
        # Create a test user
        user = User(username='testuser', email='test@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        
        # Test the user loader
        loaded_user = login_manager.user_callback(user.id)
        assert loaded_user is not None
        assert loaded_user.id == user.id
        assert loaded_user.username == 'testuser'

def test_create_app_test_config():
    """Test application factory with test config."""
    app = create_app(TestConfig)
    
    assert app.config['TESTING'] == True
    assert app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///:memory:'
    assert app.config['SECRET_KEY'] == 'test-secret-key'
