from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import bcrypt
import logging
from elasticsearch import Elasticsearch
import os

# MongoDB Configuration
mongo = PyMongo()


# Connect to Elasticsearch
try:
    print("Using elasticsearch as: elasticsearch:9200...")
    es = Elasticsearch([{'host': 'elasticsearch', 'port': 9200, 'scheme': 'http'}])
    try:
        response = es.info()
        print("Elasticsearch is reachable:", response)
    except Exception as e:
        print(f"Error connecting to Elasticsearch: {e}")
        # Check if Elasticsearch is available
        if not es.ping():
            print("Using elasticsearch as: localhost:9200...")
            es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'scheme': 'http'}])
            try:
                response = es.info()
                print("Elasticsearch is reachable:", response)
            except Exception as e:
                print(f"Error connecting to Elasticsearch: {e}")
                if not es.ping():
                    print("Using elasticsearch as: 172.31.26.196:9200...")
                    es = Elasticsearch([{'host': '172.31.26.196', 'port': 9200, 'scheme': 'http'}])
                    try:
                        response = es.info()
                        print("Elasticsearch is reachable:", response)
                    except Exception as e:
                        print(f"Error connecting to Elasticsearch: {e}")
                        if not es.ping():
                            raise ValueError("Connection to Elasticsearch failed")
except Exception as e:  # Catching all exceptions
    print(f"Error connecting to Elasticsearch: {e}")
    es = None  # Disable logging to Elasticsearch if it fails

