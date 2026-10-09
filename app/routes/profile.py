from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, EqualTo
from app import db
from app.utils import save_uploaded_file

profile_bp = Blueprint('profile', __name__)


class EditProfileForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=120)])
    phone = StringField('Phone', validators=[Optional(), Length(max=30)])
    avatar = FileField('Profile Picture', validators=[
        Optional(),
        FileAllowed(['png', 'jpg', 'jpeg', 'gif', 'webp'], 'Images only.')
    ])
    submit = SubmitField('Save Changes')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(), Length(min=8, message='Password must be at least 8 characters.')
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(), EqualTo('new_password', message='Passwords must match.')
    ])
    submit = SubmitField('Change Password')


@profile_bp.route('/')
@login_required
def view():
    return render_template('profile/view.html', user=current_user)


@profile_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.full_name = form.full_name.data.strip()
        current_user.phone = form.phone.data.strip() if form.phone.data else None
        avatar_file = request.files.get('avatar')
        if avatar_file and avatar_file.filename:
            saved = save_uploaded_file(avatar_file, subfolder='avatars')
            if saved:
                current_user.avatar = saved
            else:
                flash('Invalid image file. Avatar was not updated.', 'warning')
        try:
            db.session.commit()
            flash('Profile updated successfully.', 'success')
            return redirect(url_for('profile.view'))
        except Exception:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'danger')
    return render_template('profile/edit.html', form=form)


@profile_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('Current password is incorrect.', 'danger')
            return render_template('profile/change_password.html', form=form)
        if form.new_password.data == form.current_password.data:
            flash('New password must differ from current.', 'warning')
            return render_template('profile/change_password.html', form=form)
        current_user.set_password(form.new_password.data)
        try:
            db.session.commit()
            flash('Password changed successfully.', 'success')
            return redirect(url_for('profile.view'))
        except Exception:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'danger')
    return render_template('profile/change_password.html', form=form)
