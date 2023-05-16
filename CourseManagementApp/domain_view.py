from flask import (Blueprint, render_template, request, flash, redirect, url_for, abort)
from .dbmanager import get_db
from .domain import Domain, DomainForm
from .exceptions import ObjectAlreadyExists
from flask_login import login_required, current_user
bp = Blueprint('domain', __name__, url_prefix='/domain/')

@bp.route('/<int:id>/')
def get_domain_by_id(id):
    try:
        domain = get_db().get_domain(id)
        courses = get_db().get_courses()
    except:
        flash('Cannot reach the database')
        return redirect(url_for('home.index'))
        
    if (domain):
        return render_template('domain_information.html', domain=domain, courses=courses)
    else:
        flash('Domain not found')
        abort(404)

@bp.route('/form/add/', methods=['GET', 'POST'])
@login_required
def add_domain():
    if current_user.blocked:
        abort(401)
    
    try:
        domains = get_db().get_domains()
    except:
        flash('Database error')
        return redirect(url_for('home.index'))
        
    form = DomainForm()
    
    if request.method == 'POST' and form.validate_on_submit():
        new_domain = Domain(form.domain.data, form.domain_description.data)
        
        for domain in domains:
            if new_domain.domain == domain.domain:
                flash('Domain name is already in use')
                return redirect(url_for('home.index'))
        
        try:
            get_db().add_domain(new_domain)
            flash('Domain Successfully Added')
            domains_again = get_db().get_domains()
            for domain in domains_again:
                if new_domain.domain == domain.domain:
                    new_domain.domain_id = domain.domain_id

            return redirect(url_for('domain.get_domain_by_id', id=new_domain.domain_id))
        except ObjectAlreadyExists as e:
            flash(str(e))
        except Exception:
            flash('Cannot reach the database')
        return redirect(url_for('home.index'))
    return render_template('form_domain.html', form=form, domain=None, action='Add')

@bp.route('/form/edit/<int:domain_id>/', methods=['GET','POST'])
@login_required
def edit_domain(domain_id):
    if current_user.blocked:
        abort(401)
    
    try:
        domains = get_db().get_domains()
    except:
        flash('Database error')
        return redirect(url_for('home.index'))
        
    form = DomainForm()
    try:
        domain = get_db().get_domain(domain_id)
        if not domain:
            flash("Domain does not exist")
            return redirect(url_for('home.index'))
    except Exception:
        flash('Database Error')
        return redirect(url_for('home.index'))
    
    if request.method == 'POST':
        if form.validate_on_submit():
            updated_domain = Domain(form.domain.data, form.domain_description.data)
            
            updated_domain.domain_id = domain_id
            try:
                get_db().edit_domain(updated_domain)
                flash('Domain Successfully Updated')
            except Exception:
                flash('Database Error')
                return redirect(url_for('home.index'))
            return redirect(url_for('domain.get_domain_by_id', id=updated_domain.domain_id))
            
    return render_template('form_domain.html', form=form, domain=domain, action='Edit')

@bp.route('/form/delete/<int:domain_id>/')
@login_required
def delete_domain(domain_id):
    if current_user.blocked:
        abort(401)
        
    try:
        domain = get_db().get_domain(domain_id)
        if domain:
            get_db().del_domain(domain_id)
            flash('Domain deleted succesfully')
            return redirect(url_for('domain.get_domains'))
        else:
            flash('Domain does not exist')
    except Exception:
        flash('Database Error: Ensure domain is not linked to any course')
    
    return redirect(url_for('home.index'))

@bp.route('/reference/')
def get_domains():
    try:
        domains = get_db().get_domains()
        courses = get_db().get_courses()
    except:
        flash('Cannot reach the database')
        return redirect(url_for('home.index'))
    
    return render_template('domains_reference.html', domains=domains, courses=courses)