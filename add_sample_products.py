from app import mongo
from bson import ObjectId

def add_sample_products():
    try:
        # Clear existing products
        mongo.db.products.delete_many({})
        print("Cleared existing products")

        # Sample products with local image paths
        products = [
            {
                'name': 'Premium Wireless Headphones',
                'description': 'High-quality wireless headphones with noise cancellation',
                'price': 199.99,
                'stock': 50,
                'category': 'Electronics',
                'images': ['/static/images/Premium Wireless Headphones.png']
            },
            {
                'name': 'Smart Fitness Watch',
                'description': 'Track your fitness goals with this advanced smartwatch',
                'price': 149.99,
                'stock': 30,
                'category': 'Electronics',
                'images': ['/static/images/Smart Fitness Watch.png']
            },
            {
                'name': 'Organic Cotton T-Shirt',
                'description': 'Comfortable and eco-friendly cotton t-shirt',
                'price': 29.99,
                'stock': 100,
                'category': 'Clothing',
                'images': ['/static/images/Organic Cotton T-Shirt.png']
            },
            {
                'name': 'Professional Chef Knife',
                'description': 'High-quality chef knife for professional cooking',
                'price': 89.99,
                'stock': 20,
                'category': 'Kitchen',
                'images': ['/static/images/ProfessionalChefKnife.png']
            },
            {
                'name': 'Leather Messenger Bag',
                'description': 'Stylish and durable leather messenger bag',
                'price': 129.99,
                'stock': 15,
                'category': 'Accessories',
                'images': ['/static/images/Leather Messenger Bag.png']
            }
        ]

        # Insert products
        result = mongo.db.products.insert_many(products)
        print(f"Added {len(result.inserted_ids)} products")

    except Exception as e:
        print(f"Error adding products: {str(e)}")

if __name__ == '__main__':
    add_sample_products() 