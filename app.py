from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import bcrypt

app = Flask(__name__)
app.secret_key = 'bc7f0961a2f594ce9aa32b87903fbe21'

# MongoDB Configuration
app.config["MONGO_URI"] = "mongodb+srv://akshay:propertyallotment@cluster0.c9d47cy.mongodb.net/ecommerce_db?retryWrites=true&w=majority&appName=Cluster0"
mongo = PyMongo(app)

# Routes

@app.route('/')
def home():
    products = mongo.db.products.find()
    return render_template('home.html', products=products)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = mongo.db.users
        login_user = users.find_one({'username': request.form['username']})

        if login_user:
            password = login_user['password'].encode('utf-8')
            hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
            if bcrypt.checkpw(password, hashed_password):
                session['username'] = request.form['username']
                session['user_id'] = str(login_user['_id'])
                return redirect(url_for('home'))
        
        return 'Invalid username/password combination'
    
    return render_template('login.html')

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
        return render_template('cart.html', items=items)
    else:
        return render_template('cart.html', items=[])

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
        
        hashed_pw = str(bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt()))
        users.insert_one({
            'username': request.form['username'],
            'password': hashed_pw
        })
        return redirect(url_for('login'))
    
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)