homepg="""
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Home - E-commerce App</title>
    <!-- <link rel="stylesheet" href="{{ url_for('static', filename='css/styles.css') }}"> -->
    <!-- <script src="{{ url_for('static', filename='js/scripts.js') }}" defer></script> -->
     <script>function addToCart(productId) {
        fetch('/add_to_cart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `product_id=${productId}&quantity=1`
        })
        .then(response => response.json())
        .then(data => {
            if(data.status === 'success') {
                alert('Product added to cart!');
            } else {
                alert(data.message);
                window.location.href = '/login';
            }
        })
        .catch(error => console.error('Error:', error));
    }
    
    function removeFromCart(productId) {
        fetch('/remove_from_cart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `product_id=${productId}`
        })
        .then(response => response.json())
        .then(data => {
            if(data.status === 'success') {
                alert('Product removed from cart!');
                window.location.reload();
            } else {
                alert(data.message);
            }
        })
        .catch(error => console.error('Error:', error));
    }
    </script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
            color: #333;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }

        /* Top bar styling */
        header {
            background-color: #ff9800;
            color: white;
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: fixed;
            width: 100%;
            height: 60px; /* Fixed height for mobile and desktop */
            top: 0;
            left: 0;
            z-index: 1000;
        }

        header h1 {
            font-size: 2rem;
        }

        nav ul {
            list-style: none;
            padding: 0;
            margin: 0;
            display: flex;
            gap: 15px;
        }

        nav ul li {
            display: inline;
        }

        nav ul li a {
            color: white;
            text-decoration: none;
            font-weight: bold;
        }

        nav ul li a:hover {
            text-decoration: underline;
        }

        /* Sidebar styling */
        .sidebar {
            width: 250px;
            background-color: #37474f;
            position: fixed;
            top: 70px; /* Adjusted to start below the header */
            bottom: 0;
            padding: 20px;
            color: white;
        }

        .sidebar h2 {
            font-size: 1.5rem;
            margin-bottom: 20px;
        }

        .sidebar a {
            display: block;
            padding: 10px;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin-bottom: 10px;
            background-color: #546e7a;
        }

        .sidebar a:hover {
            background-color: #ff9800;
        }

        /* Main content */
        main {
            margin-left: 270px;
            padding: 100px 200px 20px; /* Adjusted padding to ensure content is visible below the fixed header */
        }

        .products-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr); /* 3-column grid for desktop */
            gap: 20px;
        }

        .product-card {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            text-align: center;
        }

        .product-card img {
            width: 100%;
            height: 200px;
            object-fit: cover;
            border-radius: 10px;
            margin-bottom: 10px;
        }

        .product-card h3 {
            font-size: 1.2rem;
            color: #ff9800;
            margin-bottom: 10px;
        }

        .product-card p {
            color: #757575;
            margin-bottom: 15px;
        }

        .add-to-cart-btn {
            background-color: #ff9800;
            border: none;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1rem;
        }

        .add-to-cart-btn:hover {
            background-color: #f57c00;
        }

        .login-link {
            color: #ff9800;
            font-weight: bold;
            text-decoration: none;
        }

        .login-link:hover {
            text-decoration: underline;
        }

        /* Footer styling */
        footer {
            background-color: #37474f;
            color: white;
            text-align: center;
            padding: 20px 0;
            margin-top: auto;
            width: 100%;
        }

        footer a {
            color: #ff9800;
            text-decoration: none;
        }

        footer a:hover {
            text-decoration: underline;
        }

        /* Responsive design */
        @media screen and (max-width: 768px) {
            /* Adjusting the sidebar for mobile */
            .sidebar {
                width: 100%;
                position: relative;
                top: 60px; /* Adjust based on header height */
                margin-bottom: 20px;
            }

            main {
                margin-left: 0;
                padding: 20px; /* Reduce padding for mobile */
            }

            .products-grid {
                grid-template-columns: 1fr; /* 1-column grid for mobile */
            }

            header {
                height: auto; /* Adjust header height */
                flex-direction: column; /* Stack header elements */
                text-align: center;
            }

            nav ul {
                flex-direction: column;
                gap: 10px;
            }
        }
    </style>

</head>

<body>

    <!-- Top Bar -->
    <header>
        <h1>E-commerce Store</h1>
        <nav>
            <ul>
                {% if session.username %}
                    <li>Logged in as {{ session.username }}</li>
                    <li><a href="{{ url_for('cart') }}">Cart</a></li>
                    <li><a href="{{ url_for('logout') }}">Logout</a></li>
                {% else %}
                    <li><a href="{{ url_for('login') }}">Login</a></li>
                    <li><a href="{{ url_for('register') }}">Register</a></li>
                {% endif %}
            </ul>
        </nav>
    </header>

    <!-- Sidebar -->
    <aside class="sidebar">
        <h2>Categories</h2>
        <a href="#">Electronics</a>
        <a href="#">Fashion</a>
        <a href="#">Home & Garden</a>
        <a href="#">Beauty & Health</a>
        <a href="#">Sports</a>
    </aside>

    <!-- Main Content -->
    <main>
        <h2>Featured Products</h2>
        <div class="products-grid">
            {% for product in products %}
                <div class="product-card">
                    <img src="{{ product.image_url }}" alt="{{ product.name }}">
                    <h3>{{ product.name }}</h3>
                    <p>{{ product.description }}</p>
                    <p>Price: ${{ "%.2f"|format(product.price) }}</p>
                    {% if session.username %}
                        <button class="add-to-cart-btn" onclick="addToCart('{{ product._id }}')">Add to Cart</button>
                    {% else %}
                        <p><a class="login-link" href="{{ url_for('login') }}">Login to add to cart</a></p>
                    {% endif %}
                </div>
            {% endfor %}
        </div>
    </main>

    <!-- Footer -->
    <footer>
        <p>&copy; 2024 E-commerce App. All rights reserved.</p>
        <nav>
            <a href="#">Privacy Policy</a> |
            <a href="#">Terms of Service</a> |
            <a href="#">Contact Us</a>
        </nav>
    </footer>

</body>

</html>
"""

