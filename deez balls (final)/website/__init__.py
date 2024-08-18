from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    # Create and configure the Flask application
    app = Flask(__name__)
    # Secret key for session management and security
    app.config['SECRET_KEY'] = "iP8BYFmrKH"
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    from .models import User, Post

    # Create the database tables if they don't exist
    with app.app_context():
        db.create_all()  # Create database tables based on the models
        print("Created database!")

    # Initialize the LoginManager for user session management
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    # Define the callback function to load a user from the database
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))  # Fetch user by ID

    return app
