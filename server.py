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
import re
from redis.exceptions import ConnectionError
from flask import Flask, Response, jsonify, request, json

# Create Flask application
app = Flask(__name__)

# Status Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400
HTTP_403_ACCESS_FORBIDDEN = 403
HTTP_404_NOT_FOUND = 404
HTTP_409_CONFLICT = 409

######################################################################
# GET INDEX
######################################################################
@app.route('/')
def index():
    return jsonify(name='Banking System REST API Service', version='1.0', url='/accounts'), HTTP_200_OK

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
        if not message:
            message = { 'error' : 'Account under name: %s is not found' % name }
            rc = HTTP_404_NOT_FOUND
    else :
        message = []
        rc = HTTP_200_OK
        for key in redis_server.keys():
            if (key == 'nextId'):
                continue
            account = redis_server.hgetall(key)
            message.append(account)
    return reply(message, rc)

######################################################################
# RETRIEVE AN ACCOUNT WITH ID
######################################################################
@app.route('/accounts/<id>', methods=['GET'])
def get_account_by_id(id):
    message = []
    if id == 'nextId':
        message = {'error' : 'Account id: %s is not found' % id }
        rc = HTTP_404_NOT_FOUND
    elif redis_server.exists(id):
        message = redis_server.hgetall(id)
        rc = HTTP_200_OK
    if not message:
        message = { 'error' : 'Account id: %s is not found' % id }
        rc = HTTP_404_NOT_FOUND
    return reply(message, rc)

######################################################################
# DEACTIVATE AN ACCOUNT WITH ID
######################################################################
# the link used to be /accounts/<id>/deactive, which should be /accounts/<id>/deactivate
# /accounts/<id>/deactive is still used in the bluemix link
# It will be corrected in the hw2
@app.route('/accounts/<id>/deactivate', methods=['PUT'])
def deactivate_account_by_id(id):
    message = []
    for account in redis_server.keys():
        if account == 'nextId':
            continue
        if account == id:
            redis_server.hset(id, 'active', 0)
            message = redis_server.hgetall(account)
            rc = HTTP_200_OK

    if not message:
        message = { 'error' : 'Account id: %s is not found' % id }
        rc = HTTP_404_NOT_FOUND
    return reply(message, rc)

######################################################################
# CREATE AN ACCOUNT
######################################################################
@app.route('/accounts', methods=['POST'])
def create_account():
    payload = json.loads(request.data)
    missing_params = find_missing_params(payload)
    if not missing_params:
        #validations here
        validated_balance = validate_balance(payload['balance'])
        
        if validated_balance[0] is 'false':
            message = {'error' : validated_balance[1]}
            rc = HTTP_400_BAD_REQUEST
            return reply(message, rc)
        
        #end validations
        
        id = redis_server.hget('nextId', 'nextId')
        redis_server.hset('nextId','nextId',int(id) + 1)
        redis_server.hset(id, 'id', id)
        redis_server.hset(id, 'name',  payload['name'])
        redis_server.hset(id, 'balance', validated_balance[2])    
        redis_server.hset(id, 'active', payload['active'])

        message = redis_server.hgetall(id)
        rc = HTTP_201_CREATED
    else:
        message = { 'error' : 'Missing %s' % missing_params }
        rc = HTTP_400_BAD_REQUEST

    return reply(message, rc)

######################################################################
# UPDATE AN EXISTING ACCOUNT
######################################################################
@app.route('/accounts/<id>', methods=['PUT'])
def update_account(id):
    payload = json.loads(request.data)
    if id == 'nextId':
        message = {'error' : 'Account %s is not found' % id}
        rc = HTTP_404_NOT_FOUND
    elif find_missing_params(payload):
        message = { 'error' : 'Missing %s' % find_missing_params(payload) }
        rc = HTTP_400_BAD_REQUEST
    elif redis_server.exists(id):
        #validation
        validated_balance = validate_balance(payload['balance'])
        
        if validated_balance[0] is 'false':
            message = {'error' : validated_balance[1]}
            rc = HTTP_400_BAD_REQUEST
            return reply(message, rc)
        #end validation
        
        redis_server.hset(id, 'name', payload['name'])
        redis_server.hset(id, 'active', payload['active'])
        redis_server.hset(id, 'balance', validated_balance[2])
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

