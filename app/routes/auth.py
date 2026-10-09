"""
auth.py – Authentication Blueprint for CampusFind.

Handles user registration, login and logout.
"""

from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length

from app import db
from app.models import User
from app.utils import log_activity

auth_bp = Blueprint('auth', __name__)


# ─────────────────────────────────────────────
#  FORMS
# ─────────────────────────────────────────────

class RegistrationForm(FlaskForm):
    """Form for new user registration."""

    full_name = StringField(
        'Full Name',
        validators=[
            DataRequired(message='Full name is required.'),
            Length(min=2, max=120, message='Name must be between 2 and 120 characters.'),
        ]
    )
    email = StringField(
        'Email Address',
        validators=[
            DataRequired(message='Email address is required.'),
            Email(message='Please enter a valid email address.'),
            Length(max=120),
        ]
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message='Password is required.'),
            Length(min=8, message='Password must be at least 8 characters long.'),
        ]
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(message='Please confirm your password.'),
            EqualTo('password', message='Passwords must match.'),
        ]
    )
    submit = SubmitField('Create Account')


class LoginForm(FlaskForm):
    """Form for user login."""

    email = StringField(
        'Email Address',
        validators=[
            DataRequired(message='Email address is required.'),
            Email(message='Please enter a valid email address.'),
        ]
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message='Password is required.'),
        ]
    )
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


# ─────────────────────────────────────────────
#  ROUTES
# ─────────────────────────────────────────────

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user account."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()

    if form.validate_on_submit():
        # Check for duplicate email
        existing_user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if existing_user:
            flash('An account with that email address already exists. Please log in.', 'warning')
            return render_template('auth/register.html', form=form)

        # Create the new user
        user = User(
            full_name=form.full_name.data.strip(),
            email=form.email.data.strip().lower(),
        )
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        log_activity('user_registered', details=f'New user: {user.email}', user_id=user.id)
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('dashboard.index'))

    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Authenticate an existing user."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()

        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password. Please try again.', 'danger')
            return render_template('auth/login.html', form=form)

        if not user.is_active:
            flash('Your account has been deactivated. Please contact support.', 'danger')
            return render_template('auth/login.html', form=form)

        # Log the user in
        login_user(user, remember=form.remember_me.data)

        # Update last login timestamp
        user.last_login = datetime.utcnow()
        db.session.commit()

        log_activity('user_login', details=f'User logged in: {user.email}', user_id=user.id)
        flash(f'Welcome back, {user.full_name}!', 'success')

        # Honour the 'next' parameter from login_required redirects
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)

        # Route admins to the admin dashboard
        if user.is_admin:
            return redirect(url_for('admin.dashboard'))

        return redirect(url_for('dashboard.index'))

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """Log the current user out."""
    log_activity('user_logout', details=f'User logged out: {current_user.email}', user_id=current_user.id)
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))
