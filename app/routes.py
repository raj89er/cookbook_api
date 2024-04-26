
import secrets
from flask import request
from . import app , db
from models import User, Recipe, Favorite
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
    existing_user = db.session.get(User.query.filter(User.username == username).exists()).scalar()
    if existing_user:
        return {"error": "An account with the email provided already exists"}, 400
    existing_email = db.session.get(User.query.filter(User.email == email).exists()).scalar()
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

## [PUT] /users/me
@app.route('/users/me', methods=['PUT'])
@token_auth.login_required
def update_user():
    user = token_auth.current_user()
    if user is None:
        return {"error": "User not found"}, 404
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    if username:
        existing_username = User.query.filter(User.username == username, User.user_id != user.user_id).first()
        if existing_username:
            return {"error": "An account with that username already exists"}, 400
        user.username = username
    if email:
        existing_email = User.query.filter(User.email == email, User.user_id != user.user_id).first()
        if existing_email:
            return {"error": "An account with that email already exists"}, 400
        user.email = email
    if password:
        user.set_password(password)
    db.session.commit()
    return {"success": "User updated successfully"}, 200

## [DELETE] /users/me
@app.route('/users/me', methods=['DELETE'])
@token_auth.login_required
def delete_user():
    user = token_auth.current_user()
    if user is None:
        return {"error": "Disturbance in the force detected... You do not exist"}, 404
    db.session.delete(user)
    db.session.commit()
    return {"success": "User deleted successfully"}, 200


# Recipe routes & endpoints
## [GET] /recipes
@app.route('/recipes', methods=['GET'])
def get_recipes():
    recipes = db.session.query(Recipe).all()
    recipe_list = [recipe.to_dict() for recipe in recipes]
    return {"recipes": recipe_list}, 200
    

## [GET] /recipes/<recipe_id>
@app.route('/recipes/<int:recipe_id>', methods=['GET'])
def get_recipe(recipe_id):
    recipe = db.session.get(Recipe, recipe_id)
    if recipe:
        return recipe.to_dict(), 200
    else:
        return {'error': 'Recipe not found'}, 404

# [POST] /recipes
@app.route('/recipes', methods=['POST'])
@token_auth.login_required
def create_recipe():
    data = request.json
    # JSON check
    if not request.is_json:
        return {"error": "Request must be in JSON format"}, 400
    # Required fields check
    required_fields = ['title', 'cook_time', 'prep_time']
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    if missing_fields:
        return {"error": f"You're missing the following fields in the request: {', '.join(missing_fields)}"}, 400
    # Extract data from JSON
    title = data['title']
    cook_time = data['cook_time']
    prep_time = data['prep_time']
    ingredients = data.get('ingredients', [])
    directions = data.get('directions', [])
    tips = data.get('tips', '')
    # Create the new recipe
    current_user = token_auth.current_user()
    new_recipe = Recipe(title=title, cook_time=cook_time, prep_time=prep_time, user_id=current_user.user_id,
                        ingredients=ingredients, directions=directions, tips=tips)
    db.session.add(new_recipe)
    db.session.commit()
    return {"success": "Recipe created successfully"}, 201

## [PUT] /recipes/<recipe_id>
@app.route('/recipes/<int:recipe_id>', methods=['PUT'])
@token_auth.login_required
def update_recipe(recipe_id):
    recipe = db.session.get(Recipe, recipe_id)
    if recipe is None:
        return {"error": f'Recipe with ID {recipe_id} not found'}, 404
    if recipe.user_id != token_auth.current_user().user_id:
        return {"error": "Stop trying to edit a recipe you didn't post!"}, 403
    data = request.json
    # Update recipe details
    recipe.update(**data)
    return {"success": "Recipe updated successfully"}, 200


## [DELETE] /recipes/<recipe_id>
@app.route('/recipes/<int:recipe_id>', methods=['DELETE'])
@token_auth.login_required
def delete_recipe(recipe_id):
    recipe = db.session.get(recipe_id)
    if recipe is None:
        return {"error": f'Recipe with ID {recipe_id} not found'}, 404
    if recipe.user_id != token_auth.current_user().user_id:
        return {"error": "You do not have permission to delete this recipe"}, 403
    recipe.delete()
    return {"success": "Recipe deleted successfully"}, 200

# Favorites routes & endpoints
## [GET] /favorites
@app.route('/favorites', methods=['GET'])
@token_auth.login_required
def get_favorites():
    user = token_auth.current_user()
    favorites = Favorite.query.filter_by(user_id=user.user_id, is_favorite=True).all()
    favorite_recipes = [fav.recipe.to_dict() for fav in favorites]
    return {"favorites": favorite_recipes}, 200

## [POST] /favorites/<recipe_id>
@app.route('/favorites/<int:recipe_id>', methods=['POST'])
@token_auth.login_required
def add_favorite(recipe_id):
    user = token_auth.current_user()
    recipe = db.session.get(Recipe, recipe_id)
    if recipe is None:
        return {"error": f'Recipe with ID {recipe_id} not found'}, 404
    favorite = Favorite.query.filter_by(user_id=user.user_id, recipe_id=recipe_id).first()
    if favorite:
        if favorite.is_favorite:
            return {"error": "Recipe is already in favorites"}, 400
        else:
            favorite.is_favorite = True
            db.session.commit()
            return {"success": "Recipe added to favorites"}, 200
    else:
        new_favorite = Favorite(user_id=user.user_id, recipe_id=recipe_id, is_favorite=True)
        db.session.add(new_favorite)
        db.session.commit()
        return {"success": "Recipe added to favorites"}, 200

## [DELETE] /favorites/<recipe_id>
@app.route('/favorites/<int:recipe_id>', methods=['DELETE'])
@token_auth.login_required
def remove_favorite(recipe_id):
    user = token_auth.current_user()
    favorite = Favorite.query.filter_by(user_id=user.user_id, recipe_id=recipe_id).first()
    if favorite:
        if favorite.is_favorite:
            favorite.is_favorite = False
            db.session.commit()
            return {"success": "Recipe removed from favorites"}, 200
        else:
            return {"error": "Recipe is not in favorites"}, 400
    else:
        return {"error": "Favorite entry not found"}, 404

