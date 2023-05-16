from flask import Flask, Blueprint, request, url_for, make_response
from .dbmanager import get_db
from .course import Course
from .element import Element
import math

bp = Blueprint('course_api', __name__, url_prefix = '/api/v1')

@bp.route('/courses', methods=['GET', 'POST'])
def courses():
    try:
        total_courses = get_db().get_courses()
        terms = get_db().get_terms()
        domains = get_db().get_domains()
    except Exception as e:
        error_infoset = {'id': 'Database Error',
                         'description': 'Unable to connect to the database. Please try again later.'}
        return make_response(error_infoset, 500)
    
    if request.method == 'POST':
        course_json = request.json
        
        if course_json:
            try:
                new_course = Course.from_json(course_json)
            except:
                error_infoset = {'id': 'Data Error',
                         'description': 'Data must contain complete course information, and formatted as dictionary object'}
                return make_response(error_infoset, 400)
            
            for course in total_courses:
                if course.course_id == new_course.course_id:
                    error_infoset = {'id': 'Data Error',
                         'description': 'Specified course id already exists'}
                    return make_response(error_infoset, 400)
                
            valid_term = False
            for term in terms:
                if new_course.term_id == term.term_id:
                    valid_term = True
                    break
            if not valid_term:
                error_infoset = {'id': 'Data Error',
                        'description': 'Specified term id does not exist'}
                return make_response(error_infoset, 400)
                
            valid_domain = False
            for domain in domains:
                if new_course.domain_id == domain.domain_id:
                    valid_domain = True
                    break      
            if not valid_domain:
                error_infoset = {'id': 'Data Error',
                        'description': 'Specified domain id does not exist'}
                return make_response(error_infoset, 400) 
            
            try:
                get_db().add_course(new_course)
                infoset = {'id': 'Request Complete',
                           'description': 'New course resource created'}
                resp = make_response(infoset, 201)
                resp.headers['Location'] = url_for('course_api.course_by_id', course_id=new_course.course_id)
                return resp
            except Exception as e:
                error_infoset = {'id': 'Database Error',
                        'description': 'Unable to connect to the database. Please try again later.'}
                return make_response(error_infoset, 500)
                    
        
    elif request.method == 'GET':
        page_number = 1
        page_size = 50
        if request.args:
            page = request.args.get('page')
            if page:
                page_number = int(page)
                max_page = math.ceil(len(total_courses) / float(page_size))
                if page_number < 1 or page_number > max_page:
                    error_infoset = {'id' : 'Invalid Page Number',
                                 'description': f'Page number must be from 1, up to a maximum of {max_page}'}
                    return make_response(error_infoset, 404)
    
    try:
        courses, previous_page, next_page = get_db().get_courses_for_api(page_size, page_number=page_number)
    except Exception as e:
        error_infoset = {'id': 'Database Error',
                    'description': 'Unable to connect to the database. Please try again later.'}
        return make_response(error_infoset, 500)
    
    if previous_page is not None:
        previous_page = url_for('course_api.courses', page=previous_page)
    if next_page is not None:
        next_page = url_for('course_api.courses', page=next_page)
    current_page = url_for('course_api.courses', page=page_number)
    
    count = len(total_courses)
    json = {'count': count, 'current_page': current_page, 'previous_page': previous_page, 'next_page': next_page, 'results': [course.to_json() for course in courses]}
    return make_response(json, 200)

