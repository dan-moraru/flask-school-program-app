class Term:
    def __init__(self, term_id):
        if not isinstance(term_id, int):
            raise TypeError('term_id must be an int')
        
        self.term_id = term_id
        self.term_name = 'Fall'
        if term_id % 2 == 0:
            self.term_name = 'Winter'
        
    def __repr__(self):
        return f'Term({self.term_id}, {self.term_name})' 
    
    def __str__(self):
        return f'Term {self.term_id} ({self.term_name})'
    
    def from_json(term_json):
        if not isinstance(term_json, dict):
            raise TypeError('Error: Expected type dict as input')
        new_term = Term(term_json['term_id'])
        new_term.term_name = term_json['term_name']
        return new_term
    
    def to_json(self):
        return self.__dict__
    
from flask_wtf import FlaskForm
from wtforms import IntegerField
from wtforms.validators import DataRequired, NumberRange
    
class TermForm(FlaskForm):
    term_id = IntegerField('Term Number', validators=[DataRequired(), NumberRange(min=1, max=None, message=None)])