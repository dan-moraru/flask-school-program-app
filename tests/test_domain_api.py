import flask_unittest
from CourseManagementApp import create_app
from CourseManagementApp.db import Database
from CourseManagementApp.domain import Domain

class DomainTestAPI(flask_unittest.ClientTestCase):
    app = create_app()
    
    ## The cleanup function is required to allow some of the unit tests to be run repeatedly and consitently without failing
    ## (as they make changes such as inserts into the database)
    ## Unfortunately, the usual way of getting a Database object and setting it in g will not work in the flask unit test context.
    ## It will result in consecutive database calls to cause an error regarding working outside of the test context.
    ## We couldn't find a solution that allows keeping get_db. So the Database object is created and manually closed each time.
    def cleanup(self):
        try:
            db = Database()
            
            db.del_domain_for_unit_test('New Computer Science Domain')
            
            if db is not None:
                db.close()
        except:
            if db is not None:
                db.close()
                raise Exception('Database error, cleanup incomplete. Aborting')
    
    def test_domains_get(self, client):
        ## Testing GET on domains
        resp = client.get('/api/v1/domains')
        self.assertEqual(resp.status_code, 200)
        json = resp.json
        self.assertIsNotNone(json)
        self.assertIsNone(json['next_page'])
        self.assertIsNone(json['previous_page'])
        self.assertEqual(json['results'][0]['domain'], 'Programming, Data Structures, and Algorithms')
        
        ## Testing GET on domains with invalid page numbers
        resp = client.get('/api/v1/domains/?page=0')
        self.assertEqual(resp.status_code, 404)
        resp = client.get('/api/v1/domains/?page=2')
        self.assertEqual(resp.status_code, 404)
        
    def test_domains_post(self, client):
        try:
            self.cleanup()
        except:
            raise Exception('Database error, cleanup interrupted. The subsequent tests will likely fail as a consequence')
        
        ## Testing GET on domains
        resp = client.get('/api/v1/domains')
        self.assertEqual(resp.status_code, 200)
        json = resp.json
        self.assertIsNotNone(json)
        self.assertEqual(json['results'][0]['domain'], 'Programming, Data Structures, and Algorithms')
        
        ## Testing POST on domains
        new_domain = Domain('New Computer Science Domain', 'Information is To Be Announced')
        new_domain_json = new_domain.to_json()
        resp = client.post('/api/v1/domains', json=new_domain_json)
        self.assertEqual(resp.status_code, 201)
        
        ## Testing POST of same domain
        resp = client.post('/api/v1/domains', json=new_domain_json)
        self.assertEqual(resp.status_code, 400)