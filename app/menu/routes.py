from flask import Blueprint, render_template, jsonify
from app.models import MenuItem

menu_bp = Blueprint('menu', __name__)

@menu_bp.route('/')
def index():
    menu_items = MenuItem.query.filter_by(available=True).all()
    menu = {}
    for item in menu_items:
        if item.category not in menu:
            menu[item.category] = []
        menu[item.category].append({
            'id': item.id,
            'name': item.name,
            'price': item.price,
            'description': item.description
        })
    return render_template('menu/index.html', menu=menu)
