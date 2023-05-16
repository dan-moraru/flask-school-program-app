import flask_unittest
from CourseManagementApp import create_app
from CourseManagementApp.db import Database
from CourseManagementApp.course import Course
from CourseManagementApp.element import Element

class CourseTestAPI(flask_unittest.ClientTestCase):
    app = create_app()
    
    ## The cleanup function is required to allow some of the unit tests to be run repeatedly and consitently without failing
    ## (as they make changes such as inserts into the database)
    ## Unfortunately, the usual way of getting a Database object and setting it in g will not work in the flask unit test context.
    ## It will result in consecutive database calls to cause an error regarding working outside of the test context.
    ## We couldn't find a solution that allows keeping get_db. So the Database object is created and manually closed each time.
    def cleanup(self):
        try:
            db = Database()
            
            db.del_course('420-150-DW')
            db.del_course('420-130-DW')
            db.del_element_for_unit_test('420-110-DW', 'Solve Any Programming Problem', 12)
            
            if db is not None:
                db.close()
        except:
            if db is not None:
                db.close()
                raise Exception('Database error, cleanup incomplete. Aborting')
    
    def test_courses_get(self, client):
        ## Testing GET on courses
        resp = client.get('/api/v1/courses')
        self.assertEqual(resp.status_code, 200)
        json = resp.json
        
        self.assertIsNotNone(json)
        self.assertIsNone(json['next_page'])
        self.assertIsNone(json['previous_page'])
        self.assertEqual(json['results'][0]['term_id'], 1)
        
       ## Testing GET on courses with invalid page numbers
        resp = client.get('/api/v1/courses/?page=0')
        self.assertEqual(resp.status_code, 404)
        resp = client.get('/api/v1/courses/?page=2')
        self.assertEqual(resp.status_code, 404) 
        
    def test_courses_post(self, client):
        try:
            self.cleanup()
        except:
            raise Exception('Database error, cleanup interrupted. The subsequent tests will likely fail as a consequence')
        
        ## Testing GET of courses
        resp = client.get('/api/v1/courses')
        self.assertEqual(resp.status_code, 200)
        json = resp.json    
        self.assertIsNotNone(json)
        self.assertEqual(json['results'][0]['term_id'], 1)
        
        ## Testing POST of a new course
        new_course = Course('420-150-DW', 'Programming Perspectives', 3, 3, 3, 'Understanding and adapting various thought processes towards computer programming', 1, 1)
        new_course_json = new_course.to_json()
        resp = client.post('/api/v1/courses', json=new_course_json)
        self.assertEqual(resp.status_code, 201)
        
        ## Testing POST attempting to add the same course
        resp = client.post('/api/v1/courses', json=new_course_json)
        self.assertEqual(resp.status_code, 400)
        
        ## Testing POST attempting to add a course with invalid (non-existent) term
        new_course = Course('420-170-DW', 'Programming Perspectives', 3, 3, 3, 'Understanding and adapting various thought processes towards computer programming', 1, 9)
        new_course_json = new_course.to_json()
        resp = client.post('/api/v1/courses', json=new_course_json)
        self.assertEqual(resp.status_code, 400)
        
        ## Testing POST attempting to add a course with invalid (non-existent) domain
        new_course = Course('420-156-DW', 'Programming Perspectives', 3, 3, 3, 'Understanding and adapting various thought processes towards computer programming', 9, 1)
        new_course_json = new_course.to_json()
        resp = client.post('/api/v1/courses', json=new_course_json)
        self.assertEqual(resp.status_code, 400)
        
    def test_course_by_id_get(self, client):
        ## Testing GET of existing course
        resp = client.get('/api/v1/courses/420-110-DW')
        self.assertEqual(resp.status_code, 200)
        json = resp.json 
        self.assertIsNotNone(json)
        self.assertIsNotNone(json['course_id'])
        self.assertEqual(json['course_id'], '420-110-DW')
        self.assertEqual(json['term_id'], 1)
        self.assertEqual(json['work_hours'], 3)
        
        ## Testing GET of non-existent course
        resp = client.get('/api/v1/courses/420-112-DS')
        self.assertEqual(resp.status_code, 404)
        
    def test_course_by_id_put(self, client):
        try:
            self.cleanup()
        except:
            raise Exception('Database error, cleanup interrupted. The subsequent tests will likely fail as a consequence')
        
        ## Testing PUT of new course
        new_course = Course('420-130-DW', 'Programming Alternatives', 3, 3, 3, 'Programming without the programming', 1, 1)
        new_course_json = new_course.to_json()
        resp = client.put('/api/v1/courses/420-130-DW', json=new_course_json)
        self.assertEqual(resp.status_code, 201)
        
        ## Testing GET of newly added course, positive control
        resp = client.get('/api/v1/courses/420-130-DW')
        json = resp.json
        self.assertEqual(json['course_title'], 'Programming Alternatives')
        
        ## Testing PUT of existing course causing update
        new_course_json['course_title'] = 'Programming Actual'
        resp = client.put('/api/v1/courses/420-130-DW', json=new_course_json)
        self.assertEqual(resp.status_code, 201)
        
        ## Testing GET of updated course and checking updated data
        resp = client.get('/api/v1/courses/420-130-DW')
        json = resp.json
        self.assertEqual(json['course_title'], 'Programming Actual')
        
        ## Testing PUT attempting to update a course with invalid (non-existent) term
        new_course = Course('420-130-DW', 'Programming Alternatives', 3, 3, 3, 'Programming without the programming', 1, 9)
        new_course_json = new_course.to_json()
        resp = client.put('/api/v1/courses/420-130-DW', json=new_course_json)
        self.assertEqual(resp.status_code, 400)
        
        ## Testing PUT attempting to update a course with invalid (non-existent) domain
        new_course = Course('420-130-DW', 'Programming Alternatives', 3, 3, 3, 'Programming without the programming', 9, 1)
        new_course_json = new_course.to_json()
        resp = client.put('/api/v1/courses/420-130-DW', json=new_course_json)
        self.assertEqual(resp.status_code, 400)
        
        ## Testing PUT attempting to add a course with invalid (non-existent) term
        new_course = Course('420-170-DW', 'Programming Perspectives', 3, 3, 3, 'Understanding and adapting various thought processes towards computer programming', 1, 9)
        new_course_json = new_course.to_json()
        resp = client.put('/api/v1/courses/420-170-DW', json=new_course_json)
        self.assertEqual(resp.status_code, 400)
        
        ## Testing PUT attempting to add a course with invalid (non-existent) domain
        new_course = Course('420-156-DW', 'Programming Perspectives', 3, 3, 3, 'Understanding and adapting various thought processes towards computer programming', 9, 1)
        new_course_json = new_course.to_json()
        resp = client.put('/api/v1/courses/420-156-DW', json=new_course_json)
        self.assertEqual(resp.status_code, 400)
        
    def test_course_by_id_delete(self, client):
        try:
            self.cleanup()
        except:
            raise Exception('Database error, cleanup interrupted. The subsequent tests will likely fail as a consequence')
        
        new_course = Course('420-150-DW', 'Programming Perspectives', 3, 3, 3, 'Understanding and adapting various thought processes towards computer programming', 1, 1)
        new_course_json = new_course.to_json()
        client.post('/api/v1/courses', json=new_course_json)
        
        ## Testing DELETE on existing course
        resp = client.delete('/api/v1/courses/420-150-DW')
        self.assertEqual(resp.status_code, 204)
        
        ## Testing DELETE on nonexistent course
        resp = client.delete('/api/v1/courses/420-250-DW')
        self.assertEqual(resp.status_code, 400)
        
    def test_course_competencies_get(self, client):
        ## Testing GET on competencies of an existing course
        resp = client.get('/api/v1/courses/420-110-DW/competencies')
        self.assertEqual(resp.status_code, 200)
        json = resp.json
        self.assertIsNotNone(json)
        self.assertIsNone(json['next_page'])
        self.assertIsNone(json['previous_page'])
        self.assertEqual(json['results'][0]['competency_id'], '00Q2')
        
        ## Testing GET on course competencies with invalid page numbers
        resp = client.get('/api/v1/competencies/420-110-DW/competencies/?page=0')
        self.assertEqual(resp.status_code, 404)
        resp = client.get('/api/v1/competencies/420-110-DW/competencies/?page=2')
        self.assertEqual(resp.status_code, 404)
        
        ## Testing GET on competencies of a nonexistent course
        resp = client.get('/api/v1/courses/420-110-DS/competencies')
        self.assertEqual(resp.status_code, 404)
        
    def test_course_competency_by_id_get(self, client):
        ## Testing GET on existing course competency
        resp = client.get('/api/v1/courses/420-110-DW/competencies/00Q2')
        self.assertEqual(resp.status_code, 200)
        json = resp.json
        self.assertIsNotNone(json)
        self.assertEqual(json['competency_id'], '00Q2')
        self.assertEqual(json['competency_type'], 'Mandatory')
        
        ## Testing GET on nonexistent course competency
        resp = client.get('/api/v1/courses/420-110-DW/competencies/0SQ9')
        
        ## Testing GET on competency to a nonexistent course
        self.assertEqual(resp.status_code, 404)
        resp = client.get('/api/v1/courses/420-110-DS/competencies/00Q2')
        self.assertEqual(resp.status_code, 404)
        
    def test_course_elements_get(self, client):
        ## Testing GET of course elements
        resp = client.get('/api/v1/courses/420-110-DW/competencies/00Q2/elements')
        self.assertEqual(resp.status_code, 200)
        json = resp.json
        self.assertIsNotNone(json)
        self.assertIsNone(json['next_page'])
        self.assertIsNone(json['previous_page'])
        self.assertEqual(json['results'][0]['element_order'], 1)
        
        ## Testing GET of course elements where the url course id does not exist
        resp = client.get('/api/v1/courses/420-110-DS/competencies/00Q2/elements')
        self.assertEqual(resp.status_code, 404)
        
        ## Testing GET of course elements where the url competency id does not exist
        resp = client.get('/api/v1/courses/420-110-DW/competencies/00QH/elements')
        self.assertEqual(resp.status_code, 404)
        
        ## Testing GET on course elements with invalid page numbers
        resp = client.get('/api/v1/courses/420-110-DS/competencies/00Q2/elements/?page=0')
        self.assertEqual(resp.status_code, 404)
        resp = client.get('/api/v1/courses/420-110-DS/competencies/00Q2/elements/?page=2')
        self.assertEqual(resp.status_code, 404)
        
    def test_course_elements_post(self, client):
        try:
            self.cleanup()
        except:
            raise Exception('Database error, cleanup interrupted. The subsequent tests will likely fail as a consequence')
        
        ## Testing GET on existing element
        resp = client.get('/api/v1/courses/420-110-DW/competencies/00Q2/elements')
        self.assertEqual(resp.status_code, 200)
        json = resp.json    
        self.assertIsNotNone(json)
        self.assertEqual(json['results'][0]['competency_id'], '00Q2')
        
        ## Testing POST of element with valid values
        new_element = Element(1, 'Solve Any Programming Problem', 'Under all circumstances', '00Q2')
        new_element_json = new_element.to_json()
        resp = client.post('/api/v1/courses/420-110-DW/competencies/00Q2/elements', json=new_element_json)
        self.assertEqual(resp.status_code, 201)
        
        ## Testing POST of course element with competency id mismatching url competency id
        new_element = Element(1, 'Solve Any Programming Problem', 'Under all circumstances', '0ZZ2')
        new_element_json = new_element.to_json()
        resp = client.post('/api/v1/courses/420-110-DW/competencies/00Q2/elements', json=new_element_json)
        self.assertEqual(resp.status_code, 400)
        
        ## Testing POST of course element with nonexistent url competency id
        new_element = Element(1, 'Solve Any Programming Problem', 'Under all circumstances', '0ZZ2')
        new_element_json = new_element.to_json()
        resp = client.post('/api/v1/courses/420-110-DW/competencies/0ZZ8/elements', json=new_element_json)
        self.assertEqual(resp.status_code, 400)
        
        ## Testing POST of course element with an associated competency where an element with the same name already exists
        new_element = Element(1, 'Solve Any Programming Problem', 'Under all circumstances', '00Q2')
        new_element_json = new_element.to_json()
        resp = client.post('/api/v1/courses/420-110-DW/competencies/00Q2/elements', json=new_element_json)
        self.assertEqual(resp.status_code, 400)