@bp.route('courses/<course_id>', methods=['GET', 'PUT', 'DELETE'])
def course_by_id(course_id):
    try:
        course = get_db().get_course(course_id)
        courses = get_db().get_courses()
        terms = get_db().get_terms()
        domains = get_db().get_domains()
    except Exception as e:
        error_infoset = {'id': 'Database Error',
                         'description': 'Unable to connect to the database. Please try again later.'}
        return make_response(error_infoset, 500)
    
    if request.method == 'PUT':
        course_json = request.json
        
        if course_json:
            try:
                new_course = Course.from_json(course_json)
            except:
                error_infoset = {'id': 'Data Error',
                         'description': 'Data must contain complete course information, and formatted as dictionary object'}
                return make_response(error_infoset, 400)
            
            for term in terms:
                if new_course.term_id == term.term_id:
                    break
                else:
                    error_infoset = {'id': 'Data Error',
                         'description': 'Specified term id does not exist'}
                    return make_response(error_infoset, 400)
                
            for domain in domains:
                if new_course.domain_id == domain.domain_id:
                    break
                else:
                    error_infoset = {'id': 'Data Error',
                         'description': 'Specified domain id does not exist'}
                    return make_response(error_infoset, 400)
            
            for course in courses:
                if course.course_id == new_course.course_id:
                    try:
                        get_db().edit_course(new_course)
                        resp = make_response({'id': 'Request Complete', 'description': 'Update Course Request Complete'}, 201)
                        resp.headers['Location'] = url_for('course_api.course_by_id', course_id=course_id)
                        return resp
                    except Exception as e:
                        error_infoset = {'id': 'Database Error',
                         'description': 'Unable to connect to the database. Please try again later.'}
                        return make_response(error_infoset, 500)
            
            try:
                get_db().add_course(new_course)
                resp = make_response({'id': 'Request Complete', 'description': 'Add Course Request Complete'}, 201)
                resp.headers['Location'] = url_for('course_api.course_by_id', course_id=new_course.course_id)
                return resp
            except Exception as e:
                error_infoset = {'id': 'Database Error',
                        'description': 'Unable to connect to the database. Please try again later.'}
                return make_response(error_infoset, 500)
                
    elif request.method == 'DELETE':
        if course is None:
            error_infoset = {'id': 'Data Error',
                         'description': 'Specified course id does not exist'}
            return make_response(error_infoset, 400)
        
        try:
            get_db().del_course(course_id)
            return make_response({'id': 'Deleted', 'description': 'Requested course resource deleted'}, 204)
        except Exception as e:
            error_infoset = {'id': 'Database Error',
                         'description': 'Unable to connect to the database. Please try again later.'}
            return make_response(error_infoset, 500)
    
    elif request.method == 'GET':
        if course is None:
            error_infoset = {'id' : 'Not Found',
                                 'description': 'The specified course could not be found. Make sure it was entered correctly, or try again later.'}
            return make_response(error_infoset, 404)
        
        json_course = course.to_json()
        json_course['url'] = url_for('course_api.course_by_id', course_id=course_id)
        return make_response(json_course, 200)

## Note that it is meaningless to make a POST request to this route because competencies aren't linked directly to courses. Although it will work,
## them not being linked means you will not get that competency when making a GET request afterwards. Courses are linked directly to elements.
## It's still meaningful to view the connection between courses and competencies, due secondarily to the connected elements.

@bp.route('/courses/<course_id>/competencies', methods=['GET'])
def course_competencies(course_id):
    try:
        total_course_competencies = get_db().get_competencies_of_course(course_id)
    except Exception as e:
        error_infoset = {'id': 'Database Error',
                         'description': 'Unable to connect to the database. Please try again later.'}
        return make_response(error_infoset, 500)
    
    if request.method == 'GET':
        if len(total_course_competencies) == 0:
            error_infoset = {'id' : 'Not Found',
                                 'description': 'The specified course could not be found. Make sure it was entered correctly, or try again later.'}
            return make_response(error_infoset, 404) 
        
        page_number = 1
        page_size = 50
        if request.args:
            page = request.args.get('page')
            if page:
                page_number = int(page)
                max_page = math.ceil(len(total_course_competencies) / float(page_size))
                if page_number < 1 or page_number > max_page:
                    error_infoset = {'id' : 'Invalid Page Number',
                                 'description': f'Page number must be from 1, up to a maximum of {max_page}'}
                    return make_response(error_infoset, 404)
                
    try:
        competencies, previous_page, next_page = get_db().get_course_competencies_for_api(course_id, page_size, page_number=page_number)
    except Exception as e:
        error_infoset = {'id': 'Database Error',
            'description': 'Unable to connect to the database. Please try again later.'}
        return make_response(error_infoset, 500)
    
    if previous_page is not None:
        previous_page = url_for('course_api.course_competencies', course_id=course_id, page=previous_page)
    if next_page is not None:
        next_page = url_for('course_api.course_competencies', course_id=course_id, page=next_page)
    current_page = url_for('course_api.course_competencies', course_id=course_id, page=page_number)
    
    count = len(total_course_competencies)
    json = {'count': count, 'current_page': current_page, 'previous_page': previous_page, 'next_page': next_page, 'results': [competency.to_json() for competency in competencies]}
    return make_response(json, 200)

## Due to the same reason as the above route, PUT requests are meaningless due to the lack of direct connection between courses and competencies.
## Likewise, delete has the potential to fail if a course isn't linked to a competency via any element. 

