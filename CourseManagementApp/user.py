from flask_login import UserMixin
from datetime import datetime
class Member(UserMixin):
    # Constructor for lowest member creation
    def __init__(self, name, password, email, date_created, blocked):
        if not isinstance(name, str):
            raise TypeError('name expecting a string')
        if not isinstance(password, str):
            raise TypeError('password expecting a string')
        if not isinstance(email, str):
            raise TypeError('email expecting a string')
        if not isinstance(date_created, datetime):
            raise TypeError('date_created must be a datetime')
        self.name = name
        self.password = password
        self.email = email
        self.access_group = 1
        self.date_created = date_created
        if blocked == '1':
            self.blocked = True
        else:
            self.blocked = False
        self.id = None

    def __repr__(self):
        return f'Member({self.name},{self.email})'
    
    def __str__(self):
        return f'<h2>{self.name}</h2><h3>{self.email}</h3>'
                 
class AdminUser(Member):
    def __init__(self, name, password, email, date_created, blocked):
        super().__init__(name, password, email, date_created, blocked)
        self.access_group = 2

class ServerAdmin(AdminUser):
    def __init__(self, name, password, email, date_created, blocked):
        super().__init__(name, password, email, date_created, blocked)
        self.access_group = 3


from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, EmailField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class SignupForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    email = EmailField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    avatar = FileField('avatar', validators=[FileAllowed(['png'])])

class LoginForm(FlaskForm):
    email = EmailField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField('remember me')