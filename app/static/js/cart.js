function displayCart(cart) {
    const cartContainer = document.getElementById('cart-items');
    const totalElement = document.getElementById('cart-total');
    
    if (!cart || !cart.items || cart.items.length === 0) {
        cartContainer.innerHTML = '<p class="text-center">Your cart is empty</p>';
        totalElement.textContent = '$0.00';
        return;
    }
    
    let total = 0;
    cartContainer.innerHTML = cart.items.map(item => {
        total += item.price * item.quantity;
        return `
            <div class="card mb-3">
                <div class="row g-0">
                    <div class="col-md-2">
                        <img src="/static/images/${item.name}.png" 
                             class="img-fluid rounded" 
                             alt="${item.name}"
                             style="height: 100px; object-fit: cover;"
                             onerror="this.src='/static/images/default-product.png'">
                    </div>
                    <div class="col-md-8">
                        <div class="card-body">
                            <h5 class="card-title">${item.name}</h5>
                            <p class="card-text">Price: $${item.price}</p>
                            <div class="input-group" style="width: 150px;">
                                <button class="btn btn-outline-secondary" type="button" onclick="updateQuantity('${item.product_id}', ${item.quantity - 1})">-</button>
                                <input type="number" class="form-control text-center" value="${item.quantity}" min="1" max="${item.stock}" onchange="updateQuantity('${item.product_id}', this.value)">
                                <button class="btn btn-outline-secondary" type="button" onclick="updateQuantity('${item.product_id}', ${item.quantity + 1})">+</button>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-2 d-flex align-items-center justify-content-end">
                        <button class="btn btn-danger" onclick="removeFromCart('${item.product_id}')">Remove</button>
                    </div>
                </div>
            </div>
        `;
    }).join('');
    
    totalElement.textContent = `$${total.toFixed(2)}`;
} 