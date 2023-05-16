import flask_unittest
from CourseManagementApp import create_app
from CourseManagementApp.db import Database
from CourseManagementApp.competency import Competency
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
            
    def delete_element(self):
        try:
            db = Database()
            
            db.del_element_for_unit_test('420-110-DW', 'Solve Any Programming Problem', 12)
            
            if db is not None:
                db.close()
        except:
            if db is not None:
                db.close()
                raise Exception('Database error. Aborting')

    def test_competencies_get(self, client):
            ## Testing GET on competencies
            resp = client.get('/api/v1/competencies')
            self.assertEqual(resp.status_code, 200)
            json = resp.json
            self.assertIsNotNone(json)
            self.assertIsNone(json['next_page'])
            self.assertIsNone(json['previous_page'])
            self.assertEqual(json['results'][0]['competency_id'], '00Q1')
            
            ## Testing GET on competencies with invalid page numbers
            resp = client.get('/api/v1/competencies/?page=0')
            self.assertEqual(resp.status_code, 404)
            resp = client.get('/api/v1/competencies/?page=2')
            self.assertEqual(resp.status_code, 404)
            
    def test_competencies_post(self, client):
        try:
            self.cleanup()
        except:
            raise Exception('Database error, cleanup interrupted. The subsequent tests will likely fail as a consequence')
        
        ## Testing GET on competencies
        resp = client.get('/api/v1/competencies')
        self.assertEqual(resp.status_code, 200)
        json = resp.json    
        self.assertIsNotNone(json)
        self.assertEqual(json['results'][0]['competency_id'], '00Q1')
        
        ## Testing POST on competencies with valid data
        new_competency = Competency('00Z6', 'Assess Coding Roadblocks', 'In theoretical and practical settings', 'Mandatory')
        new_element = Element(1, 'Solve Any Programming Problem', 'Under all circumstances', '00Z6')
        new_competency_json = new_competency.to_json(new_element)
        resp = client.post('/api/v1/competencies', json=new_competency_json)
        self.assertEqual(resp.status_code, 201)
        
        ## Testing POST on competencies with the same competency object
        resp = client.post('/api/v1/competencies', json=new_competency_json)
        self.assertEqual(resp.status_code, 400)
        
        ## Testing POST on competencies where new competency's competency id doesn't match accompanying element's competency id
        new_competency = Competency('009Z', 'Assess Coding Roadblocks', 'In theoretical and practical settings', 'Mandatory')
        new_element = Element(1, 'Solve Any Programming Problem', 'Under all circumstances', '00Z0')
        new_competency_json = new_competency.to_json(new_element)
        resp = client.post('/api/v1/competencies', json=new_competency_json)
        self.assertEqual(resp.status_code, 400)

    def test_competency_by_id_get(self, client):
        ## Testing GET on competency with valid competency id
        resp = client.get('/api/v1/competencies/00Q2')
        self.assertEqual(resp.status_code, 200)
        json = resp.json
        self.assertIsNotNone(json)
        self.assertEqual(json['competency_id'], '00Q2')
        
        ## Testing GET on competency with invalid competency id
        resp = client.get('/api/v1/competencies/00QH')
        self.assertEqual(resp.status_code, 404)
        
    def test_competency_by_id_put(self, client):
        try:
            self.cleanup()
        except:
            raise Exception('Database error, cleanup interrupted. The subsequent tests will likely fail as a consequence')
        
        ## Testing PUT on competency, adding new competency
        new_competency = Competency('00Z6', 'Assess Coding Roadblocks', 'In theoretical and practical settings', 'Mandatory')
        new_element = Element(1, 'Solve Any Programming Problem', 'Under all circumstances', '00Z6')
        new_competency_json = new_competency.to_json(new_element)
        resp = client.put('/api/v1/competencies/00Z6', json=new_competency_json)
        self.assertEqual(resp.status_code, 201)
        
        ## Testing GET on that new competency
        resp = client.get('/api/v1/competencies/00Z6')
        json = resp.json
        self.assertEqual(json['competency_id'], '00Z6')
        
        ## Testing PUT with same competency, resulting in update
        new_competency_json['competency'] = 'Assess Other Roadblocks'
        resp = client.put('/api/v1/competencies/00Z6', json=new_competency_json)
        self.assertEqual(resp.status_code, 201)
        
        ## Testing GET on that same competency, checking its updated detail
        resp = client.get('/api/v1/competencies/00Z6')
        json = resp.json
        self.assertEqual(json['competency'], 'Assess Other Roadblocks')
        
        ## Testing PUT on competency, where competency and element have mismatching competency ids
        new_competency = Competency('00ZZ', 'Assess Coding Roadblocks', 'In theoretical and practical settings', 'Mandatory')
        new_element = Element(1, 'Solve Any Programming Problem', 'Under all circumstances', 'Z0Z6')
        new_competency_json = new_competency.to_json(new_element)
        resp = client.put('/api/v1/competencies/00Z6', json=new_competency_json)
        self.assertEqual(resp.status_code, 400)
        
    def test_competency_by_id_delete(self, client):
        try:
            self.cleanup()
        except:
            raise Exception('Database error, cleanup interrupted. The subsequent tests will likely fail as a consequence')
        
        ## Testing POST of new competency
        new_competency = Competency('00Z6', 'Assess Coding Roadblocks', 'In theoretical and practical settings', 'Mandatory')
        new_element = Element(1, 'Solve Any Programming Problem', 'Under all circumstances', '00Z6')
        new_competency_json = new_competency.to_json(new_element)
        resp = client.post('/api/v1/competencies', json=new_competency_json)
        self.assertEqual(resp.status_code, 201)
        
        ## Testing DELETE on a competency with a linked element, which is not permitted by the foreign key constraints.
        resp = client.delete('/api/v1/competencies/00Z6')
        self.assertEqual(resp.status_code, 400)
        
        ## Testing DELETE after deleting the element
        try:
            self.delete_element()
        except:
            raise Exception('Database error, delete operation interrupted. The subsequent test will likely fail as a consequence')
        resp = client.delete('/api/v1/competencies/00Z6')
        self.assertEqual(resp.status_code, 204)
        
        ## Testing DELETE on a nonexistent competency
        resp = client.delete('/api/v1/competencies/00ZZ')
        self.assertEqual(resp.status_code, 400)

    def test_competency_elements_get(self, client):
        ## Testing GET on competency elements
        resp = client.get('/api/v1/competencies/00Q2/elements')
        self.assertEqual(resp.status_code, 200)
        json = resp.json
        self.assertIsNotNone(json)
        self.assertIsNone(json['next_page'])
        self.assertIsNone(json['previous_page'])
        self.assertEqual(json['results'][0]['element'], 'Analyze the problem.')
        
        ## Testing GET on competency elements of nonexistent competency
        resp = client.get('/api/v1/competencies/00QH/elements')
        self.assertEqual(resp.status_code, 404)
        
        ## Testing GET of elements with invalid page numbers
        resp = client.get('/api/v1/competencies/00Q2/elements/?page=0')
        self.assertEqual(resp.status_code, 404)
        resp = client.get('/api/v1/competencies/00Q2/elements/?page=2')
        self.assertEqual(resp.status_code, 404)
        
    def test_competency_elements_post(self, client):
        try:
            self.cleanup()
        except:
            raise Exception('Database error, cleanup interrupted. The subsequent tests will likely fail as a consequence')
        
        ## Testing GET on competency elements
        resp = client.get('/api/v1/competencies/00Q2/elements')
        self.assertEqual(resp.status_code, 200)
        json = resp.json    
        self.assertIsNotNone(json)
        self.assertEqual(json['results'][0]['element'], 'Analyze the problem.')
        
        ## Testing POST on competency elements
        new_element = Element(1, 'Solve Any Programming Problem', 'Under all circumstances', '00Q2')
        new_element_json = new_element.to_json()
        resp = client.post('/api/v1/competencies/00Q2/elements', json=new_element_json)
        self.assertEqual(resp.status_code, 201)
        
        ## Testing POST of same element
        resp = client.post('/api/v1/competencies/00Q2/elements', json=new_element_json)
        self.assertEqual(resp.status_code, 400)
        
        ## Testing POST of competency element with competency id mismatching url competency id
        new_element = Element(1, 'Solve Any Programming Problem', 'Under all circumstances', '0ZZ2')
        new_element_json = new_element.to_json()
        resp = client.post('/api/v1/competencies/00Q2/elements', json=new_element_json)
        self.assertEqual(resp.status_code, 400)
        
        ## Testing POST of competency element with nonexistent url competency id
        new_element = Element(1, 'Solve Any Programming Problem', 'Under all circumstances', '0ZZ2')
        new_element_json = new_element.to_json()
        resp = client.post('/api/v1/competencies/0ZZ8/elements', json=new_element_json)
        self.assertEqual(resp.status_code, 400)
        
        ## Testing POST of competency element with an associated competency where an element with the same name already exists
        new_element = Element(1, 'Solve Any Programming Problem', 'Under all circumstances', '00Q2')
        new_element_json = new_element.to_json()
        resp = client.post('/api/v1/competencies/00Q2/elements', json=new_element_json)
        self.assertEqual(resp.status_code, 400)