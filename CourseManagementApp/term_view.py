from flask import (Blueprint, render_template, request, flash, redirect, url_for, abort)
from flask_login import login_required, current_user
from .dbmanager import get_db
from .exceptions import ObjectAlreadyExists, CannotFindObject
from .term import Term, TermForm
bp = Blueprint('term', __name__, url_prefix='/term/')
    
@bp.route('/form/', methods=['GET', 'POST'])
def add_term():
    if current_user.blocked:
        abort(401)
        
    form = TermForm()
    
    if request.method == 'POST' and form.validate_on_submit():
        new_term = Term(form.term_id.data)    
        try:
            get_db().add_term(new_term)
            flash('Term Added Successfully')
            return redirect(url_for('home.index'))
        except ObjectAlreadyExists as e:
            flash(str(e))
        except:
            flash('Cannot reach the database')
    return render_template('form_term.html', form=form)

@bp.route('/form/delete/<int:term_id>/')
@login_required
def delete_term(term_id):
    if current_user.blocked:
        abort(401)
        
    try:
        term = get_db().get_term(term_id)
        if term:
            get_db().del_term(term_id)
            flash('Term deleted succesfully')
        else:
            flash("Term does not exist")
    except Exception:
        flash('Database Error: Ensure term is not linked to any course')
    
    return redirect(url_for('home.index'))