class Domain:
    def __init__(self, domain, domain_description):
        if not isinstance(domain, str) or len(domain) == 0:
            raise TypeError('domain must be a non-zero string')
        if not isinstance(domain_description, str) or len(domain_description) == 0:
            raise TypeError('domain_description must be a non-zero string')
        
        self.domain = domain
        self.domain_description = domain_description
        self.domain_id = None
        
    def __repr__(self):
        return f'Domain({self.domain}, {self.domain_description})' 
    
    def __str__(self):
        return f'Domain: {self.domain}\nDescription: {self.domain_description}'
    
    def from_json(domain_json):
        if not isinstance(domain_json, dict):
            raise TypeError('Error: Expected type dict as input')
        
        try:
            domain = Domain(domain_json['domain'], domain_json['domain_description'])
        except:
            raise Exception('Error: Invalid data format for domain object')
        
        return domain
    
    def to_json(self):
        return self.__dict__
    
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired
    
class DomainForm(FlaskForm):
    domain = StringField('Domain Name', validators=[DataRequired()])
    domain_description = TextAreaField('Domain Description', validators=[DataRequired()])