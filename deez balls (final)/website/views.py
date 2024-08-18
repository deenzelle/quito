import os
from pathlib import Path
from PIL import Image
import secrets
from flask import Blueprint, render_template, request, abort, flash, redirect, url_for, jsonify
from flask_login import current_user, login_required
from .models import Post, User, Like, Comment
from .forms import UpdateAccountForm, RegistrationForm, PostForm
from . import db

# Create a Blueprint for views
views = Blueprint("views", __name__)

# Route for the home page and recommendations page


@views.route("/")
@views.route("/home")
def home():
    return render_template("home.html", user=current_user)


@views.route("/")
@views.route("/recommendations")
def locations():
    return render_template("recommendations.html", user=current_user)

# Route for the blog page, only accessible by logged-in users


@views.route("/blog")
@login_required
def blog():
    posts = Post.query.all()  # Retrieve all posts from the database
    return render_template("blog.html", user=current_user, posts=posts)

# Route to create a new post, only accessible by logged-in users


@views.route("/create-post", methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():  # Check if form data is valid and submitted
        title = form.title.data
        text = form.text.data
        # Create a new post object
        post = Post(title=title, text=text, author=current_user.id)
        db.session.add(post)  # Add the post to the database session
        db.session.commit()  # Commit the session to save the post to the database
        flash('Post created!', category='success')
        return redirect(url_for('views.blog'))  # Redirect to the blog page

    return render_template('create_post.html', form=form, user=current_user)

# Route to view posts by a specific user


@views.route("/posts/<username>")
@login_required
def posts(username):
    # Retrieve user by username
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('No user with that username exists.', category='error')
        return redirect(url_for('views.home'))

    # Retrieve all posts by the user
    posts = Post.query.filter_by(author=user.id).all()
    return render_template("posts.html", user=current_user, posts=posts, username=username)

# Route to delete a specific post, only accessible by logged-in users


@views.route("/delete-post/<id>")
@login_required
def delete_post(id):
    post = Post.query.filter_by(id=id).first()  # Retrieve post by ID
    if not post:
        flash('This post does not exist.', category='error')
    elif current_user.id != post.author:  # Check if current user is the author of the post
        flash('You do not have permission to delete this post.', category='error')
    else:
        db.session.delete(post)  # Delete the post from the database session
        db.session.commit()  # Commit the session to save the changes
        flash('Post deleted', category='success')
    return redirect(url_for('views.blog'))  # Redirect to the blog page

# Route to like or unlike a post, only accessible by logged-in users


@views.route("/like-post/<post_id>", methods=['POST'])
@login_required
def like(post_id):
    post = Post.query.filter_by(id=post_id).first()  # Retrieve post by ID
    # Check if user already liked the post
    like = Like.query.filter_by(
        author=current_user.id, post_id=post_id).first()
    if not post:
        return jsonify({'error': 'Post does not exist.'}, 400)
    elif like:
        db.session.delete(like)  # Unlike the post by deleting the like entry
        db.session.commit()
    else:
        # Create a new like entry
        like = Like(author=current_user.id, post_id=post_id)
        db.session.add(like)  # Add the like to the database session
        db.session.commit()
    # Return the number of likes and whether the current user has liked the post
    return jsonify({"likes": len(post.likes), "liked": current_user.id in map(lambda x: x.author, post.likes)})

# Route to create a comment on a post, only accessible by logged-in users


@views.route("/create-comment/<post_id>", methods=['POST'])
@login_required
def create_comment(post_id):
    text = request.form.get('text')  # Retrieve comment text from the form
    if not text:
        flash('Comment cannot be empty.', category='error')
    else:
        post = Post.query.filter_by(id=post_id).first()  # Retrieve post by ID
        if post:
            # Create a new comment object
            comment = Comment(
                text=text, author=current_user.id, post_id=post_id)
            db.session.add(comment)  # Add the comment to the database session
            db.session.commit()
        else:
            flash('Post does not exist.', category='error')
    return redirect(url_for('views.blog'))  # Redirect to the blog page

# Route to delete a comment, only accessible by logged-in users


@views.route("/delete-comment/<comment_id>")
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(
        id=comment_id).first()  # Retrieve comment by ID
    if not comment:
        flash('Comment does not exist.', category='error')
    # Check if current user is authorized to delete the comment
    elif current_user.id != comment.author and current_user.id != comment.post.author:
        flash('You do not have permission to delete this comment', category='error')
    else:
        # Delete the comment from the database session
        db.session.delete(comment)
        db.session.commit()

    return redirect(url_for('views.blog'))  # Redirect to the blog page

# Function to save a user's profile picture


def save_picture(form_picture):
    # Note to future denz: ALL FUTURE ITERATIONS OF QUITO BLOG MUST HAVE ITS OWN PATH
    # Path where profile pictures are stored
    path = Path("deez balls (final)\website\static\profile_pics")
    # Generate a random hex string for the picture filename
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(
        form_picture.filename)  # Get the file extension
    picture_fn = random_hex + f_ext  # Create a unique filename
    picture_path = os.path.join(path, picture_fn)  # Path to save the picture
    output_size = (125, 125)  # Resize picture to 125x125 pixels
    i = Image.open(form_picture)  # Open the image file
    i.thumbnail(output_size)  # Resize the image
    i.save(picture_path)  # Save the image to the specified path
    return picture_fn  # Return the filename of the saved picture

# Route to view and update user account details, only accessible by logged-in users


@views.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            # Save the new profile picture
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file  # Update user's profile picture
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()  # Commit the session to save changes
        flash('Your account has been updated!')
        # Redirect to the account page
        return redirect(url_for('views.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' +
                         current_user.image_file)  # URL for the profile picture
    return render_template('account.html', user=current_user, image_file=image_file, form=form)

# Route to update an existing post, only accessible by logged-in users


@views.route("/update-post/<id>", methods=['GET', 'POST'])
@login_required
def update_post(id):
    post = Post.query.filter_by(id=id).first()  # Retrieve post by ID
    if post.author != current_user.id:  # Check if current user is the author of the post
        abort(403)  # Abort with a 403 Forbidden error
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.text = form.text.data
        db.session.commit()  # Commit the session to save changes
        flash('Your Post Has Been Updated!', category='success')
        return redirect(url_for('views.blog'))  # Redirect to the blog page
    elif request.method == 'GET':
        form.title.data = post.title
        form.text.data = post.text
        # URL for the profile picture
        image_file = url_for(
            'static', filename='profile_pics/' + current_user.image_file)

    return render_template('update_post.html', form=form, user=current_user, post=post, image_file=image_file)
