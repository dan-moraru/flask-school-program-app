from .element import Element

class Competency:
    def __init__(self, competency_id, competency, competency_achievement, competency_type):
        if not isinstance(competency_id, str):
            raise TypeError('competency_id must be a non-zero string')
        if not isinstance(competency, str):
            raise TypeError('competency must be a non-zero string')
        if not isinstance(competency_achievement, str):
            raise TypeError('competency_achievement must be a non-zero string')
        if not isinstance(competency_type, str):
            raise TypeError('competency_type must be a non-zero string')
        
        self.competency_id = competency_id
        self.competency = competency
        self.competency_achievement = competency_achievement
        self.competency_type = competency_type
        
    def __repr__(self):
        return f'Competency({self.competency_id}, {self.competency}, {self.competency_achievement}, {self.competency_type})' 
    
    def __str__(self):
        return f'Competency Statement: {self.competency}\nCode: {self.competency_id}\n{self.competency_type}\nAchievement Context: {self.competency_achievement}'
    
    def from_json(competency_json):
        if not isinstance(competency_json, dict):
            raise TypeError('Error: Expected type dict as input')
        
        try:
            element = Element(competency_json['element_order'], competency_json['element'], competency_json['element_criteria'], competency_json['element_competency_id'])    
            competency = Competency(competency_json['competency_id'], competency_json['competency'], competency_json['competency_achievement'], competency_json['competency_type'])
        except:
            raise Exception('Error: Invalid data format for competency or element object')
        
        return competency, element
    
    def from_json_update(competency_json):
        if not isinstance(competency_json, dict):
            raise TypeError('Error: Expected type dict as input')
        
        try:
            competency = Competency(competency_json['competency_id'], competency_json['competency'], competency_json['competency_achievement'], competency_json['competency_type'])
        except:
            raise Exception('Error: Invalid data format for competency object')
        
        return competency 
    
    def to_json(self, element=None):
        competency_json = self.__dict__
        
        if element is not None:
            competency_json['element_order'] = element.element_order
            competency_json['element'] = element.element
            competency_json['element_criteria'] = element.element_criteria
            competency_json['element_competency_id'] = element.competency_id
        
        return competency_json
    
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Length, NumberRange
    
class CompetencyForm(FlaskForm):
    competency_id = StringField('Competency Id', validators=[DataRequired(), Length(min=4, max=4)])
    competency = StringField('Competency Statement', validators=[DataRequired()])
    competency_achievement = TextAreaField('Achievement Context', validators=[DataRequired()])
    competency_type = BooleanField('Mandatory Competency', default=True)
    element = StringField('Element Name', validators=[DataRequired()])
    element_criteria = TextAreaField('Performance Criteria', validators=[DataRequired()])
    element_order = IntegerField('Order of Attainment', validators=[DataRequired(), NumberRange(min=1, max=None, message=None)])