from flask import Flask, Blueprint, request, url_for, make_response
from .dbmanager import get_db
from .competency import Competency
from .element import Element
import math

bp = Blueprint('competency_api', __name__, url_prefix = '/api/v1')

## THE FOLLOWING CHAIN COVERS ALL COMPETENCIES AND ELEMENTS, INCLUDING ANY THAT MAY NOT BE LINKED TO A SPECIFIC COURSE

@bp.route('/competencies', methods=['GET', 'POST'])
def competencies():
    try:
        total_competencies = get_db().get_competencies()
    except Exception as e:
        error_infoset = {'id': 'Database Error',
                        'description': 'Unable to connect to the database. Please try again later.'}
        return make_response(error_infoset, 500)
    
    if request.method == 'POST':
        competency_json = request.json
        
        if competency_json:
            try:
                new_competency, new_element = Competency.from_json(competency_json)
            except:
                error_infoset = {'id': 'Data Error',
                         'description': 'Data must contain complete competency and element information, and formatted as dictionary object'}
                return make_response(error_infoset, 400)
            
            for competency in total_competencies:
                if competency.competency_id == new_competency.competency_id:
                    error_infoset = {'id': 'Data Error',
                                'description': 'Specified competency id already exists'}
                    return make_response(error_infoset, 400)
                
            if new_element.competency_id != new_competency.competency_id:
                error_infoset = {'id': 'Data Error',
                                'description': 'Competency and Element competency ids do not match'}
                return make_response(error_infoset, 400)
            
            try:
                get_db().add_competency(new_competency)
                get_db().add_element(new_element)
                infoset = {'id': 'Request Complete',
                        'description': 'New competency resource created'}
                resp = make_response(infoset, 201)
                resp.headers['Location'] = url_for('competency_api.competency_by_id', competency_id=new_competency.competency_id)
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
                max_page = math.ceil(len(total_competencies) / float(page_size))
                if page_number < 1 or page_number > max_page:
                    error_infoset = {'id' : 'Invalid Page Number',
                                'description': f'Page number must be from 1, up to a maximum of {max_page}'}
                    return make_response(error_infoset, 404)
    
    try:
        competencies, previous_page, next_page = get_db().get_competencies_for_api(page_size, page_number=page_number)
    except Exception as e:
        error_infoset = {'id': 'Database Error',
                    'description': 'Unable to connect to the database. Please try again later.'}
        return make_response(error_infoset, 500)
    
    if previous_page is not None:
        previous_page = url_for('competency_api.competencies', page=previous_page)
    if next_page is not None:
        next_page = url_for('competency_api.competencies', page=next_page)
    current_page = url_for('competency_api.competencies', page=page_number)
    
    count = len(total_competencies)
    json = {'count': count, 'current_page': current_page, 'previous_page': previous_page, 'next_page': next_page, 'results': [competency.to_json() for competency in competencies]}
    return make_response(json, 200)

