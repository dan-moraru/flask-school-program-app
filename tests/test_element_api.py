import flask_unittest
from CourseManagementApp import create_app
from CourseManagementApp.db import Database
from CourseManagementApp.element import Element

class CompetencyTestAPI(flask_unittest.ClientTestCase):
    app = create_app()
    
    ## The cleanup function is required to allow some of the unit tests to be run repeatedly and consitently without failing
    ## (as they make changes such as inserts into the database)
    ## Unfortunately, the usual way of getting a Database object and setting it in g will not work in the flask unit test context.
    ## It will result in consecutive database calls to cause an error regarding working outside of the test context.
    ## We couldn't find a solution that allows keeping get_db. So the Database object is created and manually closed each time.
    def cleanup(self):
        try:
            db = Database()
            
            db.del_element_for_unit_test('420-110-DW', 'Solve Any Programming Problem', 12)
            db.del_competency('00Z6')
            
            if db is not None:
                db.close()
        except:
            if db is not None:
                db.close()
                raise Exception('Database error, cleanup incomplete. Aborting')
        
    def test_elements_get(self, client):
        ## Testing GET on elements
        resp = client.get('/api/v1/elements')
        self.assertEqual(resp.status_code, 200)
        json = resp.json
        self.assertIsNotNone(json)
        self.assertIsNotNone(json['next_page'])
        self.assertIsNone(json['previous_page'])
        self.assertEqual(json['results'][0]['element'], 'Prepare the computer.')
        
        ## Testing GET of elements with invalid page numbers
        resp = client.get('/api/v1/elements/?page=0')
        self.assertEqual(resp.status_code, 404)
        resp = client.get('/api/v1/elements/?page=5')
        self.assertEqual(resp.status_code, 404)
        
    def test_elements_post(self, client):
        try:
            self.cleanup()
        except:
            raise Exception('Database error, cleanup interrupted. The subsequent tests will likely fail as a consequence')
        
        ## Testing GET on elements
        resp = client.get('/api/v1/elements')
        self.assertEqual(resp.status_code, 200)
        json = resp.json    
        self.assertIsNotNone(json)
        self.assertEqual(json['results'][0]['element'], 'Prepare the computer.')
        
        ## Testing POST on elements
        new_element = Element(1, 'Solve Any Programming Problem', 'Under all circumstances', '00Q2')
        new_element_json = new_element.to_json()
        resp = client.post('/api/v1/elements', json=new_element_json)
        self.assertEqual(resp.status_code, 201)
        
        ## Testing POST of same element
        resp = client.post('/api/v1/elements', json=new_element_json)
        self.assertEqual(resp.status_code, 400)
        
        ## Testing POST of element with an associated competency where an element with the same name already exists
        new_element = Element(1, 'Solve Any Programming Problem', 'Under all circumstances', '00Q2')
        new_element_json = new_element.to_json()
        resp = client.post('/api/v1/elements', json=new_element_json)
        self.assertEqual(resp.status_code, 400)