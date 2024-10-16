# tests/test_api.py

import pytest
from Flaskapp.app import create_app, mongo
from flask import session
from bson.objectid import ObjectId
import bcrypt


@pytest.fixture
def client():
    # Setup test database
    test_config = {
        "MONGO_URI": "mongodb+srv://akshay:propertyallotment@cluster0.c9d47cy.mongodb.net/ecommerce_test_db?retryWrites=true&w=majority&appName=Cluster0",
        "TESTING": True
    }
    app = create_app(test_config)
   
    with app.test_client() as client:
        with app.app_context():
            mongo.cx.drop_database('ecommerce_test_db')
            # Setup initial data
            mongo.db.products.insert_many([
                {
                    "name": "API Test Product 1",
                    "description": "Description for API test product 1",
                    "price": 15.99,
                    "image_url": "https://www.jagranimages.com/images/newimg/15102024/15_10_2024-bestnoisesmartwatchesformen_23816072.jpg"
                }
            ])
            mongo.db.users.insert_one({
                "username": "apiuser",
                "password": bcrypt.hashpw("password".encode('utf-8'), bcrypt.gensalt())   # hashed 'password'
            })
        yield client
        # Teardown
        mongo.cx.drop_database('ecommerce_test_db')

def test_add_to_cart_api(client):
    # Attempt to add to cart without logging in
    product = mongo.db.products.find_one({'name': 'API Test Product 1'})
    response = client.post('/add_to_cart', data={
        'product_id': str(product['_id']),
        'quantity': 1
    })
    assert response.status_code == 401
    assert response.json['status'] == 'error'
    
    # Log in
    client.post('/login', data={
        'username': 'apiuser',
        'password': 'password'
    }, follow_redirects=True)
    
    # Add to cart
    response = client.post('/add_to_cart', data={
        'product_id': str(product['_id']),
        'quantity': 3
    })
    assert response.status_code == 200
    assert response.json['status'] == 'success'
    
    # Check cart in DB
    user = mongo.db.users.find_one({'username': 'apiuser'})
    cart = mongo.db.carts.find_one({'user_id': str(user['_id'])})
    assert cart is not None
    assert len(cart['items']) == 1
    assert cart['items'][0]['product_id'] == str(product['_id'])
    assert cart['items'][0]['quantity'] == 3

def test_remove_from_cart_api(client):
    # Log in
    client.post('/login', data={
        'username': 'apiuser',
        'password': 'password'
    }, follow_redirects=True)
    
    # Add to cart
    product = mongo.db.products.find_one({'name': 'API Test Product 1'})
    client.post('/add_to_cart', data={
        'product_id': str(product['_id']),
        'quantity': 2
    })
    
    # Remove from cart
    response = client.post('/remove_from_cart', data={
        'product_id': str(product['_id'])
    })
    assert response.status_code == 200
    assert response.json['status'] == 'success'
    
    # Check cart in DB
    user = mongo.db.users.find_one({'username': 'apiuser'})
    cart = mongo.db.carts.find_one({'user_id': str(user['_id'])})
    assert cart is not None
    assert len(cart['items']) == 0
