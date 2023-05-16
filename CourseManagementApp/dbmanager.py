import click, os
from flask import current_app, g
from .db import Database

def get_db():
    if 'db' not in g:
        g.db = Database()
    return g.db

def close_db():
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    get_db().run_file(os.path.join(current_app.root_path, 'sql', 'remove.sql'))
    get_db().run_file(os.path.join(current_app.root_path, 'sql', 'project_type.sql'))
    get_db().run_file(os.path.join(current_app.root_path, 'sql', 'setup.sql'))
    get_db().run_file(os.path.join(current_app.root_path, 'sql', 'inserting.sql'))
    get_db().run_file(os.path.join(current_app.root_path, 'sql', 'logging.sql'))
    get_db().run_file(os.path.join(current_app.root_path, 'sql', 'views.sql'))
    get_db().run_file(os.path.join(current_app.root_path, 'sql', 'courses_package.sql'))

@click.command('init-db')
def init_db_command():
    init_db()
    click.echo('Initialized the databse')
