from flask import Blueprint, render_template, redirect, url_for, request, flash
from . import db
from .models import User
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .forms import RegistrationForm

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=['GET', 'POST'])
def login():
    # Handle POST request to log in the user
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        # Check if the user exists and if the password is correct
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again', category='error')
        else:
            flash('Email does not exist.', category='error')

    # Render the login page for GET requests
    return render_template("login.html", user=current_user)


@auth.route("/signup", methods=['GET', 'POST'])
def sign_up():
    # Redirect authenticated users to home page
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = RegistrationForm()  # Create a registration form instance
    if form.validate_on_submit():
        # Hash the password and create a new user
        hashed_password = generate_password_hash(
            form.password.data, method='scrypt:32768:8:1')
        user = User(username=form.username.data,
                    email=form.email.data, password=hashed_password)

        # Add and commit the new user to the database
        db.session.add(user)
        db.session.commit()

        flash("Your account has been created! You can now log in", 'success')
        return redirect(url_for('auth.login'))

    # Render the signup page with the form
    return render_template('signup.html', form=form, user=current_user)


@auth.route("/logout")
@login_required
def logout():
    # Log out the user and redirect to the login page
    logout_user()
    return redirect(url_for("auth.login"))
