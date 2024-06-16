from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_security.utils import send_mail
from datetime import datetime, timedelta
from .utils.decorators import logout_required
import secrets
from flask_mail import Message
from . import db, mail
from .models import User
from . import db
from .tokens import confirm_token, generate_token
from .email_utils import send_email

auth = Blueprint('auth', __name__)

@auth.route('/login')
@logout_required
def login():
    return render_template('login.html')


@auth.route('/login', methods=['POST'])
@logout_required
def login_post():
    # login code goes here
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.', 'danger')
        return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page

    login_user(user, remember=remember)

    # Check if there is a stored tournament_id in the session
 
    # if the above check passes, then we know the user has the right credentials
    return redirect(url_for('main.profile'))
@auth.route('/signup')
@logout_required
def signup():
    return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
@logout_required
def signup_post():


    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    surname=request.form.get('surname')
    user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

    if user: 
        flash('Email address already exists', category='login')
        return redirect(url_for('auth.signup'))
    
    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(email=email, name=name, surname=surname, password=generate_password_hash(password))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()
    token = generate_token(email)
    confirm_url = url_for("auth.confirm_email", token=token, _external=True)
    html = render_template("email.html", confirm_url=confirm_url)
    subject = "Please confirm your email"
    send_email(new_user.email, subject, html)

    login_user(new_user)

    flash("A confirmation email has been sent via email.", "success")
    return redirect(url_for("auth.inactive"))

@auth.route("/inactive")
@login_required
def inactive():
    if current_user.confirmed:
        return redirect(url_for("main.index"))
    return render_template("inactive.html")

@auth.route('/logout')
@login_required
def logout():
    return render_template('logout.html')

@auth.route('/logout', methods=['POST'])
@login_required
def logout_post():
    logout_user()
    flash('Logged out succesfully', category='info')
    return redirect(url_for('auth.login'))


@auth.route("/confirm/<token>")
@login_required
def confirm_email(token):
    if current_user.confirmed:
        flash("Account already confirmed.", "success")
        return redirect(url_for("main.index"))
    email = confirm_token(token)
    user = User.query.filter_by(email=current_user.email).first_or_404()
    if user.email == email:
        user.confirmed = True
        user.confirmed_at = datetime.now()
        db.session.add(user)
        db.session.commit()
        flash("You have confirmed your account. Thanks!", "success")
    else:
        flash("The confirmation link is invalid or has expired.", "danger")
    return redirect(url_for("main.index"))

@auth.route("/resend")
@login_required
def resend_confirmation():
    if current_user.confirmed:
        flash("Your account has already been confirmed.", "success")
        return redirect(url_for("main.index"))
    token = generate_token(current_user.email)
    confirm_url = url_for("auth.confirm_email", token=token, _external=True)
    html = render_template("email.html", confirm_url=confirm_url)
    subject = "Please confirm your email"
    send_email(current_user.email, subject, html)
    flash("A new confirmation email has been sent.", "success")
    return redirect(url_for("auth.inactive"))

from .email_utils import send_password_reset_email
from .tokens import confirm_reset_token
@auth.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            send_password_reset_email(user)
            flash('Password reset email sent. Check your inbox.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Email not found. Please check your email and try again.', 'danger')
    return render_template('forgot_password.html')

@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = confirm_reset_token(token)
    if email is None:
        flash('Invalid or expired token. Please try again.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    user = User.query.filter_by(email=email).first()
    if user is None:
        flash('User not found. Please try again.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password')
        user.password = generate_password_hash(password)
        db.session.add(user)
        db.session.commit()
        flash('Password reset successfully. You can now log in with your new password.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('reset_password.html')