@bp.route('/courses/<course_id>/competencies/<competency_id>', methods=['GET'])
def course_competency_by_id(course_id, competency_id):
    try:
        competency = get_db().get_competency(competency_id)
        course = get_db().get_course(course_id)
    except Exception as e:
        error_infoset = {'id': 'Database Error',
                         'description': 'Unable to connect to the database. Please try again later.'}
        return make_response(error_infoset, 500)
                
    if request.method == 'GET':
        if competency is None or course is None:
            error_infoset = {'id' : 'Not Found',
                                 'description': 'The specified course or competency could not be found. Make sure each was entered correctly, or try again later.'}
            return make_response(error_infoset, 404)
        
        json_competency = competency.to_json()
        json_competency['url'] = url_for('course_api.course_competency_by_id', course_id=course_id, competency_id=competency_id)
        return make_response(json_competency, 200)
    
@bp.route('/courses/<course_id>/competencies/<competency_id>/elements', methods=['GET', 'POST'])
def course_elements(course_id, competency_id):
    try:
        total_competency_elements = get_db().get_elements_of_competency(competency_id)
        course = get_db().get_course(course_id)
        total_course_elements = get_db().get_elements_of_course(course_id)
        course_competency = get_db().get_competency(competency_id)
    except Exception as e:
        error_infoset = {'id': 'Database Error',
                         'description': 'Unable to connect to the database. Please try again later.'}
        return make_response(error_infoset, 500)
    
    if request.method == 'POST':
        element_json = request.json
        
        if element_json:
            try:
                new_element = Element.from_json(element_json)
            except:
                error_infoset = {'id': 'Data Error',
                         'description': 'Data must contain complete element information, and formatted as dictionary object'}
                return make_response(error_infoset, 400)
            
            if competency_id != new_element.competency_id:
                error_infoset = {'id': 'Data Error',
                         'description': 'Competency id specified in the URL must match the submitted element competency id'}
                return make_response(error_infoset, 400)
            
            if course_competency is None:
                error_infoset = {'id': 'Data Error',
                         'description': 'Competency id specified in the URL does not exist'}
                return make_response(error_infoset, 400) 
            
            for element in total_competency_elements:
                if element.element == new_element.element:
                    error_infoset = {'id': 'Data Error',
                                     'description': 'Element name already exists for the provided competency id.'}
                    return make_response(error_infoset, 400)
            
            try:
                get_db().add_element(new_element)
                retrieved_element = get_db().get_latest_element()
                get_db().add_course_elements(course_id, retrieved_element.element_id, 12)
                infoset = {'id': 'Request Complete',
                           'description': 'New element resource created'}
                resp = make_response(infoset, 201)
                resp.headers['Location'] = url_for('course_api.course_elements', course_id=course_id, competency_id=competency_id)
                return resp
            except Exception as e:
                error_infoset = {'id': 'Database Error',
                        'description': 'Unable to connect to the database. Please try again later.'}
                return make_response(error_infoset, 500)
                    
        
    elif request.method == 'GET':
        if len(total_course_elements) == 0 or course is None or course_competency is None:
            error_infoset = {'id' : 'Not Found',
                                 'description': 'The specified course or competency could not be found. Make sure each was entered correctly, or try again later.'}
            return make_response(error_infoset, 404)
        
        page_number = 1
        page_size = 50
        if request.args:
            page = request.args.get('page')
            if page:
                page_number = int(page)
                max_page = math.ceil(len(total_course_elements) / float(page_size))
                if page_number < 1 or page_number > max_page:
                    error_infoset = {'id' : 'Invalid Page Number',
                                 'description': f'Page number must be from 1, up to a maximum of {max_page}'}
                    return make_response(error_infoset, 404)
    
    try:
        elements, previous_page, next_page = get_db().get_course_elements_for_api(course_id, competency_id, page_size, page_number=page_number)
    except Exception as e:
        error_infoset = {'id': 'Database Error',
                    'description': 'Unable to connect to the database. Please try again later.'}
        return make_response(error_infoset, 500)
    
    if previous_page is not None:
        previous_page = url_for('course_api.course_elements', course_id=course_id, competency_id=competency_id, page=previous_page)
    if next_page is not None:
        next_page = url_for('course_api.course_elements', course_id=course_id, competency_id=competency_id, page=next_page)
    current_page = url_for('course_api.course_elements', course_id=course_id, competency_id=competency_id, page=page_number)
    
    count = len(total_course_elements)
    json = {'count': count, 'current_page': current_page, 'previous_page': previous_page, 'next_page': next_page, 'results': [element.to_json() for element in elements]}
    return make_response(json, 200)

## Since elements are uniquely distinguished by an element_id, a property that is never seen by the user as it's strictly database side, there is no use in having a
## route for specific elements.