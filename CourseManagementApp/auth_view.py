from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, send_from_directory, abort
from .user import SignupForm, LoginForm, Member
from werkzeug.security import check_password_hash, generate_password_hash
from .dbmanager import get_db
from flask_login import login_user, login_required, logout_user, current_user
from .exceptions import ObjectAlreadyExists, CannotFindObject
from datetime import datetime
import os

bp = Blueprint('auth',__name__,url_prefix='/auth/')

def get_image_path(email):
    image_path = os.path.join(current_app.config['IMAGE_PATH'], email)
    return image_path

@bp.route('/signup/', methods=['GET','POST'])
def signup():
    form = SignupForm()   
    if request.method == 'POST':
        # Check if all form requirements are met
        if form.validate_on_submit():
            # save file to instance folder in specific folder with email name
            file = form.avatar.data 
            if file:
                avatar_dir = get_image_path(form.email.data)
                os.makedirs(avatar_dir, exist_ok=True)
                avatar_path = os.path.join(avatar_dir, 'profile_pic.png')
                try:
                    file.save(avatar_path)
                except Exception:
                    flash('failed to save profile picture')
            today = datetime.today()
            # create user object
            user = Member(form.name.data, generate_password_hash(form.password.data), form.email.data, today, 0)
            try:
                get_db().add_user(user)
            except ObjectAlreadyExists as e:
                flash(str(e))
                return redirect(url_for('auth.signup'))
            except Exception:
                flash('Database Error')
                return redirect(url_for('home.index'))
            # if successful, redirect to login
            flash('Account Successfully Created.')
            if not current_user.is_authenticated:
                flash('Please Log In')
                return redirect(url_for('auth.login'))
            else:
                return redirect(url_for('admin.display_users'))
    return render_template('signup.html',form=form, user=None)

@bp.route('/login/', methods=['GET','POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        try:
            user = get_db().get_user_by_email(form.email.data)
        except CannotFindObject:
            flash('Invalid email or password')
        except Exception as e:
            flash('Database Error')
            user = None
        if user:
            if check_password_hash(user.password,form.password.data):
                if login_user(user,remember=form.remember_me.data):
                    return redirect(url_for('auth.get_profile',email=current_user.email))
            flash('Invalid email or password')
        else:
            flash('Invalid email or password')
    return render_template('login.html', form=form)

@bp.route('/profile_picture/<email>/profile_pic.png')
@login_required
def get_profile_picture(email):
    avatar_dir = get_image_path(email)
    return send_from_directory(avatar_dir, 'profile_pic.png')

@bp.route('/profile/<email>/', methods=['GET','POST'])
@login_required
def get_profile(email):
    try:
        user = get_db().get_user_by_email(email)
    except Exception:
        flash('Database Error')
    if request.method == 'POST':
        change_pwd(user.email)
    return render_template('profile.html',profile=user)

@bp.route('/logout/')
@login_required
def logout():
    logout_user()
    return render_template('logout.html')

@bp.route('/edit/<email>/', methods=['GET','POST'])
@login_required
def edit(email):
    form = SignupForm()
    if request.method == 'POST':
        form.email.data = email
        form.password.data = 'placeholder'
        if form.validate_on_submit():
            get_db().edit_user(form.name.data,email)
            file = form.avatar.data 
            if file:
                avatar_dir = get_image_path(form.email.data)
                os.makedirs(avatar_dir, exist_ok=True)
                avatar_path = os.path.join(avatar_dir, 'profile_pic.png')
                try:
                    file.save(avatar_path)
                except Exception:
                    flash('failed to save profile picture')
            return redirect(url_for('auth.get_profile',email=email))
    return render_template('signup.html',form=form, user=current_user)

@login_required
def change_pwd(email):
    if request.method == 'POST':
        old_pwd = request.form['old-pwd']
        new_pwd = request.form['new-pwd']

        try:
            user = get_db().get_user_by_email(email)
        except Exception:
            flash('Database Error')

        if check_password_hash(user.password,old_pwd):
            try:
                get_db().update_user_pwd(email,generate_password_hash(new_pwd))
            except Exception:
                flash('Database Error')
            flash('Password Updated')
            return redirect(url_for('auth.get_profile', email=email))
        flash('Invalid old password')

