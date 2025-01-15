import pytest
from app.auth.forms import LoginForm, RegistrationForm
from app.models import User
from wtforms.validators import ValidationError

def test_valid_login_form(app):
    with app.test_request_context():
        form = LoginForm(formdata=None)
        form.username.data = 'testuser'
        form.password.data = 'password123'
        assert form.validate() == True

def test_invalid_login_form_empty_fields(app):
    with app.test_request_context():
        form = LoginForm(formdata=None)
        assert form.validate() == False
        assert 'This field is required.' in form.username.errors
        assert 'This field is required.' in form.password.errors

def test_valid_registration_form(app):
    with app.test_request_context():
        form = RegistrationForm(formdata=None)
        form.username.data = 'newuser'
        form.email.data = 'newuser@example.com'
        form.password.data = 'password123'
        form.password2.data = 'password123'
        assert form.validate() == True

def test_invalid_registration_form_empty_fields(app):
    with app.test_request_context():
        form = RegistrationForm(formdata=None)
        assert form.validate() == False
        assert 'This field is required.' in form.username.errors
        assert 'This field is required.' in form.email.errors
        assert 'This field is required.' in form.password.errors
        assert 'This field is required.' in form.password2.errors

def test_invalid_registration_form_passwords_dont_match(app):
    with app.test_request_context():
        form = RegistrationForm(formdata=None)
        form.username.data = 'newuser'
        form.email.data = 'newuser@example.com'
        form.password.data = 'password123'
        form.password2.data = 'differentpassword'
        assert form.validate() == False
        assert 'Field must be equal to password.' in form.password2.errors

def test_invalid_registration_form_invalid_email(app):
    with app.test_request_context():
        form = RegistrationForm(formdata=None)
        form.username.data = 'newuser'
        form.email.data = 'invalid-email'
        form.password.data = 'password123'
        form.password2.data = 'password123'
        assert form.validate() == False
        assert 'Invalid email address.' in form.email.errors

def test_validate_username_unique(app):
    with app.app_context():
        # Create a user first
        user = User(username='existinguser', email='existing@example.com')
        app.db.session.add(user)
        app.db.session.commit()

        # Try to register with the same username
        form = RegistrationForm(formdata=None)
        form.username.data = 'existinguser'
        form.email.data = 'new@example.com'
        form.password.data = 'password123'
        form.password2.data = 'password123'
        
        with pytest.raises(ValidationError) as excinfo:
            form.validate_username(form.username)
        assert 'Please use a different username.' in str(excinfo.value)

def test_validate_email_unique(app):
    with app.app_context():
        # Create a user first
        user = User(username='testuser', email='existing@example.com')
        app.db.session.add(user)
        app.db.session.commit()

        # Try to register with the same email
        form = RegistrationForm(formdata=None)
        form.username.data = 'newuser'
        form.email.data = 'existing@example.com'
        form.password.data = 'password123'
        form.password2.data = 'password123'
        
        with pytest.raises(ValidationError) as excinfo:
            form.validate_email(form.email)
        assert 'Please use a different email address.' in str(excinfo.value)
