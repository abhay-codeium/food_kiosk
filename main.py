#!/usr/bin/env python
"""
Simple food kiosk application for Python 2/3 migration testing.

This is a verification test to demonstrate repo access, linting, and PR creation.
"""


def greet_customer(name="Customer"):
    """Greet a customer at the food kiosk."""
    return "Welcome to the Food Kiosk, {}!".format(name)


def calculate_total(items):
    """Calculate total price for food items."""
    total = 0
    for item in items:
        total += item.get('price', 0)
    return total


if __name__ == "__main__":
    print(greet_customer("Alice"))

    sample_items = [
        {'name': 'Burger', 'price': 8.99},
        {'name': 'Fries', 'price': 3.49},
        {'name': 'Drink', 'price': 2.99}
    ]

    total = calculate_total(sample_items)
    print("Total: ${:.2f}".format(total))
