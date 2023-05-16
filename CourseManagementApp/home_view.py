from flask import (Blueprint, render_template, flash, redirect, url_for, request, abort)
from .dbmanager import get_db
from .search import SearchForm
bp = Blueprint('home', __name__, url_prefix='/')

@bp.route('/', methods=['GET', 'POST'])
def index():
    form = SearchForm()
    try:
        courses = get_db().get_courses()
        terms = get_db().get_terms()
    except:
        flash('Unable to connect to database')
        abort(404)
    
    if request.method == 'POST':
        if form.validate_on_submit:
            search_query = request.form['search_query']
            return redirect(url_for('home.search', search_query=search_query))
    
    return render_template('home.html', courses=courses, terms=terms, form=form)

@bp.route('/<search_query>/')
def search(search_query):
    try:
        search_results = get_db().get_search_results(search_query)
    except:
        flash('Database Error')
        return redirect(url_for('home.index'))
    return render_template('search_results.html', search_query=search_query, results=search_results)