from flask import Flask, jsonify, request, session, redirect, url_for, render_template
from pymongo import MongoClient
from bson import ObjectId
import datetime
from flask_bcrypt import Bcrypt
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Initialize Flask-Bcrypt
bcrypt = Bcrypt(app)

# Initialize the MongoDB client and database
client = MongoClient("mongodb+srv://userxyz:userxyz@cluster0.5be8y.mongodb.net/?retryWrites=true&w=majority")
db = client["studyhacks"]
collection = db["chats"]
users_collection = db["users"]

# Define a User class that inherits from UserMixin
class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

# Initialize Flask-Login and LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# User loader function
@login_manager.user_loader
def load_user(user_id):
    user = users_collection.find_one({'user_id': user_id})
    if user:
        return User(user['user_id'])
    else:
        return None

# User registration
@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400

    # Check if the user already exists
    existing_user = users_collection.find_one({'email': email})
    if existing_user:
        return jsonify({'message': 'User already exists'}), 400

    # Generate a unique user ID
    user_id = str(ObjectId())

    # Hash the password before storing it
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    # Create the user document
    user = {
        'user_id': user_id,
        'email': email,
        'password': hashed_password
    }

    # Insert the user document into the database
    users_collection.insert_one(user)

    return jsonify({'message': 'User registered successfully'}), 201

# User login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400

    user = users_collection.find_one({'email': email})

    if not user or not bcrypt.check_password_hash(user['password'], password):
        return jsonify({'message': 'Invalid credentials'}), 401

    # Log in the user and start a session
    user_obj = User(user['user_id'])
    login_user(user_obj)

    return jsonify({'message': 'Login successful', 'user_id': user['user_id']}), 200

# User logout
@app.route('/logout') 
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200

# Change user password
@app.route('/change_password', methods=['POST'])
@login_required
def change_password():
    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')

    user = users_collection.find_one({'user_id': current_user.id})

    if not user or not bcrypt.check_password_hash(user['password'], current_password):
        return jsonify({'message': 'Current password is incorrect'}), 401

    # Hash the new password before updating it
    hashed_new_password = bcrypt.generate_password_hash(new_password).decode('utf-8')

    # Update the user's password
    users_collection.update_one({'user_id': current_user.id}, {'$set': {'password': hashed_new_password}})

    return jsonify({'message': 'Password updated successfully'}), 200

# Create a new chat
@app.route("/chats", methods=["POST"])
@login_required
def create_chat():
    data = request.get_json()
    data['created_at'] = datetime.datetime.now()
    data['user_id'] = current_user.id  # Associate the chat with the currently logged-in user

    chat_id = collection.insert_one(data).inserted_id
    return jsonify({"message": "Chat created successfully", "chat_id": str(chat_id)}), 201

@app.route("/upload", methods=["POST"])
@login_required
def upload_pdf():
    files = request.files.getlist('file')
    file=files[0]
    print(file)



# Get all chats
@app.route("/chats", methods=["GET"])
@login_required
def get_chats():
    user_id = current_user.id
    chats = list(collection.find({'user_id': user_id}))
    
    # Convert ObjectId fields to strings
    for chat in chats:
        chat["_id"] = str(chat["_id"])
    
    return jsonify(chats), 200

# Get a specific chat by ID
@app.route("/chats/<string:chat_id>", methods=["GET"])
@login_required
def get_chat(chat_id):
    user_id = current_user.id
    chat = collection.find_one({"_id": ObjectId(chat_id), 'user_id': user_id})
    if chat:
        # Convert ObjectId to string
        chat["_id"] = str(chat["_id"])
        return jsonify({"chat": chat}), 200
    else:
        return jsonify({"message": "Chat not found"}), 404

# Update a chat by ID
@app.route("/chats/<string:chat_id>", methods=["PUT"])
@login_required
def update_chat(chat_id):
    user_id = current_user.id
    data = request.get_json()
    result = collection.update_one({"_id": ObjectId(chat_id), 'user_id': user_id}, {"$set": data})
    if result.modified_count == 1:
        return jsonify({"message": "Chat updated successfully"}), 200
    else:
        return jsonify({"message": "Chat not found"}), 404

# Delete a chat by ID
@app.route("/chats/<string:chat_id>", methods=["DELETE"])
@login_required
def delete_chat(chat_id):
    user_id = current_user.id
    result = collection.delete_one({"_id": ObjectId(chat_id), 'user_id': user_id})
    if result.deleted_count == 1:
        return jsonify({"message": "Chat deleted successfully"}), 200
    else:
        return jsonify({"message": "Chat not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
