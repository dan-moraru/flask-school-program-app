from flask import Flask, Blueprint, request, url_for, make_response
from .dbmanager import get_db
from .term import Term
import math

bp = Blueprint('term_api', __name__, url_prefix = '/api/v1')

@bp.route('/terms', methods=['GET', 'POST'])
def terms():
    try:
        total_terms = get_db().get_terms()
    except Exception as e:
        error_infoset = {'id': 'Database Error',
                         'description': 'Unable to connect to the database. Please try again later.'}
        return make_response(error_infoset, 500)
    
    if request.method == 'POST':
        term_json = request.json
        
        if term_json:
            try:
                new_term = Term.from_json(term_json)
            except:
                error_infoset = {'id': 'Data Error',
                         'description': 'Data must contain complete term information, and formatted as dictionary object'}
                return make_response(error_infoset, 400)
            
            for term in total_terms:
                if term.term_id == new_term.term_id:
                    error_infoset = {'id': 'Data Error',
                                     'description': 'Term id already exists'}
                    return make_response(error_infoset, 400)
            
            try:
                get_db().add_term(new_term)
                infoset = {'id': 'Request Complete',
                           'description': 'New term resource created'}
                resp = make_response(infoset, 201)
                resp.headers['Location'] = url_for('term_api.term_by_id', term_id=new_term.term_id)
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
                max_page = math.ceil(len(total_terms) / float(page_size))
                if page_number < 1 or page_number > max_page:
                    error_infoset = {'id' : 'Invalid Page Number',
                                 'description': f'Page number must be from 1, up to a maximum of {max_page}'}
                    return make_response(error_infoset, 404)
    
    try:
        terms, previous_page, next_page = get_db().get_terms_for_api(page_size, page_number=page_number)
    except Exception as e:
        error_infoset = {'id': 'Database Error',
                    'description': 'Unable to connect to the database. Please try again later.'}
        return make_response(error_infoset, 500)
    
    if previous_page is not None:
        previous_page = url_for('term_api.terms', page=previous_page)
    if next_page is not None:
        next_page = url_for('term_api.terms', page=next_page)
    current_page = url_for('term_api.terms', page=page_number)
    
    count = len(total_terms)
    json = {'count': count, 'current_page': current_page, 'previous_page': previous_page, 'next_page': next_page, 'results': [term.to_json() for term in terms]}
    return make_response(json, 200)

## Terms are not updated directly; only by adding and deleting. As such, supporting PUT would be redundant to POST

@bp.route('/terms/<int:term_id>', methods=['GET', 'DELETE'])
def term_by_id(term_id):
    try:
        term = get_db().get_term(term_id)
        courses = get_db().get_courses()
    except Exception as e:
        error_infoset = {'id': 'Database Error',
                         'description': 'Unable to connect to the database. Please try again later.'}
        return make_response(error_infoset, 500)
    
    if request.method == 'DELETE':
        if term is None:
            error_infoset = {'id': 'Data Error',
                         'description': 'Specified term id does not exist'}
            return make_response(error_infoset, 400)
        
        for course in courses:
            if course.term_id == term_id:
                error_infoset = {'id': 'Data Error',
                         'description': 'Unable to delete term resource: term id is associated to 1 or more courses'}
                return make_response(error_infoset, 400)
        
        try:
            get_db().del_term(term_id)
            return make_response({'id': 'Deleted', 'description': 'Requested term resource deleted'}, 204)
        except Exception as e:
            error_infoset = {'id': 'Database Error',
                         'description': 'Unable to connect to the database. Please try again later.'}
            return make_response(error_infoset, 500)
    
    elif request.method == 'GET':
        if term is None:
            error_infoset = {'id' : 'Not Found',
                                 'description': 'The specified term could not be found. Make sure it was entered correctly, or try again later.'}
            return make_response(error_infoset, 404)
        
        json_term = term.to_json()
        json_term['url'] = url_for('term_api.term_by_id', term_id=term_id)
        return make_response(json_term, 200)