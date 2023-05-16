import secrets
from flask import Flask, render_template
from flask_login import LoginManager
from .dbmanager import get_db
import os

def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=secrets.token_urlsafe(32),
        IMAGE_PATH=os.path.join(app.instance_path, 'images')
    )
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    app.teardown_appcontext(cleanup)
    
    from .dbmanager import init_db_command
    app.cli.add_command(init_db_command)
    
    from .home_view import bp as home_bp
    app.register_blueprint(home_bp)
    
    from .course_view import bp as course_bp
    app.register_blueprint(course_bp)
    
    from .term_view import bp as term_bp
    app.register_blueprint(term_bp)
    
    from .domain_view import bp as domain_bp
    app.register_blueprint(domain_bp)
    
    from .competency_view import bp as competency_bp
    app.register_blueprint(competency_bp)
    
    from .element_view import bp as element_bp
    app.register_blueprint(element_bp)

    from .course_elements_view import bp as course_elements_bp
    app.register_blueprint(course_elements_bp)

    from .auth_view import bp as auth_bp
    app.register_blueprint(auth_bp)

    from .admin_view import bp as admin_bp
    app.register_blueprint(admin_bp)
    
    from .course_api import bp as course_api_bp
    app.register_blueprint(course_api_bp)
    
    from .competency_api import bp as competency_api_bp
    app.register_blueprint(competency_api_bp)
    
    from .element_api import bp as element_api_bp
    app.register_blueprint(element_api_bp)
    
    from .domain_api import bp as domain_api_bp
    app.register_blueprint(domain_api_bp)
    
    from .term_api import bp as term_api_bp
    app.register_blueprint(term_api_bp)
    
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('custom404.html'), 404
    
    @app.errorhandler(401)
    def unauthorized(error):
        return render_template('custom401.html'), 401
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return get_db().get_user_by_id(int(user_id))

    os.makedirs(app.instance_path,exist_ok=True)
    os.makedirs(app.config['IMAGE_PATH'], exist_ok=True)

    return app

def cleanup(value):
    from .dbmanager import close_db
    close_db()
