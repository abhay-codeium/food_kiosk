let orderItems = {};
let currentOrder = {
    items: {},
    total: 0
};

function formatPrice(price) {
    return '$' + price.toFixed(2);
}

function updateOrderSummary() {
    const orderItemsDiv = document.getElementById('order-items');
    orderItemsDiv.innerHTML = '';
    let total = 0;

    if (Object.keys(currentOrder.items).length === 0) {
        orderItemsDiv.innerHTML = `
            <div class="empty-order">
                <p>Your order is empty</p>
                <p>Add items from the menu to get started</p>
            </div>
        `;
    } else {
        Object.entries(currentOrder.items).forEach(([itemId, item]) => {
            const itemDiv = document.createElement('div');
            itemDiv.className = 'order-item';
            const itemTotal = item.price * item.quantity;
            total += itemTotal;

            itemDiv.innerHTML = `
                <div class="order-item-details">
                    <span class="order-item-name">${item.name}</span>
                    <span class="order-item-price">${formatPrice(itemTotal)}</span>
                </div>
                <div class="order-item-controls">
                    <button onclick="updateQuantity(${itemId}, ${item.quantity - 1})">-</button>
                    <span class="order-item-quantity">${item.quantity}</span>
                    <button onclick="updateQuantity(${itemId}, ${item.quantity + 1})">+</button>
                </div>
            `;
            orderItemsDiv.appendChild(itemDiv);
        });
    }

    document.getElementById('total-amount').textContent = formatPrice(total);
    currentOrder.total = total;

    // Show/hide order button based on whether there are items in the order
    const orderButton = document.getElementById('place-order');
    if (orderButton) {
        orderButton.style.display = Object.keys(currentOrder.items).length > 0 ? 'block' : 'none';
    }
}

function updateQuantity(itemId, newQuantity) {
    if (newQuantity <= 0) {
        delete currentOrder.items[itemId];
    } else {
        currentOrder.items[itemId].quantity = newQuantity;
    }
    updateOrderSummary();
}

function addToOrder(itemId, name, price) {
    if (currentOrder.items[itemId]) {
        currentOrder.items[itemId].quantity += 1;
    } else {
        currentOrder.items[itemId] = {
            name: name,
            price: price,
            quantity: 1
        };
    }
    updateOrderSummary();
    
    // Show success message
    showNotification(`Added ${name} to your order!`);
}

function showNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;
    document.body.appendChild(notification);

    // Remove notification after 3 seconds
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    // Show first category by default
    const firstTab = document.querySelector('.category-tab');
    if (firstTab) {
        firstTab.classList.add('active');
        const firstCategory = firstTab.dataset.category;
        showCategory(firstCategory);
    }

    // Add click handlers to category tabs
    document.querySelectorAll('.category-tab').forEach(tab => {
        tab.addEventListener('click', function() {
            document.querySelectorAll('.category-tab').forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            showCategory(this.dataset.category);
        });
    });

    // Initialize order summary
    updateOrderSummary();

    // Add event listener for place order button
    const orderButton = document.getElementById('place-order');
    if (orderButton) {
        orderButton.addEventListener('click', function() {
            if (Object.keys(currentOrder.items).length === 0) {
                showNotification('Please add items to your order first.');
                return;
            }

            fetch('/order', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(currentOrder.items)
            })
            .then(response => response.json())
            .then(data => {
                showNotification(data.message);
                // Clear the order after successful placement
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

function showCategory(category) {
    document.querySelectorAll('.menu-category').forEach(cat => {
        cat.style.display = cat.id === category ? 'block' : 'none';
    });
}
