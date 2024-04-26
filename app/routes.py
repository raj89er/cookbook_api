
import secrets
from flask import request
from . import app , db
from .models import User, Recipe, Favorite, Ingredient, Direction
from .auth import basic_auth, token_auth

# Token route & endpoint
@app.route('/token', methods=['GET'])
@basic_auth.login_required
def get_token():
    user = basic_auth.current_user()
    return user.get_token()

# [POST] /recipes
@app.route('/recipes', methods=['POST'])
def add_recipe():
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
    data = request.get_json()
    title = data.get('title')
    cook_time = data.get('cook_time')
    prep_time = data.get('prep_time')
    ingredients_data = data.get('ingredients', [])
    directions_data = data.get('directions', [])
    tips = data.get('tips')
    new_recipe = Recipe(title=title, cook_time=cook_time, prep_time=prep_time, tips=tips)
    # Create the new recipe
    # Add ingredients to the recipe
    for ingredient_data in ingredients_data:
        name = ingredient_data.get('name')
        quantity = ingredient_data.get('quantity')
        units = ingredient_data.get('units')
        new_recipe.add_ingredient(name=name, quantity=quantity, units=units)

    # Add directions to the recipe
    for direction_data in directions_data:
        step_number = direction_data.get('step_number')
        instruction = direction_data.get('instruction')
        new_recipe.add_direction(step_number=step_number, instruction=instruction)

    # Save the new recipe to the database
    db.session.add(new_recipe)
    db.session.commit()
    return {"success": f"Recipe {new_recipe.title} created successfully"}, 201

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
    ingredients_data = data.get('ingredients', [])
    directions_data = data.get('directions', [])
    tips = data.get('tips', '')
    # Create the new recipe
    new_recipe = Recipe(
        title=title,
        cook_time=cook_time,
        prep_time=prep_time,
        ingredients=[Ingredient(**ingredient) for ingredient in ingredients_data],
        directions=[Direction(**direction) for direction in directions_data],
        tips=tips)
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


# [DELETE] /recipes/<int:recipe_id>
@app.route('/recipes/<int:recipe_id>', methods=['DELETE'])
@token_auth.login_required
def delete_recipe(recipe_id):
    recipe = Recipe.query.get(recipe_id)
    if recipe is None:
        return {"error": "Recipe not found"}, 404
    if recipe.user_id != token_auth.current_user().user_id:
        return {"error": "You do not have permission to delete this recipe"}, 403
    db.session.delete(recipe)
    db.session.commit()
    return {"success": "Recipe has been deleted successfully"}, 200

# [GET] /favorites
@app.route('/favorites', methods=['GET'])
@token_auth.login_required
def get_favorites():
    current_user = token_auth.current_user()
    favorite_recipes = db.session.query(Recipe).join(Favorite).filter(Favorite.user_id == current_user.user_id, Favorite.is_favorite == True).all()
    favorite_list = []
    for recipe in favorite_recipes:
        favorite_list.append(recipe.to_dict())
    return {"favorites": favorite_list}, 200


# [POST] /favorites/<int:recipe_id>
@app.route('/favorites/<int:recipe_id>', methods=['POST'])
@token_auth.login_required
def toggle_favorite(recipe_id):
    current_user = token_auth.current_user()
    recipe = db.session.get(Recipe, recipe_id)
    if recipe is None:
        return {"error": f"Recipe with ID {recipe_id} not found"}, 404
    favorite = db.session.query(Favorite).filter_by(user_id=current_user.user_id, recipe_id=recipe_id).first()
    if favorite:
        favorite.is_favorite = not favorite.is_favorite
    else:
        favorite = Favorite(user_id=current_user.user_id, recipe_id=recipe_id)
        db.session.add(favorite)
    db.session.commit()
    return {"success": "Favorite status updated successfully"}, 200


# [DELETE] /favorites/<recipe_id>
@app.route('/favorites/<int:recipe_id>', methods=['DELETE'])
@token_auth.login_required
def remove_favorite(recipe_id):
    current_user = token_auth.current_user()
    favorite = db.session.query(Favorite).filter_by(user_id=current_user.user_id, recipe_id=recipe_id).first()
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        return {"success": "Recipe removed from favorites successfully"}, 200
    else:
        return {"error": "Recipe is not in your favorites"}, 404



