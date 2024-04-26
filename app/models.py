import secrets
from datetime import datetime, timedelta, timezone
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text(50), unique=True, nullable=False)
    email = db.Column(db.Text(50), unique=True)
    password = db.Column(db.Text, nullable=False)
    token = db.Column(db.Text)
    token_expiration = db.Column(db.DateTime)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_password(kwargs.get('password', ''))

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

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
            'email': self.email,
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
    title = db.Column(db.Text, nullable=False)
    cook_time = db.Column(db.Integer)  # in minutes
    prep_time = db.Column(db.Integer)  # in minutes
    ingredients = db.relationship('Ingredient', backref='recipe', lazy=True)
    directions = db.relationship('Direction', backref='recipe', lazy=True)
    tips = db.Column(db.Text)
    created_at = db.Column(db.DateTime, datetime.now(timezone.utc))
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
            'created_at': self.created_at,
            'user_id': self.user_id,
        }


class Ingredient(db.Model):
    ingredient_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float)
    units = db.Column(db.Text(20))
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.recipe_id'), nullable=False)

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.save()

    def __repr__(self):
        return f'<Ingredient {self.name}>'


class Direction(db.Model):
    direction_id = db.Column(db.Integer, primary_key=True)
    step_number = db.Column(db.Integer, nullable=False)
    instruction = db.Column(db.Text, nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.recipe_id'), nullable=False)

    def __init__(self, step_number, instruction, recipe_id):
        self.step_number = step_number
        self.instruction = instruction
        self.recipe_id = recipe_id

    def __repr__(self):
        return f'<Direction {self.step_number}>'


class Favorite(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.recipe_id'), primary_key=True)
    is_favorite = db.Column(db.Boolean, default=True, nullable=False)

    def __init__(self, user_id, recipe_id, is_favorite=True):
        self.user_id = user_id
        self.recipe_id = recipe_id
        self.is_favorite = is_favorite

    def __repr__(self):
        return f'<Favorite user_id={self.user_id} recipe_id={self.recipe_id} is_favorite={self.is_favorite}>'


