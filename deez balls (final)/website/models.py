from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

# Model representing users in the application


class User(db.Model, UserMixin):
    # Unique identifier for each user
    id = db.Column(db.Integer, primary_key=True)
    # User's email, must be unique
    email = db.Column(db.String(150), unique=True)
    # User's username, must be unique
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))  # User's password (hashed)
    image_file = db.Column(db.String(20), nullable=False,
                           default='default.jpg')  # Profile image file name
    # Timestamp when the user account was created
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    posts = db.relationship('Post', backref='user', passive_deletes=True)
    likes = db.relationship('Like', backref='user', passive_deletes=True)
    comments = db.relationship('Comment', backref='user', passive_deletes=True)

# Model representing posts created by users


class Post(db.Model):
    # Unique identifier for each post
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)  # Title of the post
    text = db.Column(db.Text, nullable=False)  # Content of the post
    # Timestamp when the post was created
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    author = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete='CASCADE'), nullable=False)
    likes = db.relationship('Like', backref='post', passive_deletes=True)
    comments = db.relationship('Comment', backref='post', passive_deletes=True)

# Model representing likes on posts by users


class Like(db.Model):
    # Unique identifier for each like
    id = db.Column(db.Integer, primary_key=True)
    # Timestamp when the like was created
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    author = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete='CASCADE'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey(
        'post.id', ondelete='CASCADE'), nullable=False)

# Model representing comments on posts by users


class Comment(db.Model):
    # Unique identifier for each comment
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)  # Content of the comment
    # Timestamp when the comment was created
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    author = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete='CASCADE'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey(
        'post.id', ondelete='CASCADE'), nullable=False)
