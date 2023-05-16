from flask import Blueprint, render_template, abort, flash, request, redirect, url_for
from flask_login import login_required, current_user
from .dbmanager import get_db

bp = Blueprint('admin',__name__,url_prefix='/admin/')

@bp.route('/user-dashboard/', methods=['GET','POST'])
@login_required
def display_users():
    if current_user.access_group == 3:
        try:
            users = get_db().get_users()
        except Exception:
            flash('Database Error')
    else:
        try:
            users = get_db().get_members()
        except Exception:
            flash('Database Error')
    return render_template('user_dashboard.html', users=users)

@bp.route('/user-edit/<email>/', methods=['GET','POST'])
@login_required
def edit_user(email):
    form = GroupForm()
    if current_user.access_group == 3:
        form.choice_access_group.choices.extend(['Member','Admin','Server Admin'])
    elif current_user.access_group == 2:
        form.choice_access_group.choices.extend(['Member','Admin'])
    try:
        user = get_db().get_user_by_email(email)
    except Exception:
        flash('Database Error')
    if request.method == 'POST' and form.validate_on_submit:
        try:
            get_db().edit_user_group(form.choice_access_group.data, user.email)
        except Exception:
            flash('Database Error')
        return redirect(url_for('admin.display_users'))
    return render_template('user_form.html', user=user, form=form)

@bp.route('/user-delete/<email>/')
def delete_user(email):
    if current_user.access_group == 1 or current_user.blocked:
        abort(401)
    try:
        get_db().del_user(email)
    except Exception:
        flash('Database Error')

    return redirect(url_for('admin.display_users'))

@bp.route('/user-block/<email>/')
def block_user(email):
    if current_user.access_group == 1 or current_user.blocked:
        abort(401)
    try:
        get_db().block_user_db(email)
    except Exception:
        flash('Database Error')
    return redirect(url_for('admin.display_users'))

from flask_wtf import FlaskForm
from wtforms import SelectField, StringField

class GroupForm(FlaskForm):
    choice_access_group = SelectField('New Group: ', choices=[])