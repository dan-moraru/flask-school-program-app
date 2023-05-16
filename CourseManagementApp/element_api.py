from flask import Flask, Blueprint, request, url_for, make_response
from .dbmanager import get_db
from .element import Element
import math

bp = Blueprint('element_api', __name__, url_prefix = '/api/v1')

@bp.route('/elements', methods=['GET', 'POST'])
def elements():
    try:
        total_elements = get_db().get_elements()
        competencies = get_db().get_competencies()
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
            
            for element in total_elements:
                if element.element == new_element.element and element.competency_id == new_element.competency_id:
                    error_infoset = {'id': 'Data Error',
                                     'description': 'Element name already exists for an existing competency id.'}
                    return make_response(error_infoset, 400)
                
            invalid_data = True
            for competency in competencies:
                if competency.competency_id == new_element.competency_id:
                    invalid_data = False
                    break
            
            if invalid_data:
                error_infoset = {'id': 'Data Error',
                                    'description': 'Specified competency id does not exist'}
                return make_response(error_infoset, 400)
            
            try:
                get_db().add_element(new_element)
                infoset = {'id': 'Request Complete',
                           'description': 'New element resource created'}
                resp = make_response(infoset, 201)
                resp.headers['Location'] = url_for('element_api.elements')
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
                max_page = math.ceil(len(total_elements) / float(page_size))
                if page_number < 1 or page_number > max_page:
                    error_infoset = {'id' : 'Invalid Page Number',
                                 'description': f'Page number must be from 1, up to a maximum of {max_page}'}
                    return make_response(error_infoset, 404)
    
    try:
        elements, previous_page, next_page = get_db().get_elements_for_api(page_size, page_number=page_number)
    except Exception as e:
        error_infoset = {'id': 'Database Error',
                    'description': 'Unable to connect to the database. Please try again later.'}
        return make_response(error_infoset, 500)
    
    if previous_page is not None:
        previous_page = url_for('element_api.elements', page=previous_page)
    if next_page is not None:
        next_page = url_for('element_api.elements', page=next_page)
    current_page = url_for('element_api.elements', page=page_number)
    
    count = len(total_elements)
    json = {'count': count, 'current_page': current_page, 'previous_page': previous_page, 'next_page': next_page, 'results': [element.to_json() for element in elements]}
    return make_response(json, 200)

## As explained above, elements being distinguished by element_id makes it meaningless to have routes to specific elements, as well as putting and deleting them.