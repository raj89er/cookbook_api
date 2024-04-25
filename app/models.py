
import secrets
from datetime import datetime, timedelta, timezone
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    token = db.Column(db.String)
    token_expiration = db.Column(db.DateTime)

    def __init__(self, username):
        self.username = username

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'token': self.token,
            'token_expiration': self.token_expiration
        }

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.save()

    def get_token(self):
        now = datetime.now(timezone.utc)
        if self.token and self.token_expiration > now + timedelta(minutes=1):
            return {"token": self.token, "tokenExpiration": self.token_expiration}
        self.token = secrets.token_hex(16)
        self.token_expiration = now + timedelta(hours=1)
        self.save()
        return {"token": self.token, "tokenExpiration": self.token_expiration}

    @staticmethod
    def check_token(token):
        return User.query.filter_by(token=token).first() is not None


class Recipe(db.Model):
    recipe_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    cook_time = db.Column(db.Integer)  # in minutes
    prep_time = db.Column(db.Integer)  # in minutes
    ingredients = db.relationship('Ingredient', backref='recipe', lazy=True)
    directions = db.relationship('Direction', backref='recipe', lazy=True)
    tips = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)

    def __init__(self, title, cook_time=None, prep_time=None, tips=None, user_id=None):
        self.title = title
        self.cook_time = cook_time
        self.prep_time = prep_time
        self.tips = tips
        self.user_id = user_id

    def __repr__(self):
        return f'<Recipe {self.title}>'

    def add_ingredient(self, name, quantity, units):
        ingredient = Ingredient(name=name, quantity=quantity, units=units, recipe_id=self.recipe_id)
        db.session.add(ingredient)
        db.session.commit()

    def add_direction(self, step_number, instruction):
        direction = Direction(step_number=step_number, instruction=instruction, recipe_id=self.recipe_id)
        db.session.add(direction)
        db.session.commit()

    # method to save recipe to database
    def update(self, **kwargs):
        allowed_fields = ['title', 'cook_time', 'prep_time', 'tips']
        for key, value in kwargs.items():
            if key in allowed_fields:
                setattr(self, key, value)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        return {
            'recipe_id': self.recipe_id,
            'title': self.title,
            'cook_time': self.cook_time,
            'prep_time': self.prep_time,
            'tips': self.tips,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'user_id': self.user_id,
        }
    
    

class Ingredient(db.Model):
    ingredient_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float)
    units = db.Column(db.String(20))
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.recipe_id'), nullable=False)

class Direction(db.Model):
    direction_id = db.Column(db.Integer, primary_key=True)
    step_number = db.Column(db.Integer, nullable=False)
    instruction = db.Column(db.Text, nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.recipe_id'), nullable=False)

class Favorite(db.Model):
    fav_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.recipe_id'), nullable=False)
