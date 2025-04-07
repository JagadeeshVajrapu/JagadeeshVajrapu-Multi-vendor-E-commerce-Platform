// Global variables
let currentUser = null;
const API_BASE_URL = '/api';

// DOM Elements
const authButtons = document.getElementById('auth-buttons');
const userMenu = document.getElementById('user-menu');
const userEmail = document.getElementById('user-email');
const vendorDashboardLink = document.getElementById('vendor-dashboard-link');
const productsContainer = document.getElementById('products-container');
const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');

// Check authentication status on page load
document.addEventListener('DOMContentLoaded', () => {
    console.log('Page loaded, checking auth status...');
    checkAuthStatus();
    updateCartCount();
    setupFormHandlers();
});

// Setup form handlers
function setupFormHandlers() {
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }
}

// Authentication Functions
function checkAuthStatus() {
    console.log('Checking auth status...');
    const token = localStorage.getItem('token');
    if (token) {
        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            const expirationTime = payload.exp * 1000; // Convert to milliseconds
            const currentTime = Date.now();
            
            if (currentTime > expirationTime) {
                console.log('Token expired');
                localStorage.removeItem('token');
                updateUIForLoggedOutUser();
                return;
            }
            
            currentUser = {
                email: payload.sub,
                role: payload.role
            };
            console.log('User authenticated:', currentUser);
            updateUIForLoggedInUser();
            updateCartCount();
        } catch (error) {
            console.error('Invalid token:', error);
            localStorage.removeItem('token');
            updateUIForLoggedOutUser();
        }
    } else {
        console.log('No token found');
        updateUIForLoggedOutUser();
    }
}

function updateUIForLoggedInUser() {
    if (authButtons) authButtons.style.display = 'none';
    if (userMenu) userMenu.style.display = 'block';
    if (userEmail) userEmail.textContent = currentUser.email;
    
    if (currentUser.role === 'vendor' && vendorDashboardLink) {
        vendorDashboardLink.style.display = 'block';
    }
}

function updateUIForLoggedOutUser() {
    if (authButtons) authButtons.style.display = 'block';
    if (userMenu) userMenu.style.display = 'none';
    if (vendorDashboardLink) vendorDashboardLink.style.display = 'none';
}

// Modal Functions
function showLoginModal() {
    const modal = new bootstrap.Modal(document.getElementById('loginModal'));
    modal.show();
}

function showRegisterModal() {
    const modal = new bootstrap.Modal(document.getElementById('registerModal'));
    modal.show();
}

// Form Handlers
async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('loginEmail')?.value;
    const password = document.getElementById('loginPassword')?.value;
    
    if (!email || !password) {
        showErrorMessage('Please fill in all fields');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            localStorage.setItem('token', data.access_token);
            currentUser = {
                email: data.email,
                role: data.role
            };
            updateUIForLoggedInUser();
            showSuccessMessage('Login successful!');
            updateCartCount();
            
            // Close the login modal
            const loginModal = bootstrap.Modal.getInstance(document.getElementById('loginModal'));
            if (loginModal) {
                loginModal.hide();
            }
        } else {
            showErrorMessage(data.error || 'Login failed');
        }
    } catch (error) {
        console.error('Login error:', error);
        showErrorMessage('An error occurred during login');
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const email = document.getElementById('registerEmail')?.value;
    const password = document.getElementById('registerPassword')?.value;
    const role = document.getElementById('registerRole')?.value;
    
    if (!email || !password || !role) {
        showErrorMessage('Please fill in all fields');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password, role })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showSuccessMessage('Registration successful! Please login.');
            if (registerForm) registerForm.reset();
        } else {
            showErrorMessage(data.error || 'Registration failed');
        }
    } catch (error) {
        console.error('Registration error:', error);
        showErrorMessage('An error occurred during registration');
    }
}

// Product Functions
async function loadProducts() {
    try {
        const response = await fetch('/api/products');
        if (!response.ok) {
            throw new Error('Failed to load products');
        }
        const products = await response.json();
        console.log('Loaded products:', products); // Debug log
        displayProducts(products);
    } catch (error) {
        console.error('Error loading products:', error);
        document.getElementById('products-container').innerHTML = 
            '<div class="alert alert-danger">Error loading products. Please try again later.</div>';
    }
}

