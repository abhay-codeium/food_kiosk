from app import app, db
from models import MenuItem

def init_menu():
    with app.app_context():
        # Clear existing menu items
        MenuItem.query.delete()
        
        # Menu items
        menu_items = [
            # Burgers
            MenuItem(
                name='Classic Burger',
                price=8.99,
                category='burgers',
                description='Juicy beef patty with lettuce, tomato, onion, and our special sauce',
                available=True
            ),
            MenuItem(
                name='Cheeseburger',
                price=9.99,
                category='burgers',
                description='Classic burger topped with melted cheddar cheese',
                available=True
            ),
            MenuItem(
                name='Bacon Burger',
                price=10.99,
                category='burgers',
                description='Classic burger with crispy bacon strips',
                available=True
            ),
            MenuItem(
                name='Veggie Burger',
                price=8.99,
                category='burgers',
                description='Plant-based patty with fresh vegetables',
                available=True
            ),
            
            # Sides
            MenuItem(
                name='French Fries',
                price=3.99,
                category='sides',
                description='Crispy golden fries with sea salt',
                available=True
            ),
            MenuItem(
                name='Onion Rings',
                price=4.99,
                category='sides',
                description='Crispy battered onion rings',
                available=True
            ),
            MenuItem(
                name='Caesar Salad',
                price=5.99,
                category='sides',
                description='Fresh romaine lettuce with caesar dressing and croutons',
                available=True
            ),
            MenuItem(
                name='Coleslaw',
                price=2.99,
                category='sides',
                description='Fresh cabbage and carrots in creamy dressing',
                available=True
            ),
            
            # Drinks
            MenuItem(
                name='Cola',
                price=1.99,
                category='drinks',
                description='Classic cola with ice',
                available=True
            ),
            MenuItem(
                name='Lemonade',
                price=2.49,
                category='drinks',
                description='Fresh squeezed lemonade',
                available=True
            ),
            MenuItem(
                name='Iced Tea',
                price=1.99,
                category='drinks',
                description='Fresh brewed iced tea',
                available=True
            ),
            MenuItem(
                name='Water',
                price=1.00,
                category='drinks',
                description='Bottled water',
                available=True
            ),
            
            # Desserts
            MenuItem(
                name='Chocolate Shake',
                price=4.99,
                category='desserts',
                description='Rich chocolate milkshake with whipped cream',
                available=True
            ),
            MenuItem(
                name='Apple Pie',
                price=3.99,
                category='desserts',
                description='Warm apple pie with cinnamon',
                available=True
            ),
            MenuItem(
                name='Ice Cream Sundae',
                price=4.99,
                category='desserts',
                description='Vanilla ice cream with chocolate sauce and nuts',
                available=True
            )
        ]
        
        # Add all menu items
        for item in menu_items:
            db.session.add(item)
        
        # Commit changes
        db.session.commit()
        print("Menu initialized successfully!")

if __name__ == '__main__':
    init_menu()
