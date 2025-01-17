from flask import Flask
from config import Config
from app.extensions import db, login_manager
from app.models import User

# Initialize extensions
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(id):
    return db.session.get(User, int(id))

def create_app(config_class=Config):
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config_class)
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    
    # Register blueprints
    from app.auth.routes import auth_bp
    from app.menu.routes import menu_bp
    from app.orders.routes import orders_bp
    from app.admin.routes import admin_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(menu_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(admin_bp)

    # Create database tables
    with app.app_context():
        db.create_all()
        init_admin()

    return app

def init_admin():
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', email='admin@example.com')
        admin.set_password('admin')
        admin.is_admin = True
        db.session.add(admin)
        db.session.commit()
