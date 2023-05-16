from flask import (Blueprint, render_template, request, flash, redirect, url_for, abort)
from .dbmanager import get_db
from .exceptions import ObjectAlreadyExists, CannotFindObject
from .course import Course, CourseForm
from flask_login import login_required, current_user
bp = Blueprint('course', __name__, url_prefix='/course/')

@bp.route('/<id>/')
def get_course_by_id(id):
    try:
        course = get_db().get_course(id)
        course_competencies = get_db().get_competencies_of_course(id)
        course_elements = get_db().get_elements_of_course(id)
        course_domain = get_db().get_domain_of_course(id)
        course_element_hours = get_db().get_course_element_hours(id)
    except:
        flash('Cannot reach the database')
        return redirect(url_for('home.index'))
    
    total_element_hours = 0
    for element_hours in course_element_hours:
        total_element_hours += element_hours[1]
        
    if course is not None and course_competencies is not None and course_elements is not None and course_domain is not None and course_element_hours is not None:
        return render_template('specific_course.html', course=course, course_competencies=course_competencies, course_elements=course_elements, course_domain=course_domain, course_element_hours=course_element_hours, total_element_hours=total_element_hours)
    else:
        flash('Specified course and related information not found')
        abort(404)
    
@bp.route('/form/add/', methods=['GET', 'POST'])
@login_required
def add_course():
    if current_user.blocked:
        abort(401)
        
    form = CourseForm()
    try:
        terms = get_db().get_terms()
        domains = get_db().get_domains()
    except:
        flash('Cannot reach the database')
        return redirect(url_for('home.index'))
    
    for term in terms: 
        form.term_id.choices.append(term.term_id)
    for domain in domains:
        form.domain.choices.append(domain.domain)
    
    if request.method == 'POST' and form.validate_on_submit():
        for domain in domains:
            if form.domain.data == domain.domain:
                form.domain.data = domain.domain_id
        new_course = Course(form.course_id.data, form.course_title.data, form.theory_hours.data, form.lab_hours.data, form.work_hours.data, form.description.data, form.domain.data, form.term_id.data)
        try:
            get_db().add_course(new_course)
            flash('Course Added Successfully')
            return redirect(url_for('course.get_course_by_id', id=new_course.course_id))
        except ObjectAlreadyExists as e:
            flash(str(e))
        except:
            flash('Cannot reach the database')
    return render_template('form_course.html', form=form, course=None, domain=None, action='Add')

@bp.route('/form/edit/<course_id>/', methods=['GET','POST'])
@login_required
def edit_course(course_id):
    if current_user.blocked:
        abort(401)
        
    form = CourseForm()
    
    try:
        course = get_db().get_course(course_id)
        if course:
            terms = get_db().get_terms()
            domains = get_db().get_domains()
            domain = get_db().get_domain_of_course(course_id)
        else:
            flash('Course does not exist')
            return redirect(url_for('home.index'))
    except Exception:
        flash('Database Error')
        return redirect(url_for('home.index'))
    
    for term in terms: 
        form.term_id.choices.append(term.term_id)
    for each_domain in domains:
        form.domain.choices.append(each_domain.domain)
    form.course_id.data = course.course_id
    form.course_id(disabled=True)
    
    if request.method == 'POST':
        if form.validate_on_submit():
            for domain in domains:
                if form.domain.data == domain.domain:
                    domain_id = domain.domain_id
                    
            updated_course = Course(course.course_id, form.course_title.data, form.theory_hours.data, form.lab_hours.data, form.work_hours.data, form.description.data, domain_id, form.term_id.data)
            try:
                get_db().edit_course(updated_course)
                flash('Course Updated Successfully')
            except Exception as e:
                flash(f'Database Error: {e}')
                return(redirect(url_for('home.index')))
                
            return redirect(url_for('course.get_course_by_id', id=form.course_id.data))
        
    return render_template('form_course.html', form=form, course=course, domain=domain, action='Edit')

@bp.route('/form/delete/<course_id>/')
@login_required
def delete_course(course_id):
    if current_user.blocked:
        abort(401)
        
    try:
        course = get_db().get_course(course_id)
        if course:
            get_db().del_elements_of_course(course_id)
            get_db().del_course(course_id)
            flash('Course deleted succesfully, as well as its course-element links.')
        else:
            flash('Course does not exist')
    except Exception:
        flash('Database Error')
    
    return redirect(url_for('home.index'))