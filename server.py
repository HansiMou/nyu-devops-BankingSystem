# Copyright 2016 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import redis
from flask import Flask, Response, jsonify, request, json

# Get bindings from the environment
if 'VCAP_SERVICES' in os.environ:
    VCAP_SERVICES = os.environ['VCAP_SERVICES']
    services = json.loads(VCAP_SERVICES)
    redis_creds = services['rediscloud'][0]['credentials']
    # pull out the fields we need
    redis_hostname = redis_creds['hostname']
    redis_port = int(redis_creds['port'])
    redis_password = redis_creds['password']
else:
    redis_hostname = '127.0.0.1'
    redis_port = 6379
    redis_password = None
redis_server = redis.Redis(host=redis_hostname, port=redis_port, password=redis_password)

# Create Flask application
app = Flask(__name__)

# Status Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400
HTTP_404_NOT_FOUND = 404
HTTP_409_CONFLICT = 409

######################################################################
# GET INDEX
######################################################################
@app.route('/')
def index():
    return jsonify(name='Bank System REST API Service', version='1.0', url='/accounts'), HTTP_200_OK

######################################################################
# LIST ALL ACCOUNTS WITHOUT A CERTAIN NAME :/accounts
# LIST ALL ACCOUNTS WITH A CERTAIN NAME: /accounts?name=john
######################################################################
@app.route('/accounts', methods=['GET'])
def list_accounts():
    name = request.args.get('name')
    if name:
        message = []
        for key in redis_server.keys():
            account = redis_server.hgetall(key)
            if account.has_key('name'):
                if account.get('name')==name:
                    message.append(account)
                    rc = HTTP_200_OK
        if message:
            return reply(message, rc)
        message = { 'error' : 'Account under name: %s was not found' % name }
        rc = HTTP_404_NOT_FOUND
        return reply(message, rc)
    else :
        message = []
        for key in redis_server.keys():
            account = redis_server.hgetall(key)
            message.append(account)
            rc = HTTP_200_OK
        if message:
            return reply(message, rc)
        message = { 'error' : 'No account was not found'}
        rc = HTTP_404_NOT_FOUND
        return reply(message, rc)

######################################################################
# RETRIEVE AN ACCOUNT WITH ID
######################################################################
@app.route('/accounts/<id>', methods=['GET'])
def get_account_by_id(id):
    if (redis_server.exists(id)):
        message = redis_server.hgetall(id)
        rc = HTTP_200_OK
        return reply(message, rc)

    message = { 'error' : 'Account id: %s was not found' % id }
    rc = HTTP_204_NO_CONTENT
    return reply(message, rc)

######################################################################
# DEACTIVE/ACTIVE AN ACCOUNT WITH ID
######################################################################
@app.route('/accounts/<id>/deactive', methods=['PUT'])
def deactive_account_by_id(id):
    payload = json.loads(request.data)
    for account in redis_server.keys():
        if account == (id):
            redis_server.hset(id,  'active', payload['active'])
            message = redis_server.hgetall(account)
            rc = HTTP_200_OK
            return reply(message, rc)

    message = { 'error' : 'Account id: %s was not found' % id }
    rc = HTTP_404_NOT_FOUND
    return reply(message, rc)

######################################################################
# CREATE AN ACCOUNT
######################################################################
@app.route('/accounts', methods=['POST'])
def create_account():
    payload = json.loads(request.data)
    if is_valid(payload):
        #global idMax
        idTemp = redis_server.hget('idMax','idMax')
        if redis_server.exists(idTemp):
            message = { 'error' : 'Account id: %s already exists. Simpy try again' % idTemp }
            rc = HTTP_409_CONFLICT
            return reply(message, rc)

        name = payload['name']
        balance = payload['balance']
        active = payload['active']
        redis_server.hset(idTemp,  'id', idTemp)
        redis_server.hset(idTemp,  'name', name)
        redis_server.hset(idTemp,  'balance', balance)
        redis_server.hset(idTemp,  'active', active)
        message = redis_server.hgetall(idTemp)
        redis_server.hset('idMax','idMax',int(idTemp) + 1)
        rc = HTTP_201_CREATED
    else:
        message = { 'error' : 'Data is not valid' }
        rc = HTTP_400_BAD_REQUEST

    return reply(message, rc)

######################################################################
# UPDATE AN EXISTING ACCOUNT
######################################################################
@app.route('/accounts/<id>', methods=['PUT'])
def update_account(id):
    payload = json.loads(request.data)
    if redis_server.exists(id):
        redis_server.hmset(id, payload)
        message = redis_server.hgetall(id)
        rc = HTTP_200_OK
    else:
        message = { 'error' : 'Account id: %s was not found' % id }
        rc = HTTP_404_NOT_FOUND

    return reply(message, rc)

######################################################################
# DELETE AN ACCOUNT
######################################################################
@app.route('/accounts/<id>', methods=['DELETE'])
def delete_account(id):
    if redis_server.exists(id):
        redis_server.delete(id)

    return '', HTTP_204_NO_CONTENT

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def reply(message, rc):
    response = Response(json.dumps(message))
    response.headers['Content-Type'] = 'application/json'
    response.status_code = rc
    return response

# NEED ALL FOUR FIELDS TO BE NOT NULL: name, id, balance, active
def is_valid(data):
    valid = False
    try:
        active = data['active']
        balance = data['balance']
        name = data['name']
        valid = True
    except KeyError as err:
        app.logger.error('Missing value error: %s', err)
    return valid

######################################################################
#   M A I N
######################################################################
if __name__ == "__main__":
    # Get bindings from the environment
    if not redis_server.exists('idMax'):
        redis_server.hset('idMax','idMax',len(redis_server.keys()) + 1)
    port = os.getenv('PORT', '5000')
    app.run(host='0.0.0.0', port=int(port), debug=True)
