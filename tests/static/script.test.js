/**
 * @jest-environment jsdom
 */

import {
    formatPrice,
    addToOrder,
    updateQuantity,
    updateOrderSummary,
    showNotification,
    showCategory,
    currentOrder
} from '../../app/static/script.js';

// Mock the fetch function
global.fetch = jest.fn(() =>
    Promise.resolve({
        json: () => Promise.resolve({ message: 'Order placed successfully!' })
    })
);

// Setup document body before each test
beforeEach(() => {
    // Reset current order
    currentOrder.items = {};
    currentOrder.total = 0;

    // Setup DOM
    document.body.innerHTML = `
        <div id="order-items"></div>
        <div id="total-amount"></div>
        <button id="place-order">Place Order</button>
        <div class="category-tabs">
            <div class="category-tab" data-category="main-course">Main Course</div>
            <div class="category-tab" data-category="sides">Sides</div>
        </div>
        <div id="main-course" class="menu-category"></div>
        <div id="sides" class="menu-category"></div>
    `;

    // Initialize event listeners
    const orderButton = document.getElementById('place-order');
    if (orderButton) {
        orderButton.addEventListener('click', function() {
            if (Object.keys(currentOrder.items).length === 0) {
                showNotification('Please add items to your order first.');
                return;
            }

            const orderData = { ...currentOrder.items };  // Create a copy for the request

            fetch('/order', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(orderData)
            })
            .then(response => response.json())
            .then(data => {
                showNotification(data.message);
                currentOrder.items = {};
                updateOrderSummary();
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('There was an error placing your order. Please try again.');
            });
        });
    }
});

// Clear all mocks after each test
afterEach(() => {
    jest.clearAllMocks();
    // Clean up any notifications
    const notifications = document.querySelectorAll('.notification');
    notifications.forEach(n => n.remove());
});

describe('Price Formatting', () => {
    test('formatPrice formats number to currency string', () => {
        expect(formatPrice(10)).toBe('$10.00');
        expect(formatPrice(10.5)).toBe('$10.50');
        expect(formatPrice(0)).toBe('$0.00');
    });
});

describe('Order Management', () => {
    test('addToOrder adds new item to order', () => {
        addToOrder(1, 'Burger', 10.99);
        
        expect(currentOrder.items[1]).toEqual({
            name: 'Burger',
            price: 10.99,
            quantity: 1
        });
    });

    test('addToOrder increments quantity for existing item', () => {
        addToOrder(1, 'Burger', 10.99);
        addToOrder(1, 'Burger', 10.99);
        
        expect(currentOrder.items[1].quantity).toBe(2);
    });

    test('updateQuantity updates item quantity', () => {
        addToOrder(1, 'Burger', 10.99);
        updateQuantity(1, 3);
        
        expect(currentOrder.items[1].quantity).toBe(3);
    });

    test('updateQuantity removes item when quantity is 0', () => {
        addToOrder(1, 'Burger', 10.99);
        updateQuantity(1, 0);
        
        expect(currentOrder.items[1]).toBeUndefined();
    });
});

describe('Order Summary', () => {
    test('updateOrderSummary shows empty order message when no items', () => {
        currentOrder.items = {};
        updateOrderSummary();
        
        const orderItems = document.getElementById('order-items');
        expect(orderItems.innerHTML).toContain('Your order is empty');
    });

    test('updateOrderSummary displays order items and total', () => {
        addToOrder(1, 'Burger', 10.99);
        addToOrder(2, 'Fries', 4.99);
        updateOrderSummary();
        
        const orderItems = document.getElementById('order-items');
        const totalAmount = document.getElementById('total-amount');
        
        expect(orderItems.innerHTML).toContain('Burger');
        expect(orderItems.innerHTML).toContain('Fries');
        expect(totalAmount.textContent).toBe('$15.98');
    });

    test('updateOrderSummary shows/hides order button based on items', () => {
        const orderButton = document.getElementById('place-order');
        
        // Empty order
        currentOrder.items = {};
        updateOrderSummary();
        expect(orderButton.style.display).toBe('none');
        
        // Add item
        addToOrder(1, 'Burger', 10.99);
        expect(orderButton.style.display).toBe('block');
    });
});

describe('Notifications', () => {
    test('showNotification creates and removes notification', () => {
        jest.useFakeTimers();
        
        showNotification('Test message');
        
        const notification = document.querySelector('.notification');
        expect(notification).toBeTruthy();
        expect(notification.textContent).toBe('Test message');
        
        // Fast-forward time
        jest.advanceTimersByTime(3000);
        
        expect(document.querySelector('.notification')).toBeNull();
        
        jest.useRealTimers();
    });
});

describe('Category Management', () => {
    test('showCategory shows selected category and hides others', () => {
        showCategory('main-course');
        
        expect(document.getElementById('main-course').style.display).toBe('block');
        expect(document.getElementById('sides').style.display).toBe('none');
    });
});

describe('Order Placement', () => {
    test('places order successfully', async () => {
        addToOrder(1, 'Burger', 10.99);
        
        const orderButton = document.getElementById('place-order');
        const expectedOrder = { ...currentOrder.items };  // Create a copy before submitting
        
        orderButton.click();
        
        await new Promise(resolve => setTimeout(resolve, 0)); // Wait for promises to resolve
        
        expect(fetch).toHaveBeenCalledWith('/order', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(expectedOrder)
        });
        
        // Wait for the promise chain to complete
        await new Promise(resolve => setTimeout(resolve, 0));
        
        // Check order was cleared
        expect(Object.keys(currentOrder.items)).toHaveLength(0);
    });

    test('prevents empty order submission', async () => {
        currentOrder.items = {};
        const orderButton = document.getElementById('place-order');
        orderButton.click();
        
        // Wait for notification to appear
        await new Promise(resolve => setTimeout(resolve, 0));
        
        expect(fetch).not.toHaveBeenCalled();
        const notification = document.querySelector('.notification');
        expect(notification).toBeTruthy();
        expect(notification.textContent).toBe('Please add items to your order first.');
    });
});
