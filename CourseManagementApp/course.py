class Course:
    def __init__(self, course_id, course_title, theory_hours, lab_hours, work_hours,  description, domain_id, term_id):
        if not isinstance(course_id, str) or len(course_id) == 0:
            raise TypeError('course_id must be a non-zero string')
        if not isinstance(course_title, str) or len(course_title) == 0:
            raise TypeError('course_title must be a non-zero string')
        if not isinstance(theory_hours, int):
            raise TypeError('theory_hours must be a int')
        if not isinstance(lab_hours, int):
            raise TypeError('lab_hours must be an int')
        if not isinstance(work_hours, int):
            raise TypeError('work_hours must be an int')
        if not isinstance(description, str) or len(description) == 0:
            raise TypeError('description must be a non-zero string')
        if not isinstance(domain_id, int):
            raise TypeError('domain_id must be an int')
        if not isinstance(term_id, int):
            raise TypeError('term_id must be an int')
        
        self.course_id = course_id
        self.course_title = course_title
        self.theory_hours = theory_hours
        self.lab_hours = lab_hours
        self.work_hours = work_hours
        self.description = description
        self.domain_id = domain_id
        self.term_id = term_id
        
    def __repr__(self):
        return f'Course({self.course_id}, {self.course_title}, {self.theory_hours}, {self.lab_hours}, {self.work_hours}, {self.description}, {self.domain_id}, {self.term_id})' 
    
    def __str__(self):
        return f'Course Title: {self.course_title}\nCourse Code: {self.course_id}\nTerm: {self.term_id}\nDescription: {self.description}\nTheory Hours: {self.theory_hours}\nLab Hours: {self.lab_hours}\nHomework Hours: {self.work_hours}'
    
    def from_json(course_json):
        if not isinstance(course_json, dict):
            raise TypeError('Error: Expected type dict as input')
        
        try:
            course = Course(course_json['course_id'], course_json['course_title'], course_json['theory_hours'], course_json['lab_hours'], course_json['work_hours'], course_json['description'], course_json['domain_id'], course_json['term_id'])
        except:
            raise Exception('Error: Invalid data format for course object')
        
        return course
    
    def to_json(self):
        return self.__dict__
    
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, TextAreaField
from wtforms.validators import DataRequired, NumberRange
    
class CourseForm(FlaskForm):
    course_title = StringField('Course Title', validators=[DataRequired()])
    course_id = StringField('Course Id', validators=[DataRequired()])
    term_id = SelectField('Associated Term', validators=[DataRequired()], coerce=int, choices=[])
    domain = SelectField('Associated Domain', validators=[DataRequired()], choices=[])
    theory_hours = IntegerField('Theory Hours', validators=[DataRequired(), NumberRange(min=0, max=None, message=None)])
    lab_hours = IntegerField('Lab Hours', validators=[DataRequired(), NumberRange(min=0, max=None, message=None)])
    work_hours = IntegerField('Homework Hours', validators=[DataRequired(), NumberRange(min=0, max=None, message=None)])
    description = TextAreaField('Description', validators=[DataRequired()])
