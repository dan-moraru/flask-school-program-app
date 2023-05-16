class Element:
    def __init__(self, element_order, element, element_criteria, competency_id):
        if not isinstance(element_order, int):
            raise TypeError('element_order must be an int')
        if not isinstance(element, str) or len(element) == 0:
            raise TypeError('element must be a non-zero length string')
        if not isinstance(element_criteria, str) or len(element_criteria) == 0:
            raise TypeError('element_criteria must be a non-zero string')
        if not isinstance(competency_id, str) or len(competency_id) == 0:
            raise TypeError('competency_id must be a non-zero string')
        
        self.element_order = element_order
        self.element = element
        self.element_criteria = element_criteria
        self.competency_id = competency_id
        self.element_id = None
        
    def __repr__(self):
        return f'Element({self.element_order}, {self.element}, {self.element_criteria}, {self.competency_id})' 
    
    def __str__(self):
        return f'Competency Element: {self.element}\nOrder of Attainment: {self.element_order}\nPerformance Criteria: {self.element_criteria}\nAssociated Competency Code: {self.competency_id}'
    
    def from_json(element_json):
        if not isinstance(element_json, dict):
            raise TypeError('Error: Expected type dict as input')
        
        try:
            element = Element(element_json['element_order'], element_json['element'], element_json['element_criteria'], element_json['competency_id'])
        except:
            raise Exception('Invalid data format for element object')
        
        return element
    
    def to_json(self):
        return self.__dict__
    
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, TextAreaField
from wtforms.validators import DataRequired, NumberRange
    
class ElementForm(FlaskForm):
    element = StringField('Element Name', validators=[DataRequired()])
    element_criteria = TextAreaField('Performance Criteria', validators=[DataRequired()])
    element_order = IntegerField('Order of Attainment', validators=[DataRequired(), NumberRange(min=1, max=None, message=None)])
    competency_id = SelectField('Associated Competency Id', validators=[DataRequired()], choices=[])
