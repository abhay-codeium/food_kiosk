import pytest
from app import create_app
from app.extensions import db
from app.models import User, MenuItem
from config import TestConfig

@pytest.fixture
def app():
    app = create_app(TestConfig)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def test_user(app):
    with app.app_context():
        user = User(username='test_user', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return user.id

@pytest.fixture
def admin_user(app):
    with app.app_context():
        user = User(username='admin_test', email='admin@test.com')
        user.set_password('password123')
        user.is_admin = True
        db.session.add(user)
        db.session.commit()
        return user.id

@pytest.fixture
def menu_items(app):
    with app.app_context():
        items = [
            MenuItem(name='Burger', price=10.99, category='Main', description='Delicious burger', available=True),
            MenuItem(name='Fries', price=4.99, category='Sides', description='Crispy fries', available=True),
            MenuItem(name='Unavailable Item', price=5.99, category='Test', description='Test item', available=False)
        ]
        for item in items:
            db.session.add(item)
        db.session.commit()
        return [item.id for item in items]

@pytest.fixture(autouse=True)
def cleanup(app):
    yield
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.create_all()