cartpg = """"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Cart - E-commerce App</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
            color: #333;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }

        /* Top bar styling */
        header {
            background-color: #ff9800;
            color: white;
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: fixed;
            width: 98%;
            height: 6%;
            top: 0;
            left: 0;
            z-index: 1000;
        }

        header h1 {
            font-size: 2rem;
        }

        nav a, nav span {
            color: white;
            text-decoration: none;
            font-weight: bold;
            margin-left: 15px;
        }

        nav a:hover {
            text-decoration: underline;
        }

        /* Main content */
        main {
            flex: 1;
            margin-left: auto;
            margin-right: auto;
            padding: 100px 20px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
        }

        table th, table td {
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }

        table th {
            background-color: #ff9800;
            color: white;
        }

        table td {
            background-color: white;
        }

        table td button {
            background-color: #ff9800;
            border: none;
            color: white;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.9rem;
        }

        table td button:hover {
            background-color: #f57c00;
        }

        h3 {
            text-align: right;
            font-size: 1.5rem;
            color: #ff9800;
        }

        /* Footer styling */
        footer {
            background-color: #37474f;
            color: white;
            text-align: center;
            padding: 20px 0;
            width: 100%;
            margin-top: auto;
        }

        footer a {
            color: #ff9800;
            text-decoration: none;
        }

        footer a:hover {
            text-decoration: underline;
        }

        /* Responsive design */
        @media screen and (max-width: 768px) {
            table th, table td {
                padding: 10px;
            }

            h3 {
                text-align: center;
            }
        }
    </style>
    <!-- <script src="{{ url_for('static', filename='js/scripts.js') }}" defer></script> -->
     <script>function addToCart(productId) {
        fetch('/add_to_cart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `product_id=${productId}&quantity=1`
        })
        .then(response => response.json())
        .then(data => {
            if(data.status === 'success') {
                alert('Product added to cart!');
            } else {
                alert(data.message);
                window.location.href = '/login';
            }
        })
        .catch(error => console.error('Error:', error));
    }
    
    function removeFromCart(productId) {
        fetch('/remove_from_cart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `product_id=${productId}`
        })
        .then(response => response.json())
        .then(data => {
            if(data.status === 'success') {
                alert('Product removed from cart!');
                window.location.reload();
            } else {
                alert(data.message);
            }
        })
        .catch(error => console.error('Error:', error));
    }
    </script>
</head>
<body>
    <header>
        <h1>Your Cart</h1>
        <nav>
            <a href="{{ url_for('home') }}">Home</a>
            <span>Logged in as {{ session.username }}</span>
            <a href="{{ url_for('logout') }}">Logout</a>
        </nav>
    </header>

    <main>
        {% if items %}
            <table>
                <thead>
                    <tr>
                        <th>Product</th>
                        <th>Price</th>
                        <th>Quantity</th>
                        <th>Total</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    {% for item in items %}
                        <tr>
                            <td>{{ item.name }}</td>
                            <td>${{ "%.2f"|format(item.price) }}</td>
                            <td>{{ item.quantity }}</td>
                            <td>${{ "%.2f"|format(item.total) }}</td>
                            <td><button onclick="removeFromCart('{{ item.product_id }}')">Remove</button></td>
                        </tr>
                    {% endfor %}
                </tbody>
            </table>
            <h3>Total: ${{ "%.2f"|format(items|sum(attribute='total')) }}</h3>
        {% else %}
            <p>Your cart is empty.</p>
        {% endif %}
    </main>

    <footer>
        <p>&copy; 2024 E-commerce App. All rights reserved.</p>
    </footer>
</body>
</html>

"""

