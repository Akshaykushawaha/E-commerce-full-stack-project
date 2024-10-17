# tests/test_unit.py

import pytest
import sys
import os

# Get the current working directory
current_dir = os.getcwd()

# Add the path to your docker_app directory
sys.path.append(os.path.join(current_dir, 'docker_app'))

# Now you can import your modules
from Flaskapp.app import create_app, mongo
# from docker_app.Flaskapp.app import create_app, mongo
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
                    "name": "Test Product 1",
                    "description": "Description for test product 1",
                    "price": 10.99,
                    "image_url": "https://www.jagranimages.com/images/newimg/15102024/15_10_2024-bestnoisesmartwatchesformen_23816072.jpg"
                },
                {
                    "name": "Test Product 2",
                    "description": "Description for test product 2",
                    "price": 20.99,
                    "image_url": "https://www.jagranimages.com/images/newimg/13102024/13_10_2024-premium_smart_watch_for_men_23815045.webp"
                }
            ])
            mongo.db.users.insert_one({
                "username": "testuser",
                "password": bcrypt.hashpw("password".encode('utf-8'), bcrypt.gensalt())  # hashed 'password'
            })
        yield client
        # Teardown
        mongo.cx.drop_database('ecommerce_test_db')

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome to Our Store' in response.data
    assert b'Test Product 1' in response.data
    assert b'Test Product 2' in response.data

def test_login_success(client):
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'password'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Logged in as testuser' in response.data

def test_login_failure(client):
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid username/password combination' in response.data

def test_add_to_cart(client):
    # Log in first
    client.post('/login', data={
        'username': 'testuser',
        'password': 'password'
    }, follow_redirects=True)
    
    # Add product to cart
    product = mongo.db.products.find_one({'name': 'Test Product 1'})
    response = client.post('/add_to_cart', data={
        'product_id': str(product['_id']),
        'quantity': 2
    })
    assert response.status_code == 200
    assert response.json['status'] == 'success'
    
    # Check cart
    response = client.get('/cart')
    assert b'Test Product 1' in response.data
    assert b'2' in response.data  # Quantity
    assert b'$21.98' in response.data  # Total

def test_remove_from_cart(client):
    # Log in first
    client.post('/login', data={
        'username': 'testuser',
        'password': 'password'
    }, follow_redirects=True)
    
    # Add product to cart
    product = mongo.db.products.find_one({'name': 'Test Product 1'})
    client.post('/add_to_cart', data={
        'product_id': str(product['_id']),
        'quantity': 2
    })
    
    # Remove product from cart
    response = client.post('/remove_from_cart', data={
        'product_id': str(product['_id'])
    })
    assert response.status_code == 200
    assert response.json['status'] == 'success'
    
    # Check cart is empty
    response = client.get('/cart')
    assert b'Your cart is empty' in response.data