# NEED THREE FIELDS TO BE NOT NULL: name, balance, active
def find_missing_params(data):
    missing_params = []
    if not data.has_key('active'):
        missing_params.append('active')
    if not data.has_key('balance'):
        missing_params.append('balance')
    if not data.has_key('name'):
        missing_params.append('name')
    return missing_params
    
# Returns a list - first element is whether it passed validation, second is message, third is transformed data    
def validate_balance(balance):
    
    balance = str(balance)
    
    is_a_number = re.compile("^(-)?((((\d){1,3},(\d){1,3})+(,(\d){1,3})?(\.(\d)+))|((\d)+(\.)*(\d)+)|(\d)+)$")
    
    if is_a_number.match(balance):
        is_negative = re.compile("^-(.)*$")
        
        if is_negative.match(balance):
            return ('false', 'Negative balances not allowed', balance)
            
        too_many_decimals = re.compile("^(\d)*\.(\d){3,}$")
        
        if too_many_decimals.match(balance):
            return ('false', 'More than two digits after the decimal', balance)
            
        if ',' in balance:
            balance = re.sub(',', '', balance)
            
        is_an_int = re.compile("^(\d+)$")
        
        if is_an_int.match(balance):
            balance += '.0'
            
        too_few_decimals = re.compile("^(\d)*\.\d$")
        
        if too_few_decimals.match(balance):
            balance += '0'
            
        return ("true", "processed", balance)
    else:
        return ('false', 'Not a valid number', balance)

######################################################################
# Connect to Redis and catch connection exceptions
######################################################################
def connect_to_redis(hostname, port, password):
    try:
    	redis_server = redis.Redis(host=hostname, port=port, password=password)
    	redis_server.ping()
    except Exception:
    	redis_server = None
    	return redis_server
    if not redis_server.exists('nextId'):
        redis_server.hset('nextId','nextId',len(redis_server.keys()) + 1)
    return redis_server


######################################################################
# INITIALIZE Redis
# This method will work in the following conditions:
#   1) In Bluemix with Redsi bound through VCAP_SERVICES
#   2) With Redis running on the local server as with Travis CI
#   3) With Redis --link ed in a Docker container called 'redis'
######################################################################
def inititalize_redis():
    global redis_server
    redis_server = None
    # Get the crdentials from the Bluemix environment
    if 'VCAP_SERVICES' in os.environ:
        print "Using VCAP_SERVICES..."
        VCAP_SERVICES = os.environ['VCAP_SERVICES']
        services = json.loads(VCAP_SERVICES)
        creds = services['rediscloud'][0]['credentials']
        print "Conecting to Redis on host %s port %s" % (creds['hostname'], creds['port'])
        redis_server = connect_to_redis(creds['hostname'], creds['port'], creds['password'])
    else:
        print "VCAP_SERVICES not found, checking localhost for Redis"
        redis_server = connect_to_redis('127.0.0.1', 6379, None)
        if not redis_server:
            print "No Redis on localhost, pinging: redis"
            response = os.system("ping -c 1 redis")
            if response == 0:
                print "Connecting to remote: redis"
                redis_server = connect_to_redis('redis', 6379, None)
    if not redis_server:
        # if you end up here, redis instance is down.
        print '*** FATAL ERROR: Could not connect to the Redis Service'
        exit(1)


# Get the next ID
def get_next_id():
    return redis_server.hget('nextId', 'nextId')


######################################################################
#   M A I N
######################################################################
if __name__ == "__main__":
    inititalize_redis()
    # this line is used to empty database
    # redis_server.flushdb()
    # Get bindings from the environment
    port = os.getenv('PORT', '5000')
    app.run(host='0.0.0.0', port=int(port), debug=True)
