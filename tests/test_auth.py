import pytest
from flask import url_for
from app.models import User
from app import db

@pytest.fixture
def test_user(app):
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        yield user
        # Cleanup
        db.session.delete(user)
        db.session.commit()

def test_login_page(client):
    """Test that login page loads correctly"""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Sign In' in response.data

def test_successful_login(client, test_user):
    """Test successful login with correct credentials"""
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'password123',
        'remember_me': False
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Welcome' in response.data  # Assuming there's a welcome message on the menu page

def test_failed_login_wrong_password(client, test_user):
    """Test login failure with wrong password"""
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'wrongpassword',
        'remember_me': False
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid username or password' in response.data

def test_failed_login_wrong_username(client):
    """Test login failure with non-existent username"""
    response = client.post('/login', data={
        'username': 'nonexistentuser',
        'password': 'password123',
        'remember_me': False
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid username or password' in response.data

def test_logout(client, test_user):
    """Test logout functionality"""
    # First login
    client.post('/login', data={
        'username': 'testuser',
        'password': 'password123',
        'remember_me': False
    })
    # Then logout
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Sign In' in response.data  # Should be redirected to login page

def test_register_page(client):
    """Test that registration page loads correctly"""
    response = client.get('/register')
    assert response.status_code == 200
    assert b'Register' in response.data

def test_successful_registration(client, app):
    """Test successful user registration"""
    response = client.post('/register', data={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'newpassword123',
        'password2': 'newpassword123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Congratulations' in response.data
    
    # Verify user was created in database
    with app.app_context():
        user = User.query.filter_by(username='newuser').first()
        assert user is not None
        assert user.email == 'newuser@example.com'
        # Cleanup
        db.session.delete(user)
        db.session.commit()

def test_registration_existing_username(client, test_user):
    """Test registration with existing username"""
    response = client.post('/register', data={
        'username': 'testuser',  # Same username as test_user
        'email': 'different@example.com',
        'password': 'password123',
        'password2': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Please use a different username' in response.data

def test_registration_existing_email(client, test_user):
    """Test registration with existing email"""
    response = client.post('/register', data={
        'username': 'differentuser',
        'email': 'test@example.com',  # Same email as test_user
        'password': 'password123',
        'password2': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Please use a different email address' in response.data

def test_registration_mismatched_passwords(client):
    """Test registration with mismatched passwords"""
    response = client.post('/register', data={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'password123',
        'password2': 'differentpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Field must be equal to password' in response.data

def test_authenticated_user_redirect(client, test_user):
    """Test that authenticated users are redirected from login/register pages"""
    # Login first
    client.post('/login', data={
        'username': 'testuser',
        'password': 'password123',
        'remember_me': False
    })
    
    # Try to access login page
    response = client.get('/login', follow_redirects=True)
    assert response.status_code == 200
    assert b'Sign In' not in response.data  # Should be redirected to menu
    
    # Try to access register page
    response = client.get('/register', follow_redirects=True)
    assert response.status_code == 200
    assert b'Register' not in response.data  # Should be redirected to menu
