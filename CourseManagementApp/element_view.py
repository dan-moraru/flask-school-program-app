from flask import (Blueprint, render_template, request, flash, redirect, url_for, abort)
from .dbmanager import get_db
from .exceptions import ObjectAlreadyExists
from .element import Element, ElementForm
from .course_view import get_course_by_id
from flask_login import login_required, current_user
bp = Blueprint('element', __name__, url_prefix='/element/')
    
@bp.route('/<int:id>/')
def get_element_by_id(id):
    try:
        element = get_db().get_element(id)
        courses = get_db().get_courses_of_element(id)
    except:
        flash('Cannot reach the database')
        return redirect(url_for('home.index'))
        
    if element is not None:
        return render_template('specific_element.html', element=element, courses=courses)
    else:
        flash('Specified element not found')
        abort(404)
        
@bp.route('/reference/')
def get_elements():
    try:
        elements = get_db().get_elements()
        course_element_groupings = get_db().get_course_element_groupings()
    except:
        flash('Cannot reach the database')
        return redirect(url_for('home.index'))
        
    return render_template('elements_reference.html', elements=elements, course_element_groupings=course_element_groupings)

@bp.route('/form/add/', methods=['GET', 'POST'])
@login_required
def add_element():
    if current_user.blocked:
        abort(401)  
    form = ElementForm()

    try:
        competencies = get_db().get_competencies()
    except:
        flash('Cannot reach the database')
        return redirect(url_for('home.index')) 
    
    for competency in competencies:
        form.competency_id.choices.append(competency.competency_id)

    if request.method == 'POST' and form.validate_on_submit():
        try:
            competency_elements = get_db().get_elements_of_competency(form.competency_id.data)
        except:
            flash('Cannot connect to the database. Try again later')
            return redirect(url_for('home.index'))
        
        for each_element in competency_elements:
            if each_element.element.upper() == form.element.data.upper():
                flash('Selected Competency already contains an element with that name')
                return redirect(url_for('home.index'))
        
        new_element = Element(form.element_order.data, form.element.data, form.element_criteria.data, form.competency_id.data)
         
        try:
            get_db().add_element(new_element)
            new_element_retrieved = get_db().get_latest_element()
            flash('Element Added Successfully')
            return redirect(url_for('element.get_element_by_id', id=new_element_retrieved.element_id))
        except ObjectAlreadyExists as e:
            flash(str(e))
        except:
            flash('Cannot reach the database')
        return redirect(url_for('home.index'))
    return render_template('form_element.html', form=form, element=None, action='Add')

@bp.route('/form/edit/<int:element_id>/', methods=['GET','POST'])
@login_required
def edit_element(element_id):
    if current_user.blocked:
        abort(401)
        
    form = ElementForm()
    try:
        element = get_db().get_element(element_id)
        if element:
            competencies = get_db().get_competencies()
        else:
            flash('Element does not exist')
            return redirect(url_for('home.index'))
    except Exception:
        flash('Database Error')
        return redirect(url_for('home.index'))
    
    for comp in competencies:
        form.competency_id.choices.append(comp.competency_id)
    
    if request.method == 'POST':
        if form.validate_on_submit():
            updated_element = Element(form.element_order.data,form.element.data,form.element_criteria.data, form.competency_id.data)
            
            try:
                competency_elements = get_db().get_elements_of_competency(form.competency_id.data)
            except:
                flash('Cannot connect to the database. Try again later')
                return redirect(url_for('home.index'))
            
            updated_element.element_id = element_id

            try:
                get_db().edit_element(updated_element)
                flash('Element Updated')
                return redirect(url_for('element.get_element_by_id', id=updated_element.element_id))
            except Exception:
                flash('Database Error')
                return redirect(url_for('home.index'))

    return render_template('form_element.html', form=form, element=element, action='Edit')

@bp.route('/form/delete/<int:element_id>/')
@login_required
def delete_element(element_id):
    if current_user.blocked:
        abort(401)

    message = '' 
    try:
        element = get_db().get_element(element_id)
        if element:
            competency_id = element.competency_id
            competency_elements = get_db().get_elements_of_competency(competency_id)
            
            last_element = False
            if len(competency_elements) == 1:
                last_element = True
            
            get_db().del_courses_of_element(element_id)
            get_db().del_element(element_id)
            message += 'Element deleted succesfully, as well as its course-element links.'
        else:
            flash('Element cannot be found')
            return redirect(url_for('home.index'))
        
    except Exception:
        flash('Database Error')
        return redirect(url_for('home.index'))
        
    if last_element:
        try:
            get_db().del_competency(competency_id)
            flash(f'{message} and deleted element\'s associated competency has no more elements. Competency deleted.')
        except:
            flash(f'Competency of deleted element ({competency_id}) has no more elements. Either add some or delete the competency')
            return redirect(url_for('competency.get_competency_by_id', id=competency_id))
    else:
        flash(message)
    
    return redirect(url_for('element.get_elements'))