loginpg = """"<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - E-commerce App</title>
    <style>
    body {
        font-family: Arial, sans-serif;
        margin: 0;
        padding: 0;
        background-color: #f4f4f4;
        color: #333;
        display: flex;
        flex-direction: column;
        min-height: 100vh; /* Ensures the body takes the full height of the viewport */
    }
    
    /* Top bar styling */
    header {
        background-color: #ff9800;
        color: white;
        padding: 15px 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: fixed;
        width: 98%;
        height: 6%;
        top: 0;
        left: 0;
        z-index: 1000;
    }
    
    header h1 {
        font-size: 2rem;
    }
    
    nav ul {
        list-style: none;
        padding: 0;
        margin: 0;
        display: flex;
        gap: 15px;
    }
    
    nav ul li {
        display: inline;
    }
    
    nav ul li a {
        color: white;
        text-decoration: none;
        font-weight: bold;
    }
    
    nav ul li a:hover {
        text-decoration: underline;
    }
    
    /* Sidebar styling */
    .sidebar {
        width: 250px;
        background-color: #37474f;
        position: fixed;
        top: 70px; /* Adjusted for header */
        bottom: 0;
        padding: 20px;
        color: white;
    }
    
    .sidebar h2 {
        font-size: 1.5rem;
        margin-bottom: 20px;
    }
    
    .sidebar a {
        display: block;
        padding: 10px;
        color: white;
        text-decoration: none;
        border-radius: 5px;
        margin-bottom: 10px;
        background-color: #546e7a;
    }
    
    .sidebar a:hover {
        background-color: #ff9800;
    }
    
    /* Main content */
    main {
        flex: 1; /* This allows the main content to stretch and fill available space */
        margin-left: 270px;
        padding: 100px 20px;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    
    form {
        background-color: white;
        padding: 30px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        width: 400px;
    }
    
    form label {
        display: block;
        margin-bottom: 10px;
        font-weight: bold;
        color: #333;
    }
    
    form input {
        width: 100%;
        padding: 10px;
        margin-bottom: 20px;
        border: 1px solid #ccc;
        border-radius: 5px;
    }
    
    form button {
        background-color: #ff9800;
        border: none;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        cursor: pointer;
        width: 100%;
        font-size: 1rem;
        margin-top: 10px;
    }
    
    form button:hover {
        background-color: #f57c00;
    }
    
    /* Footer styling */
    footer {
        background-color: #37474f;
        color: white;
        text-align: center;
        padding: 20px 0;
        width: 100%;
        margin-top: auto; /* Ensures the footer stays at the bottom */
    }
    
    footer a {
        color: #ff9800;
        text-decoration: none;
    }
    
    footer a:hover {
        text-decoration: underline;
    }
    
    /* Responsive design */
    @media screen and (max-width: 600px) {
        .sidebar {
            width: 100%;
            position: relative;
            top: 0;
            margin-bottom: 20px;
        }
    
        main {
            margin-left: 0;
        }
    }
    
    </style>

</head>

<body>

    <!-- Top Bar -->
    <header>
        <h1>Login</h1>
        <nav>
            <ul>
                <li><a href="{{ url_for('home') }}">Home</a></li>
                <li><a href="{{ url_for('register') }}">Register</a></li>
            </ul>
        </nav>
    </header>

    <!-- Sidebar -->
    <aside class="sidebar">
        <h2>Categories</h2>
        <a href="#">Electronics</a>
        <a href="#">Fashion</a>
        <a href="#">Home & Garden</a>
        <a href="#">Beauty & Health</a>
        <a href="#">Sports</a>
    </aside>

    <!-- Main Content -->
    <main>
        <form action="{{ url_for('login') }}" method="POST">
            <label for="username">Username:</label>
            <input type="text" name="username" id="username" required>

            <label for="password">Password:</label>
            <input type="password" name="password" id="password" required>

            <button type="submit">Login</button>
        </form>
    </main>

    <!-- Footer -->
    <footer>
        <p>&copy; 2024 E-commerce App. All rights reserved.</p>
        <nav>
            <a href="#">Privacy Policy</a> |
            <a href="#">Terms of Service</a> |
            <a href="#">Contact Us</a>
        </nav>
    </footer>

</body>

</html>

"""
regpg = """"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Register - E-commerce App</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
            color: #333;
            display: flex;
            flex-direction: column;
            min-height: 100vh; /* Ensures full height layout */
        }

        /* Top bar styling */
        header {
            background-color: #ff9800;
            color: white;
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: fixed;
            width: 98%;
            height: 6%;
            top: 0;
            left: 0;
            z-index: 1000;
        }

        header h1 {
            font-size: 2rem;
        }

        nav a {
            color: white;
            text-decoration: none;
            font-weight: bold;
            margin-left: 15px;
        }

        nav a:hover {
            text-decoration: underline;
        }

        /* Main content */
        main {
            flex: 1; /* Flex to push footer down */
            margin-left: auto;
            margin-right: auto;
            padding: 100px 20px;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        form {
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            width: 400px;
        }

        form label {
            display: block;
            margin-bottom: 10px;
            font-weight: bold;
            color: #333;
        }

        form input {
            width: 100%;
            padding: 10px;
            margin-bottom: 20px;
            border: 1px solid #ccc;
            border-radius: 5px;
        }

        form button {
            background-color: #ff9800;
            border: none;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            width: 100%;
            font-size: 1rem;
            margin-top: 10px;
        }

        form button:hover {
            background-color: #f57c00;
        }

        /* Footer styling */
        footer {
            background-color: #37474f;
            color: white;
            text-align: center;
            padding: 20px 0;
            width: 100%;
            margin-top: auto; /* Ensures footer stays at the bottom */
        }

        footer a {
            color: #ff9800;
            text-decoration: none;
        }

        footer a:hover {
            text-decoration: underline;
        }

        /* Responsive design */
        @media screen and (max-width: 600px) {
            main {
                padding: 50px 10px;
            }

            form {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <header>
        <h1>Register</h1>
        <nav>
            <a href="{{ url_for('home') }}">Home</a>
            <a href="{{ url_for('login') }}">Login</a>
        </nav>
    </header>

    <main>
        <form action="{{ url_for('register') }}" method="POST">
            <label for="username">Username:</label>
            <input type="text" name="username" id="username" required>
            
            <label for="password">Password:</label>
            <input type="password" name="password" id="password" required>
            
            <button type="submit">Register</button>
        </form>
    </main>

    <footer>
        <p>&copy; 2024 E-commerce App. All rights reserved.</p>
    </footer>
</body>
</html>

"""

# Define the path for the log file
log_file_path = 'Flaskapp/reports/app.log'
# Check if the log file exists
if os.path.isfile(log_file_path):
    print(f"The log file '{log_file_path}' exists.")
