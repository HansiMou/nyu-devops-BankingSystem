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
from flask import Flask, Response, jsonify, request, json

# Pet Model for demo
pets = {'fido': {'name': 'fido', 'kind': 'dog'}, 'kitty': {'name': 'kitty', 'kind': 'cat'}}

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
    return jsonify(name='Pet Demo REST API Service', version='1.0', url='/pets'), HTTP_200_OK

######################################################################
# LIST ALL PETS
######################################################################
@app.route('/pets', methods=['GET'])
def list_pets():
    results = pets.values()
    kind = request.args.get('kind')
    if kind:
        results = []
        for key, value in pets.iteritems():
            if value['kind'] == kind:
                results.append(pets[key])

    return reply(results, HTTP_200_OK)

######################################################################
# RETRIEVE A PET
######################################################################
@app.route('/pets/<id>', methods=['GET'])
def get_pet(id):
    if pets.has_key(id):
        message = pets[id]
        rc = HTTP_200_OK
    else:
        message = { 'error' : 'Pet %s was not found' % id }
        rc = HTTP_404_NOT_FOUND

    return reply(message, rc)

######################################################################
# ADD A NEW PET
######################################################################
@app.route('/pets', methods=['POST'])
def create_pet():
    payload = json.loads(request.data)
    if is_valid(payload):
        id = payload['name']
        if pets.has_key(id):
            message = { 'error' : 'Pet %s already exists' % id }
            rc = HTTP_409_CONFLICT
        else:
            pets[id] = {'name': payload['name'], 'kind': payload['kind']}
            message = pets[id]
            rc = HTTP_201_CREATED
    else:
        message = { 'error' : 'Data is not valid' }
        rc = HTTP_400_BAD_REQUEST

    return reply(message, rc)

######################################################################
# UPDATE AN EXISTING PET
######################################################################
@app.route('/pets/<id>', methods=['PUT'])
def update_pet(id):
    payload = json.loads(request.data)
    if pets.has_key(id):
        pets[id] = {'name': payload['name'], 'kind': payload['kind']}
        message = pets[id]
        rc = HTTP_200_OK
    else:
        message = { 'error' : 'Pet %s was not found' % id }
        rc = HTTP_404_NOT_FOUND

    return reply(message, rc)

######################################################################
# DELETE A PET
######################################################################
@app.route('/pets/<id>', methods=['DELETE'])
def delete_pet(id):
    del pets[id];
    return '', HTTP_204_NO_CONTENT

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def reply(message, rc):
    response = Response(json.dumps(message))
    response.headers['Content-Type'] = 'application/json'
    response.status_code = rc
    return response

def is_valid(data):
    valid = False
    try:
        name = data['name']
        kind = data['kind']
        valid = True
    except KeyError as err:
        app.logger.error('Missing value error: %s', err)
    return valid

######################################################################
#   M A I N
######################################################################
if __name__ == "__main__":
    # Get bindings from the environment
    port = os.getenv('PORT', '5000')
    app.run(host='0.0.0.0', port=int(port), debug=True)
