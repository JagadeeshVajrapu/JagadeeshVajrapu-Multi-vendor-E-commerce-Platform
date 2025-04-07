# Multi-Vendor E-Commerce Platform

A modern e-commerce platform that allows multiple vendors to sell their products and customers to browse and purchase items.

## Features

### Vendor Features
- Product Management (Add/Edit/Delete)
- Order Tracking
- Sales Analytics
- Stock Management

### Customer Features
- Product Browsing
- Shopping Cart
- Order Placement
- Order Tracking
- Coupon System

## Tech Stack
- Backend: Flask
- Database: MongoDB
- Frontend: HTML, CSS, JavaScript
- Authentication: JWT

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file with the following variables:
```
MONGODB_URI=your_mongodb_uri
JWT_SECRET_KEY=your_jwt_secret
```

4. Run the application:
```bash
python app.py
```

## Project Structure
```
├── app/
│   ├── __init__.py
│   ├── models/
│   ├── routes/
│   ├── static/
│   └── templates/
├── requirements.txt
└── README.md
``` 