else:
    print(f"The log file '{log_file_path}' does not exist. It will be created.")

# Check if the directory exists; if not, create it
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

# Set up file logging
logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Function to log to Elasticsearch
def log_to_elk(message):
    if es:
        try:
            es.index(index="flask-logs", doc_type="_doc", body={"message": message})
        except ElasticsearchException as e:
            logging.error(f"Failed to log to Elasticsearch: {e}")
    else:
        logging.error("Elasticsearch not connected. Cannot log message.")


def create_app(test_config=None):
    app = Flask(__name__)
    app.secret_key = 'bc7f0961a2f594ce9aa32b87903fbe21'

    # MongoDB Configuration
    if test_config:
        app.config.update(test_config)
    else:
        app.config["MONGO_URI"] = "mongodb+srv://akshay:propertyallotment@cluster0.c9d47cy.mongodb.net/ecommerce_db?retryWrites=true&w=majority&appName=Cluster0"

    mongo.init_app(app)

    # Routes
    @app.route('/')
    def home():
        print(os.getcwd())
        print(os.listdir(os.getcwd()))
        products = mongo.db.products.find()
        # log_to_elk("Home page accessed")
        # return render_template('home.html', products=products)
        return render_template_string(homepg, products=products)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            users = mongo.db.users
            login_user = users.find_one({'username': request.form['username']})

            if login_user:
                if type(login_user['password']) != bytes:
                    password_in_db = login_user['password'].encode('utf-8')
                else:
                    password_in_db = login_user['password']
                if bcrypt.checkpw(request.form['password'].encode('utf-8'), password_in_db):
                    session['username'] = request.form['username']
                    session['user_id'] = str(login_user['_id'])
                    return redirect(url_for('home'))
                else:
                    return 'Invalid username/password combination'

        # return render_template('login.html')
        return render_template_string(loginpg)

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('home'))

    @app.route('/cart')
    def cart():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        user_id = session['user_id']
        cart = mongo.db.carts.find_one({'user_id': user_id})
        
        if cart:
            items = []
            for item in cart['items']:
                product = mongo.db.products.find_one({'_id': ObjectId(item['product_id'])})
                if product:
                    items.append({
                        'product_id': str(product['_id']),
                        'name': product['name'],
                        'price': product['price'],
                        'quantity': item['quantity'],
                        'total': product['price'] * item['quantity']
                    })
            # return render_template('cart.html', items=items)
            return render_template_string(cartpg, items=items)
        else:
            # return render_template('cart.html', items=[])
            return render_template_string(cartpg, items=items)

    @app.route('/add_to_cart', methods=['POST'])
    def add_to_cart():
        if 'user_id' not in session:
            return jsonify({'status': 'error', 'message': 'User not logged in'}), 401
        
        user_id = session['user_id']
        product_id = request.form['product_id']
        quantity = int(request.form.get('quantity', 1))
        
        cart = mongo.db.carts.find_one({'user_id': user_id})
        
        if cart:
            # Check if product already in cart
            for item in cart['items']:
                if item['product_id'] == product_id:
                    item['quantity'] += quantity
                    break
            else:
                cart['items'].append({'product_id': product_id, 'quantity': quantity})
            mongo.db.carts.update_one({'user_id': user_id}, {'$set': {'items': cart['items']}})
        else:
            # Create new cart
            mongo.db.carts.insert_one({
                'user_id': user_id,
                'items': [{'product_id': product_id, 'quantity': quantity}]
            })
        
        return jsonify({'status': 'success'})

    @app.route('/remove_from_cart', methods=['POST'])
    def remove_from_cart():
        if 'user_id' not in session:
            return jsonify({'status': 'error', 'message': 'User not logged in'}), 401
        
        user_id = session['user_id']
        product_id = request.form['product_id']
        
        cart = mongo.db.carts.find_one({'user_id': user_id})
        
        if cart:
            new_items = [item for item in cart['items'] if item['product_id'] != product_id]
            mongo.db.carts.update_one({'user_id': user_id}, {'$set': {'items': new_items}})
        
        return jsonify({'status': 'success'})

    # Utility route to register users (optional)
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            users = mongo.db.users
            existing_user = users.find_one({'username': request.form['username']})
            
            if existing_user:
                return 'Username already exists'
            
            hashed_pw = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
            users.insert_one({
                'username': request.form['username'],
                'password': hashed_pw
            })
            return redirect(url_for('login'))
        
        # return render_template('register.html')
        return render_template_string(regpg)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0')