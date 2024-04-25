
import secrets
from flask import request
from . import app , db
from models import User
from .auth import basic_auth, token_auth

# User routes & endpoints
# [POST] /user
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
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return {"error": "An account with this username already exists"}, 400
    existing_email = User.query.filter_by(email=email).first()
    if existing_email:
        return {"error": "An account with this email already exists"}, 400
    # Generate a token for the new user
    token = secrets.token_hex(16)
    new_user = User(username=username, email=email, password=password, token=token)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    return {"success": f"Account with username '{username}' was created successfully... You're password is (password123)!"}, 201