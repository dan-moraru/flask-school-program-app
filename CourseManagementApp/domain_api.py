from flask import Flask, Blueprint, request, url_for, make_response
from .dbmanager import get_db
from .domain import Domain
import math

bp = Blueprint('domain_api', __name__, url_prefix = '/api/v1')

@bp.route('/domains', methods=['GET', 'POST'])
def domains():
    try:
        total_domains = get_db().get_domains()
    except Exception as e:
        error_infoset = {'id': 'Database Error',
                         'description': 'Unable to connect to the database. Please try again later.'}
        return make_response(error_infoset, 500)
    
    if request.method == 'POST':
        domain_json = request.json
        
        if domain_json:
            try:
                new_domain = Domain.from_json(domain_json)
            except:
                error_infoset = {'id': 'Data Error',
                         'description': 'Data must contain complete domain information, and formatted as dictionary object'}
                return make_response(error_infoset, 400)
            
            for domain in total_domains:
                if domain.domain == new_domain.domain:
                    error_infoset = {'id': 'Data Error',
                                     'description': 'Domain name already exists'}
                    return make_response(error_infoset, 400)
            
            try:
                get_db().add_domain(new_domain)
                infoset = {'id': 'Request Complete',
                           'description': 'New domain resource created'}
                resp = make_response(infoset, 201)
                resp.headers['Location'] = url_for('domain_api.domains')
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
                max_page = math.ceil(len(total_domains) / float(page_size))
                if page_number < 1 or page_number > max_page:
                    error_infoset = {'id' : 'Invalid Page Number',
                                 'description': f'Page number must be from 1, up to a maximum of {max_page}'}
                    return make_response(error_infoset, 404)
    
    try:
        domains, previous_page, next_page = get_db().get_domains_for_api(page_size, page_number=page_number)
    except Exception as e:
        error_infoset = {'id': 'Database Error',
                    'description': 'Unable to connect to the database. Please try again later.'}
        return make_response(error_infoset, 500)
    
    if previous_page is not None:
        previous_page = url_for('domain_api.domains', page=previous_page)
    if next_page is not None:
        next_page = url_for('domain_api.domains', page=next_page)
    current_page = url_for('domain_api.domains', page=page_number)
    
    count = len(total_domains)
    json = {'count': count, 'current_page': current_page, 'previous_page': previous_page, 'next_page': next_page, 'results': [domain.to_json() for domain in domains]}
    return make_response(json, 200)

## Similar to elements, domains being distinguished by domain_id makes it meaningless to have routes to specific domains, as well as putting and deleting them.