function displayProducts(products) {
    const productsContainer = document.getElementById('products-container');
    console.log('Displaying products:', products); // Debug log
    
    if (!products || products.length === 0) {
        productsContainer.innerHTML = '<div class="col-12"><p class="text-center">No products available</p></div>';
        return;
    }

    // Create a data URL for a simple placeholder image
    const placeholderImage = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgZmlsbD0iI2VlZSIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTQiIGZpbGw9IiM5OTkiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj5ObyBJbWFnZTwvdGV4dD48L3N2Zz4=';

    productsContainer.innerHTML = products.map(product => {
        console.log(`Product ${product.name} images:`, product.images); // Debug log
        
        // Get the first image URL or use placeholder
        let imageUrl = placeholderImage;
        if (product.images && product.images.length > 0) {
            imageUrl = product.images[0];
            // If the image URL is relative, prepend the base URL
            if (!imageUrl.startsWith('http') && !imageUrl.startsWith('/')) {
                imageUrl = `/static/images/${imageUrl}`;
            }
            // Ensure the image URL is properly encoded
            imageUrl = imageUrl.replace(/ /g, '%20');
        }
        
        console.log(`Using image URL for ${product.name}:`, imageUrl); // Debug log
        
        return `
            <div class="col-md-4 col-sm-6 mb-4">
                <div class="card product-card fade-in h-100">
                    <img src="${imageUrl}" 
                         class="card-img-top" 
                         alt="${product.name}"
                         style="height: 200px; object-fit: cover;"
                         onerror="this.onerror=null; this.src='${placeholderImage}';">
                    <div class="card-body d-flex flex-column">
                        <h5 class="card-title">${product.name}</h5>
                        <p class="card-text">${product.description}</p>
                        <p class="card-text"><strong>Price: $${product.price.toFixed(2)}</strong></p>
                        <p class="card-text">Stock: ${product.stock}</p>
                        <div class="mt-auto">
                            <button class="btn btn-primary" onclick="addToCart('${product._id}')">Add to Cart</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

// Cart Functions
function updateCartCount() {
    const token = localStorage.getItem('token');
    if (!token) {
        console.log('No token found, skipping cart update');
        return;
    }

    fetch(`${API_BASE_URL}/cart/`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Accept': 'application/json'
        }
    })
    .then(response => {
        if (response.status === 401) {
            // Token expired or invalid
            localStorage.removeItem('token');
            updateUIForLoggedOutUser();
            return;
        }
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.error || 'Failed to fetch cart');
            });
        }
        return response.json();
    })
    .then(data => {
        const cartBadge = document.querySelector('.cart-badge');
        if (cartBadge) {
            const itemCount = data.items ? data.items.length : 0;
            cartBadge.textContent = itemCount;
            cartBadge.style.display = itemCount > 0 ? 'inline' : 'none';
        }
    })
    .catch(error => {
        console.error('Error updating cart count:', error);
        showErrorMessage(error.message || 'Error updating cart count');
    });
}

function addToCart(productId) {
    const token = localStorage.getItem('token');
    if (!token) {
        showErrorMessage('Please login to add items to cart');
        window.location.href = '/auth/login';
        return;
    }

    // Validate productId format
    if (!productId || typeof productId !== 'string' || productId.length !== 24) {
        showErrorMessage('Invalid product ID format');
        return;
    }

    console.log('Adding to cart:', { productId, token: token.substring(0, 10) + '...' });

    fetch(`${API_BASE_URL}/cart/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
            'Accept': 'application/json'
        },
        body: JSON.stringify({ product_id: productId, quantity: 1 })
    })
    .then(response => {
        console.log('Cart response status:', response.status);
        if (response.status === 401) {
            // Token expired or invalid
            localStorage.removeItem('token');
            showErrorMessage('Session expired. Please login again.');
            window.location.href = '/auth/login';
            return;
        }
        if (!response.ok) {
            return response.json().then(data => {
                console.error('Cart error response:', data);
                throw new Error(data.error || 'Failed to add item to cart');
            });
        }
        return response.json();
    })
    .then(data => {
        console.log('Cart update successful:', data);
        showSuccessMessage('Item added to cart successfully!');
        updateCartCount();
    })
    .catch(error => {
        console.error('Error adding to cart:', error);
        showErrorMessage(error.message || 'Error adding item to cart');
    });
}

// Event Listeners
document.addEventListener('click', (e) => {
    if (e.target && e.target.classList.contains('add-to-cart')) {
        const productId = e.target.dataset.productId;
        if (productId) {
            addToCart(productId);
        }
    }
});

// Utility Functions
function showSuccessMessage(message) {
    // Create and show a success message
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-success alert-dismissible fade show';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.insertBefore(alertDiv, document.body.firstChild);
    setTimeout(() => alertDiv.remove(), 3000);
}

function showErrorMessage(message) {
    // Create and show an error message
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-danger alert-dismissible fade show';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.insertBefore(alertDiv, document.body.firstChild);
    setTimeout(() => alertDiv.remove(), 3000);
}

// Logout Function
function logout() {
    localStorage.removeItem('token');
    currentUser = null;
    authButtons.style.display = 'block';
    userMenu.style.display = 'none';
    vendorDashboardLink.style.display = 'none';
    window.location.href = '/';
} 