from app import create_app, db
from app.models import User, MenuItem

def init_db():
    app = create_app()
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Create admin user if it doesn't exist
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', email='admin@example.com', is_admin=True)
            admin.set_password('admin123')
            db.session.add(admin)
        
        # Add sample menu items
        menu_items = [
            {
                'name': 'Classic Burger',
                'price': 8.99,
                'category': 'Burgers',
                'description': 'Juicy beef patty with lettuce, tomato, and special sauce'
            },
            {
                'name': 'Cheeseburger',
                'price': 9.99,
                'category': 'Burgers',
                'description': 'Classic burger with melted cheddar cheese'
            },
            {
                'name': 'French Fries',
                'price': 3.99,
                'category': 'Sides',
                'description': 'Crispy golden fries with sea salt'
            },
            {
                'name': 'Onion Rings',
                'price': 4.99,
                'category': 'Sides',
                'description': 'Crispy battered onion rings'
            },
            {
                'name': 'Cola',
                'price': 2.49,
                'category': 'Drinks',
                'description': 'Ice-cold cola'
            },
            {
                'name': 'Milkshake',
                'price': 4.99,
                'category': 'Drinks',
                'description': 'Creamy vanilla milkshake'
            }
        ]
        
        # Add menu items if they don't exist
        for item_data in menu_items:
            if not MenuItem.query.filter_by(name=item_data['name']).first():
                item = MenuItem(**item_data)
                db.session.add(item)
        
        db.session.commit()
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()
