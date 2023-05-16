from flask import (Blueprint, render_template, request, flash, redirect, url_for, abort)
from .dbmanager import get_db
from .exceptions import ObjectAlreadyExists
from .competency import Competency, CompetencyForm
from flask_login import login_required, current_user
from .element import Element
bp = Blueprint('competency', __name__, url_prefix='/competency/')
    
@bp.route('/form/add/', methods=['GET', 'POST'])
@login_required
def add_competency():
    if current_user.blocked:
        abort(401)
    form = CompetencyForm()
    
    if request.method == 'POST' and form.validate_on_submit():
        if form.competency_type.data:
            competency_type = 'Mandatory'
        else:
            competency_type = 'Optional'
        new_competency = Competency(form.competency_id.data, form.competency.data, form.competency_achievement.data, competency_type)
        new_element = Element(form.element_order.data, form.element.data, form.element_criteria.data, form.competency_id.data)
         
        try:
            get_db().add_competency(new_competency)
            competency_added = True
            get_db().add_element(new_element)
            flash('Competency Added and New Element Associated. You may create and associate more elements.')
            return redirect(url_for('competency.get_competency_by_id', id=new_competency.competency_id))
        except ObjectAlreadyExists as e:
            flash(str(e))
        except:
            flash('Cannot reach the database')
            if competency_added:
                try:
                    get_db().del_competency(new_competency.competency_id)
                    flash('New competency was not added. Please try again.')
                except:
                    flash('Cannot reach the database. Please delete the new competency and add it again, or associate at least one element to it')
        
    return render_template('form_competency.html', form=form, competency=None, element=None, action='Add')

@bp.route('/reference/')
def get_competencies():
    try:
        competencies = get_db().get_competencies()
        elements = get_db().get_elements()
        course_competency_groupings = get_db().get_course_competency_groupings()
    except:
        flash('Cannot reach the database')
        return redirect(url_for('home.index'))
    
    return render_template('competencies_reference.html', competencies=competencies, elements=elements, course_competency_groupings=course_competency_groupings)

@bp.route('/<id>/')
def get_competency_by_id(id):
    try:
        competency = get_db().get_competency(id)
        competency_elements = get_db().get_elements_of_competency(id)
        course_competency_groupings = get_db().get_course_competency_groupings()
    except:
        flash('Cannot reach the database')
        return redirect(url_for('home.index'))
        
    if competency is not None and competency_elements is not None:
        return render_template('specific_competency.html', competency=competency, competency_elements=competency_elements, course_competency_groupings=course_competency_groupings)
    else:
        flash('Specified competency and related information not found')
        abort(404)

@bp.route('/form/edit/<comp_id>', methods=['GET','POST'])
@login_required
def edit_competency(comp_id):
    if current_user.blocked:
        abort(401)
    form = CompetencyForm()
    try:
        competency = get_db().get_competency(comp_id)
        if not competency:
            flash('Competency does not exist')
            return redirect(url_for('home.index'))
    except Exception:
        flash('Database Error')
        return redirect(url_for('home.index'))
    
    form.competency_id.data = competency.competency_id
    form.competency_id(disabled=True)
    form.element.data = 'placeholder'
    form.element_criteria.data = 'placeholder'
    form.element_order.data = 1
    
    if request.method == 'POST':
        if form.validate_on_submit():
            if form.competency_type.data:
                competency_type = 'Mandatory'
            else:
                competency_type = 'Optional'  
            updated_competency = Competency(comp_id,form.competency.data,form.competency_achievement.data,competency_type)
            try:
                get_db().edit_competency(updated_competency)
                flash('Competency Successfully Updated')
                return redirect(url_for('competency.get_competency_by_id', id=updated_competency.competency_id))
            except Exception:
                flash('Database Error')
                return redirect(url_for('home.index'))
    return render_template('form_competency.html', form=form, competency=competency, action='Edit')

@bp.route('/form/delete/<comp_id>/')
@login_required
def delete_competency(comp_id):
    if current_user.blocked:
        abort(401)
    try:
        comp = get_db().get_competency(comp_id)
        if comp:
            get_db().del_competency(comp_id)
            flash('Competency deleted succesfully')
            return redirect(url_for('competency.get_competencies'))
        else:
            flash('Competency does not exist')
    except Exception:
        flash('Database Error: Ensure competency is not linked to any elements')
    
    return redirect(url_for('home.index'))