@bp.route('/competencies/<competency_id>', methods=['GET', 'PUT', 'DELETE'])
def competency_by_id(competency_id):
    try:
        competency = get_db().get_competency(competency_id)
        competencies = get_db().get_competencies()
        competency_elements = get_db().get_elements_of_competency(competency_id)
    except Exception as e:
        error_infoset = {'id': 'Database Error',
                         'description': 'Unable to connect to the database. Please try again later.'}
        return make_response(error_infoset, 500)
    
    if request.method == 'PUT':
        competency_json = request.json
        
        if competency_json:
            try:
                new_competency = Competency.from_json_update(competency_json)
            except:
                error_infoset = {'id': 'Data Error',
                         'description': 'Data must contain complete competency information, and formatted as dictionary object'}
                return make_response(error_infoset, 400)
            
            for competency in competencies:
                if competency.competency_id == new_competency.competency_id:
                    try:
                        get_db().edit_competency(new_competency)
                        resp = make_response({'id': 'Request Complete', 'description': 'Update Competency Request Complete. New element resource, if provided, must be added separately'}, 201)
                        resp.headers['Location'] = url_for('competency_api.competency_by_id', competency_id=competency_id)
                        return resp
                    except Exception as e:
                        error_infoset = {'id': 'Database Error',
                         'description': 'Unable to connect to the database. Please try again later.'}
                        return make_response(error_infoset, 500)
                    
            try:
                new_competency, new_element = Competency.from_json(competency_json)
            except:
                error_infoset = {'id': 'Data Error',
                         'description': 'Data must contain complete competency and element information, and formatted as dictionary object'}
                return make_response(error_infoset, 400)
            
            if new_element.competency_id != new_competency.competency_id:
                error_infoset = {'id': 'Data Error',
                                'description': 'Competency and element competency ids do not match'}
                return make_response(error_infoset, 400)
            
            try:
                get_db().add_competency(new_competency)
                get_db().add_element(new_element)
                resp = make_response({'id': 'Request Complete', 'description': 'Add Competency And Element Request Complete'}, 201)
                resp.headers['Location'] = url_for('competency_api.competency_by_id', competency_id=new_competency.competency_id)
                return resp
            except Exception as e:
                error_infoset = {'id': 'Database Error',
                        'description': 'Unable to connect to the database. Please try again later.'}
                return make_response(error_infoset, 500)
                
    elif request.method == 'DELETE':
        if competency is None:
            error_infoset = {'id': 'Data Error',
                         'description': 'Specified competency id does not exist'}
            return make_response(error_infoset, 400)
        
        if len(competency_elements) > 0:
            error_infoset = {'id': 'Data Error',
                         'description': 'Unable to delete competency: competency id is associated to 1 or more elements'}
            return make_response(error_infoset, 400)
            
        try:
            get_db().del_competency(competency_id)
            return make_response({'id': 'Deleted', 'description': 'Requested competency resource deleted'}, 204)
        except Exception as e:
            error_infoset = {'id': 'Database Error',
                         'description': 'Unable to connect to the database. Please try again later.'}
            return make_response(error_infoset, 500)
    
    elif request.method == 'GET':
        if competency is None:
            error_infoset = {'id' : 'Not Found',
                                 'description': 'The specified competency could not be found. Make sure it was entered correctly, or try again later.'}
            return make_response(error_infoset, 404)
        
        json_competency = competency.to_json()
        json_competency['url'] = url_for('competency_api.competency_by_id', competency_id=competency_id)
        return make_response(json_competency, 200)
    
@bp.route('/competencies/<competency_id>/elements', methods=['GET', 'POST'])
def competency_elements(competency_id):
    try:
        total_elements = get_db().get_elements_of_competency(competency_id)
        competency = get_db().get_competency(competency_id)
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
            
            if competency is None:
                error_infoset = {'id': 'Data Error',
                         'description': 'Competency id specified in the URL does not exist'}
                return make_response(error_infoset, 400) 
            
            for element in total_elements:
                if element.element == new_element.element:
                    error_infoset = {'id': 'Data Error',
                                     'description': 'Element name already exists for the provided competency id.'}
                    return make_response(error_infoset, 400)
            
            try:
                get_db().add_element(new_element)
                infoset = {'id': 'Request Complete',
                           'description': 'New element resource created'}
                resp = make_response(infoset, 201)
                resp.headers['Location'] = url_for('competency_api.competency_elements', competency_id=competency_id)
                return resp
            except Exception as e:
                error_infoset = {'id': 'Database Error',
                        'description': 'Unable to connect to the database. Please try again later.'}
                return make_response(error_infoset, 500)
                    
        
    elif request.method == 'GET':
        if competency is None:
            error_infoset = {'id' : 'Not Found',
                                 'description': 'The specified competency could not be found. Make sure it was entered correctly, or try again later.'}
            return make_response(error_infoset, 404)
        
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
        elements, previous_page, next_page = get_db().get_competency_elements_for_api(competency_id, page_size, page_number=page_number)
    except Exception as e:
        error_infoset = {'id': 'Database Error',
                    'description': 'Unable to connect to the database. Please try again later.'}
        return make_response(error_infoset, 500)
    
    if previous_page is not None:
        previous_page = url_for('competency_api.competency_elements', competency_id=competency_id, page=previous_page)
    if next_page is not None:
        next_page = url_for('competency_api.competency_elements', competency_id=competency_id, page=next_page)
    current_page = url_for('competency_api.competency_elements', competency_id=competency_id, page=page_number)
    
    count = len(total_elements)
    json = {'count': count, 'current_page': current_page, 'previous_page': previous_page, 'next_page': next_page, 'results': [element.to_json() for element in elements]}
    return make_response(json, 200)

## Elements being distinguished by element_id makes it meaningless to have routes to specific elements, as well as putting and deleting them.