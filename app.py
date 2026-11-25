from flask import Flask, request, jsonify
from pymongo import MongoClient
import os
import requests

app = Flask(__name__)

# Connect to MongoDB (Order Database)
mongo_uri = os.getenv('MONGO_URI', 'mongodb://order-db-service:27017/orders_db')
client = MongoClient(mongo_uri)
db = client.orders_db
orders_collection = db.orders

# The URL of the Product Service (Internal K8 DNS)
PRODUCT_SERVICE_URL = os.getenv('PRODUCT_SERVICE_URL', 'http://product-service:5000')

@app.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity')

    # 1. Microservice Call: Check if product exists
    try:
        response = requests.get(f'{PRODUCT_SERVICE_URL}/products')
        if response.status_code != 200:
            return jsonify({"error": "Product service unreachable"}), 500
        
        # Simple check (since we only return a list in this lab)
        products = response.json()
        product = next((p for p in products if p['id'] == product_id), None)
        
        if not product:
            return jsonify({"error": "Product not found"}), 404
            
    except Exception as e:
        return jsonify({"error": "Product service unreachable"}), 500

    # 2. Save the order
    new_order = {
        "product_id": product_id,
        "product_name": product['name'],
        "quantity": quantity,
        "status": "pending"
    }
    orders_collection.insert_one(new_order)
    
    return jsonify({"message": "Order created successfully", "order": new_order}), 201

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)