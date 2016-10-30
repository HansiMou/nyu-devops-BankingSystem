# run with:
# python -m unittest discover

import unittest
import json
import server

# Status Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400
HTTP_404_NOT_FOUND = 404
HTTP_409_CONFLICT = 409

######################################################################
#  T E S T   C A S E S
######################################################################
class TestBankServer(unittest.TestCase):
    idRef = -1
    def setUp(self):
        server.app.debug = True
        self.app = server.app.test_client()
        new_account = {'name': 'Gina', 'balance': 1000, 'active': 0}
        data = json.dumps(new_account)
        resp = self.app.post('/accounts', data=data, content_type='application/json')
        self.idRef = json.loads(resp.data)['id']
    def test_index(self):
        resp = self.app.get('/')
        self.assertTrue ('Bank System REST API Service' in resp.data)
        self.assertTrue( resp.status_code == HTTP_200_OK )

    def test_get_account_list(self):
        resp = self.app.get('/accounts')
        #print 'resp_data: ' + resp.data
        self.assertTrue( resp.status_code == HTTP_200_OK )
        self.assertTrue( len(resp.data) > 0 )

    def test_get_account(self):
        resp = self.app.get('/accounts/%s' %self.idRef)
        #print 'resp: ' + resp
        self.assertTrue( resp.status_code == HTTP_200_OK )
        data = json.loads(resp.data)
        self.assertTrue (data['name'] == 'Gina')
        self.assertTrue (data['balance'] == '1000')
        self.assertTrue (data['active'] == '0')

    def test_create_account(self):
        # add a new account
        new_account = {'name': 'john', 'balance': 100, 'active': 1}
        data = json.dumps(new_account)
        resp = self.app.post('/accounts', data=data, content_type='application/json')
        self.assertTrue( resp.status_code == HTTP_201_CREATED )
        new_json = json.loads(resp.data)
        self.assertTrue (new_json['name'] == 'john')
        self.assertTrue (new_json['balance'] == '100')
        self.assertTrue (new_json['active'] == '1')
        # check that count has gone up and includes sammy
        resp = self.app.get('/accounts/%s' %new_json['id'])
        # print 'resp_data(2): ' + resp.data
        data = json.loads(resp.data)
        self.assertTrue( resp.status_code == HTTP_200_OK )
        self.assertTrue( new_json == data )

    def test_update_account(self):
        new_account = {'name': 'Gina', 'balance': 999, 'active': 0}
        data = json.dumps(new_account)
        resp = self.app.put('/accounts/%s' %self.idRef, data=data, content_type='application/json')
        self.assertTrue( resp.status_code == HTTP_200_OK )
        new_json = json.loads(resp.data)
        self.assertTrue (new_json['balance'] == '999')

    def test_delete_account(self):
        # delete a pet
        resp = self.app.delete('/accounts/1', content_type='application/json')
        self.assertTrue( resp.status_code == HTTP_204_NO_CONTENT )
        self.assertTrue( len(resp.data) == 0 )
        resp = self.app.get('/accounts/1')
        self.assertTrue ( resp.status_code == HTTP_204_NO_CONTENT)

    def test_deactive_account(self):
        new_account = {'name': 'Gina', 'balance': 999, 'active': 1}
        data = json.dumps(new_account)
        resp = self.app.put('/accounts/%s/deactive' %self.idRef, data=data, content_type='application/json')
        self.assertTrue( resp.status_code == HTTP_200_OK )
        new_json = json.loads(resp.data)
        self.assertTrue (new_json['active'] == '1')

######################################################################
# Utility functions
######################################################################

    def get_account_count(self):
        # save the current number of pets
        resp = self.app.get('/accounts')
        self.assertTrue( resp.status_code == HTTP_200_OK )
        # print 'resp_data: ' + resp.data
        data = json.loads(resp.data)
        return len(data)


######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
