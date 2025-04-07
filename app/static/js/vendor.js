// Global variables
let currentUser = null;
const API_BASE_URL = '/api';
let productModal = null;

// DOM Elements
const vendorEmail = document.getElementById('vendor-email');
const productsContainer = document.getElementById('products-container');
const productForm = document.getElementById('productForm');

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    checkAuthStatus();
    loadVendorProducts();
    productModal = new bootstrap.Modal(document.getElementById('productModal'));
});

// Authentication Functions
function checkAuthStatus() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = '/';
        return;
    }

    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        if (payload.role !== 'vendor') {
            window.location.href = '/';
            return;
        }
        
        currentUser = {
            email: payload.email,
            role: payload.role
        };
        vendorEmail.textContent = currentUser.email;
    } catch (error) {
        console.error('Invalid token:', error);
        localStorage.removeItem('token');
        window.location.href = '/';
    }
}

// Product Functions
async function loadVendorProducts() {
    try {
        const response = await fetch(`${API_BASE_URL}/products`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to load products');
        }
        
        const products = await response.json();
        displayVendorProducts(products.filter(p => p.vendor_email === currentUser.email));
    } catch (error) {
        console.error('Error loading products:', error);
        showAlert('Error loading products', 'danger');
    }
}

function displayVendorProducts(products) {
    const productsContainer = document.getElementById('vendor-products');
    console.log('Displaying vendor products:', products); // Debug log
    
    if (!products || products.length === 0) {
        productsContainer.innerHTML = '<div class="col-12"><p class="text-center">No products available</p></div>';
        return;
    }

    productsContainer.innerHTML = products.map(product => {
        console.log('Product images:', product.images); // Debug log
        const imageUrl = product.images && product.images.length > 0 
            ? product.images[0] 
            : '/static/images/Premium Wireless Headphones.png';
        console.log('Using image URL:', imageUrl); // Debug log
        
        return `
            <div class="col-md-4 col-sm-6 mb-4">
                <div class="card product-card h-100">
                    <img src="${imageUrl}" 
                         class="card-img-top" 
                         alt="${product.name}"
                         style="height: 200px; object-fit: cover;"
                         onerror="this.onerror=null; this.src='/static/images/Premium Wireless Headphones.png'; console.log('Using default product image');">
                    <div class="card-body d-flex flex-column">
                        <h5 class="card-title">${product.name}</h5>
                        <p class="card-text">${product.description}</p>
                        <p class="card-text"><strong>Price: $${product.price.toFixed(2)}</strong></p>
                        <p class="card-text">Stock: ${product.stock}</p>
                        <div class="mt-auto">
                            <button class="btn btn-primary me-2" onclick="editProduct('${product._id}')">Edit</button>
                            <button class="btn btn-danger" onclick="deleteProduct('${product._id}')">Delete</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function showAddProductModal() {
    productForm.reset();
    document.getElementById('productId').value = '';
    document.getElementById('modalTitle').textContent = 'Add New Product';
    productModal.show();
}

async function editProduct(productId) {
    try {
        const response = await fetch(`${API_BASE_URL}/products/${productId}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to load product');
        }
        
        const product = await response.json();
        
        document.getElementById('productId').value = product._id;
        document.getElementById('productName').value = product.name;
        document.getElementById('productDescription').value = product.description;
        document.getElementById('productPrice').value = product.price;
        document.getElementById('productCategory').value = product.category;
        document.getElementById('productStock').value = product.stock;
        
        // Show current image if exists
        const preview = document.getElementById('imagePreview');
        if (product.images && product.images.length > 0) {
            preview.innerHTML = `<img src="${product.images[0]}" class="img-thumbnail" style="max-height: 200px;">`;
        } else {
            preview.innerHTML = '';
        }
        
        productModal.show();
    } catch (error) {
        console.error('Error:', error);
        showAlert(error.message, 'danger');
    }
}

// Handle image upload
document.getElementById('productImage').addEventListener('change', async function(e) {
    const file = e.target.files[0];
    if (file) {
        try {
            const formData = new FormData();
            formData.append('image', file);
            
            const response = await fetch('/api/products/upload-image', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: formData
            });
            
            if (!response.ok) {
                throw new Error('Failed to upload image');
            }
            
            const data = await response.json();
            console.log('Image uploaded successfully:', data.image_url); // Debug log
            
            // Show preview
            const preview = document.getElementById('imagePreview');
            preview.innerHTML = `
                <img src="${data.image_url}" 
                     class="img-thumbnail" 
                     style="max-height: 200px;"
                     onerror="this.onerror=null; this.src='/static/images/Premium Wireless Headphones.png'; console.log('Using default product image');">
            `;
            
            // Store the image URL
            preview.dataset.imageUrl = data.image_url;
        } catch (error) {
            console.error('Error uploading image:', error);
            alert('Failed to upload image. Please try again.');
        }
    }
});

// Update product form submission
document.getElementById('productForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    try {
        // Get the stored image URL
        const preview = document.getElementById('imagePreview');
        const imageUrl = preview.dataset.imageUrl;
        
        // Prepare product data
        const productData = {
            name: document.getElementById('productName').value,
            description: document.getElementById('productDescription').value,
            price: parseFloat(document.getElementById('productPrice').value),
            category: document.getElementById('productCategory').value,
            stock: parseInt(document.getElementById('productStock').value),
            images: imageUrl ? [imageUrl] : []
        };
        
        console.log('Submitting product data:', productData); // Debug log
        
        const productId = document.getElementById('productId').value;
        const url = productId ? `/api/products/${productId}` : '/api/products';
        const method = productId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify(productData)
        });
        
        if (!response.ok) {
            throw new Error('Failed to save product');
        }
        
        const result = await response.json();
        console.log('Product saved successfully:', result); // Debug log
        
        document.getElementById('productForm').reset();
        document.getElementById('imagePreview').innerHTML = '';
        document.getElementById('imagePreview').dataset.imageUrl = '';
        
        await loadVendorProducts();
        showAlert('Product saved successfully!', 'success');
    } catch (error) {
        console.error('Error:', error);
        showAlert(error.message, 'danger');
    }
});

async function deleteProduct(productId) {
    if (!confirm('Are you sure you want to delete this product?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/products/${productId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to delete product');
        }
        
        loadVendorProducts();
        showAlert('Product deleted successfully', 'success');
    } catch (error) {
        console.error('Error deleting product:', error);
        showAlert('Error deleting product', 'danger');
    }
}

function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.querySelector('.container').insertBefore(alertDiv, document.querySelector('.row'));
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

function logout() {
    localStorage.removeItem('token');
    window.location.href = '/';
} 