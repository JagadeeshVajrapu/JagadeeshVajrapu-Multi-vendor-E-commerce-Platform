# 🛒 Multi-Vendor E-Commerce Platform

A full-stack e-commerce platform that supports multiple vendors and customers. Vendors can manage their product listings, and customers can browse products, add items to the cart, apply discounts, and place orders.

---

## 🚀 Features

### 👥 User Roles
- **Vendor**:
  - Add, edit, and delete products
  - View and manage orders related to their products
  - Track product performance: sales, revenue, stock

- **Customer**:
  - Browse products by category
  - Add to cart, remove from cart, and checkout
  - Apply discount coupons
  - Track order status (Pending, Shipped, Delivered)
  - View order history

---

## 🧠 Tech Stack

### Frontend:
- HTML5, CSS3
- JavaScript (AJAX/Fetch API)
- Responsive design
- Client-side form validation

### Backend:
- **Framework**: Django REST Framework (DRF) or Flask
- **Database**: MongoDB (using `djongo` or `PyMongo`)
- **Authentication**: JWT-based auth system
- **API Features**:
  - User auth & registration
  - CRUD for products (vendors only)
  - Cart management with real-time price calculations
  - Order processing
  - Apply coupon codes for discounts

---

## 🛡️ Security
- JWT authentication
- CSRF protection
- Input validation
- Secure password hashing
- Safe queries to avoid XSS/SQL injection

---

## 🧪 Bonus Features (Optional)
- Real-time stock update using WebSockets
- Product review & rating system
- Admin panel for managing all vendors/customers

---

## 🧰 How to Run Locally

### Backend Setup:
1. Clone this repo:
   ```bash
   git clone https://github.com/your-username/multi-vendor-ecommerce.git
   cd multi-vendor-ecommerce
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use venv\Scripts\activate
   ```

3. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Add your MongoDB URI and JWT_SECRET in a `.env` file:
   ```env
   MONGO_URI=mongodb://localhost:27017/ecommerce_db
   JWT_SECRET=your_jwt_secret
   ```

5. Run the backend:
   ```bash
   python app.py  # or python manage.py runserver if using Django
   ```

---

### Frontend:
- Open `index.html` in your browser.
- Interact with the platform using AJAX/Fetch API calls.

---

## 📦 API Endpoints

### Authentication
- `POST /api/register/` – Register a new user
- `POST /api/login/` – Get JWT token

### Products (Vendor)
- `GET /api/products/` – List products
- `POST /api/products/` – Add new product
- `PUT /api/products/<id>/` – Edit product
- `DELETE /api/products/<id>/` – Delete product

### Cart & Orders (Customer)
- `POST /api/cart/add/`
- `DELETE /api/cart/remove/`
- `POST /api/checkout/`
- `GET /api/orders/history/`

---

## 🖼️ Screenshots (Optional)
_Add UI screenshots or flow diagrams here._

---

## 📜 License
MIT License – feel free to use or improve upon it for learning or personal projects.

---

## 👨‍💻 Author
- [Your Name](https://github.com/your-username)
