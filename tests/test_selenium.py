# tests/test_selenium.py

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
import time
import threading
import sys
import os
import requests


# Get the current working directory
current_dir = os.getcwd()

# Add the path to your docker_app directory
sys.path.append(os.path.join(current_dir, 'docker_app'))

# Now you can import your modules
from Flaskapp.app import create_app, mongo
import bcrypt

@pytest.fixture(scope="module")
def test_app():
    # Setup test database
    test_config = {
        "MONGO_URI": "mongodb+srv://akshay:propertyallotment@cluster0.c9d47cy.mongodb.net/ecommerce_test_db_selenium?retryWrites=true&w=majority&appName=Cluster0",
        "TESTING": True
    }
    app = create_app(test_config)

    # Insert test data
    with app.app_context():
        mongo.db.products.insert_one({
            "name": "Selenium Test Product",
            "description": "Description for Selenium test product",
            "price": 25.99,
            "image_url": "https://www.jagranimages.com/images/newimg/15102024/15_10_2024-bestnoisesmartwatchesformen_23816072.jpg"
        })
        mongo.db.users.insert_one({
            "username": "seleniumuser",
            "password": bcrypt.hashpw("password".encode('utf-8'), bcrypt.gensalt())
        })

    # Start the Flask app in a separate thread
    server_thread = threading.Thread(target=app.run, kwargs={"port": 5005, "use_reloader": False})
    server_thread.setDaemon(True)
    server_thread.start()
    # Wait for Flask to be fully up and responsive
    def wait_for_flask():
        url = "http://localhost:5005/"
        for attempt in range(10):  # Retry 10 times
            print(f"Attempt {attempt + 1} to connect to Flask...")
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    print("Flask app is up and running!")
                    return True
            except requests.ConnectionError:
                print("Flask not up yet. Retrying...")
            time.sleep(2)  # Wait before the next attempt
        return False

    print("Waiting for Flask app to start...")
    if not wait_for_flask():
        raise RuntimeError("Flask app did not start in time")
    time.sleep(1)  # Give the server time to start

    yield app

    # Teardown
    with app.app_context():
        mongo.cx.drop_database('ecommerce_test_db_selenium')

@pytest.fixture
def browser():
    # Set up Firefox options
    firefox_options = Options()
    firefox_options.add_argument("--headless")  # Run in headless mode
    service = FirefoxService()  # Assumes geckodriver is in PATH
    driver = webdriver.Firefox(service=service, options=firefox_options)
    yield driver
    driver.quit()


def test_login_and_add_to_cart_selenium(test_app, browser):
    browser.get("http://localhost:5005/")

    # Verify home page
    assert 'Home - E-commerce App' in browser.title

    # Click on Login
    login_link = browser.find_element(By.LINK_TEXT, "Login")
    login_link.click()

    # Fill login form
    username_input = browser.find_element(By.ID, "username")
    password_input = browser.find_element(By.ID, "password")
    username_input.send_keys("seleniumuser")
    password_input.send_keys("password")

    # Submit form
    login_button = browser.find_element(By.XPATH, "//button[@type='submit']")
    login_button.click()

    # Verify login success
    assert "Logged in as seleniumuser" in browser.page_source

    # Add product to cart
    add_to_cart_button = browser.find_element(By.XPATH, "//button[contains(text(), 'Add to Cart')]")
    add_to_cart_button.click()

    # Handle alert
    time.sleep(1)  # Wait for alert to appear
    alert = browser.switch_to.alert
    assert alert.text == "Product added to cart!"
    alert.accept()

    # Navigate to cart
    cart_link = browser.find_element(By.LINK_TEXT, "Cart")
    cart_link.click()

    # Verify product in cart
    assert "Selenium Test Product" in browser.page_source
    assert "1" in browser.page_source  # Quantity
    assert "$25.99" in browser.page_source  # Price
