from flask import (Blueprint, render_template, request, flash, abort, redirect, url_for)
from .dbmanager import get_db
from .exceptions import ObjectAlreadyExists, CannotFindObject
from flask_login import current_user
bp = Blueprint('course_elements', __name__, url_prefix='/course_elements/form/')
    
@bp.route('/', methods=['GET', 'POST'])
def add_course_elements():
    if current_user.blocked:
        abort(401)
    try:
        elements = get_db().get_elements()
        competencies = get_db().get_competencies()
        courses = get_db().get_courses()
        terms = get_db().get_terms()
    except:
        flash('Cannot reach the database')
        return redirect(url_for('home.index'))
        
    if request.method == 'POST':
        course_id = request.form['course_id']
        element_id = request.form['element_id']
        element_hours = request.form['element_hours'] 
        try:
            get_db().add_course_elements(course_id, element_id, element_hours)
            flash('Course-Element connection created. Ensure total course-element hours match expected total course hours')
        except ObjectAlreadyExists as e:
            flash('Course-Element link already exists.')
        except:
            flash('Cannot reach the database')
    return render_template('form_course_elements.html', elements=elements, competencies=competencies, courses=courses, terms=terms)

@bp.route('/edit/', methods=['GET', 'POST'])
def edit_course_elements():
    try:
        course_element_groupings = get_db().get_course_element_groupings()
    except:
        flash('Cannot reach the database')
        return redirect(url_for('home.index'))
        
    if request.method == 'POST':
        course_element_pairing = request.form['grouping'].split('_')
        course_id = course_element_pairing[0]
        element_id = int(course_element_pairing[1])
        new_hours = request.form['element_hours'] 
        try:
            get_db().edit_course_element_hours(course_id, element_id, new_hours)
            course_element_groupings = get_db().get_course_element_groupings()
            
            exists = False
            for grouping in course_element_groupings:
                if grouping[0] == course_id and grouping[2] == element_id:
                    exists = True
                    break
            if not exists:
                flash('Course-element link does not exist')
                return redirect(url_for('home'))
            
            flash('Course-Element link updated with new hours. Ensure total course-element hours match expected total course hours')
            return redirect(url_for('home.index'))
        except CannotFindObject as e:
            flash(str(e))
        except:
            flash('Cannot reach the database')
    return render_template('form_course_elements_edit.html', course_element_groupings=course_element_groupings)

@bp.route('/delete/', methods=['GET', 'POST'])
def delete_course_elements():
    try:
        course_element_groupings = get_db().get_course_element_groupings()
    except:
        flash('Cannot reach the database')
        return redirect(url_for('home.index'))
        
    if request.method == 'POST':
        course_element_pairing = request.form['grouping'].split('_')
        course_id = course_element_pairing[0]
        element_id = int(course_element_pairing[1])
        
        exists = False
        for grouping in course_element_groupings:
            if grouping[0] == course_id and grouping[2] == element_id:
                exists = True
                break
        if not exists:
            flash('Course-element link does not exist')
            return redirect(url_for('home.index'))
        
        try:
            get_db().del_course_element_pairing(course_id, element_id)
            flash('Course-Element link deleted')
        except CannotFindObject as e:
            flash(str(e))
        except:
            flash('Cannot reach the database')
        return redirect(url_for('home.index'))
    
    return render_template('form_course_elements_delete.html', course_element_groupings=course_element_groupings)