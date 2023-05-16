import flask_unittest
from CourseManagementApp import create_app
from CourseManagementApp.db import Database
from CourseManagementApp.course import Course
from CourseManagementApp.term import Term

class TermTestAPI(flask_unittest.ClientTestCase):
    app = create_app()
    
    ## The cleanup function is required to allow some of the unit tests to be run repeatedly and consitently without failing
    ## (as they make changes such as inserts into the database)
    ## Unfortunately, the usual way of getting a Database object and setting it in g will not work in the flask unit test context.
    ## It will result in consecutive database calls to cause an error regarding working outside of the test context.
    ## We couldn't find a solution that allows keeping get_db. So the Database object is created and manually closed each time.
    def cleanup(self):
        try:
            db = Database()
            
            db.del_course('420-999-DW')
            db.del_term(7)
            
            if db is not None:
                db.close()
        except:
            if db is not None:
                db.close()
                raise Exception('Database error, cleanup incomplete. Aborting')
        
    def test_terms_get(self, client):
        ## Testing GET of terms
        resp = client.get('/api/v1/terms')
        self.assertEqual(resp.status_code, 200)
        json = resp.json
        self.assertIsNotNone(json)
        self.assertIsNone(json['next_page'])
        self.assertIsNone(json['previous_page'])
        self.assertEqual(json['results'][0]['term_name'], 'Fall')
        
        ## Testing GET of terms with invalid page numbers
        resp = client.get('/api/v1/terms/?page=0')
        self.assertEqual(resp.status_code, 404)
        resp = client.get('/api/v1/terms/?page=2')
        self.assertEqual(resp.status_code, 404)
        
    def test_terms_post(self, client):
        try:
            self.cleanup()
        except:
            raise Exception('Database error, cleanup interrupted. The subsequent tests will likely fail as a consequence')
        
        ## Testing GET of terms
        resp = client.get('/api/v1/terms')
        self.assertEqual(resp.status_code, 200)
        json = resp.json
        self.assertIsNotNone(json)
        self.assertEqual(json['results'][0]['term_name'], 'Fall')
        
        ## Testing POST of terms
        new_term = Term(7)
        new_term_json = new_term.to_json()
        resp = client.post('/api/v1/terms', json=new_term_json)
        self.assertEqual(resp.status_code, 201)
        
        ## Testing POST of same term
        resp = client.post('/api/v1/terms', json=new_term_json)
        self.assertEqual(resp.status_code, 400)
    
    def test_term_by_id_get(self, client):
        ## Testing GET of term
        resp = client.get('/api/v1/terms/1')
        self.assertEqual(resp.status_code, 200)
        json = resp.json
        self.assertIsNotNone(json)
        self.assertEqual(json['term_name'], 'Fall')
        
        ## Testing GET of nonexistent term
        resp = client.get('/api/v1/terms/15')
        self.assertEqual(resp.status_code, 404)
        
    def test_term_by_id_delete(self, client):
        try:
            self.cleanup()
        except:
            raise Exception('Database error, cleanup interrupted. The subsequent tests will likely fail as a consequence')
        
        ## Testing POST of term
        new_term = Term(7)
        new_term_json = new_term.to_json()
        resp = client.post('/api/v1/terms', json=new_term_json)
        self.assertEqual(resp.status_code, 201)
        
        ## Testing DELETE of term
        resp = client.delete('/api/v1/terms/7')
        self.assertEqual(resp.status_code, 204)
        
        ## Testing DELETE of term with a course associated to it
        new_term = Term(7)
        new_term_json = new_term.to_json()
        resp = client.post('/api/v1/terms', json=new_term_json)
        new_course = Course('420-999-DW', 'Test Course', 3, 3, 3, 'Test Description', 1, 7)
        new_course_json = new_course.to_json()
        client.post('/api/v1/courses', json=new_course_json)
        resp = client.delete('/api/v1/terms/7')
        self.assertEqual(resp.status_code, 400)
        
        client.delete('/api/v1/courses/420-999-DW')
        client.delete('/api/v1/terms/7')
        
        ## Testing DELETE of nonexistent term
        resp = client.delete('/api/v1/terms/7')
        self.assertEqual(resp.status_code, 400)