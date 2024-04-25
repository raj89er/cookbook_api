
import secrets
from flask import request
from . import app , db
from models import User
from .auth import basic_auth, token_auth

# Token route & endpoint
@app.route('/token', methods=['GET'])
@basic_auth.login_required
def get_token():
    user = basic_auth.current_user()
    return user.get_token()

# User routes & endpoints
## [POST] /user
@app.route('/users', methods=['POST'])
def create_user():
    # Ensure the request is a JSON object
    if not request.is_json:
        return {"error": "Request must be in JSON format"}, 400
    # chheck request for required/missing fields
    data = request.json
    required_fields = ['username', 'password', 'email']
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    if missing_fields:
        return {"error": f"You're missing the following fields: {', '.join(missing_fields)}"}, 400
    # Extract the username, password, and email from the request
    username = data['username']
    email = data['email']
    password = data['password']
    # Check if the username/email already exists
    existing_user = db.excute(User.query.filter(User.username == username).exists()).scalar()
    if existing_user:
        return {"error": "An account with the email provided already exists"}, 400
    existing_email = db.excute(User.query.filter(User.email == email).exists()).scalar()
    if existing_email:
        return {"error": "An account with the email provided already exists"}, 400
    # Generate a token for the new user
    token = secrets.token_hex(16)
    new_user = User(username=username, email=email, password=password, token=token)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    return {"success": f"Account with username '{username}' was created successfully... You're password is (password123)!"}, 201

## [GET] /users/me
@app.route('/users/me', methods=['GET'])
@token_auth.login_required
def get_me():
    user = token_auth.current_user()
    return user.to_dict()

## [GET] /user/<user_id>
@app.route('/users/<int:user_id>', methods=['GET'])
@token_auth.login_required
def get_user(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        return {"error": "User not found"}, 404
    return user.to_dict() , 200

## [PUT] /users/<int:user_id>
@app.route('/users/<int:user_id>', methods=['PUT'])
@token_auth.login_required
def update_user(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        return {"error": "User not found"}, 404
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    if username:
        existing_username = User.query.filter(User.username == username, User.user_id != user_id).first()
        if existing_username:
            return {"error": "Username with name already exists"}, 400
        user.username = username
    if email:
        existing_email = User.query.filter(User.email == email, User.user_id != user_id).first()
        if existing_email:
            return {"error": "That email already exists as a user, try with another one."}, 400
        user.email = email
    if password:
        user.set_password(password)
    db.session.commit()
    return {"success": "User updated successfully"}, 200

## [DELETE] /users/<int:user_id>
@app.route('/users/<int:user_id>', methods=['DELETE'])
@token_auth.login_required
def delete_user(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        return {"error": "User not found"}, 404
    db.session.delete(user)
    db.session.commit()
    return {"success": "User deleted successfully"}, 200
