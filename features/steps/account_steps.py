from behave import *
import server
import json

# Status Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400
HTTP_404_NOT_FOUND = 404
HTTP_409_CONFLICT = 409

@given(u'the server is started')
def step_impl(context):
    context.app = server.app.test_client()
    context.server = server
    server.connect_to_redis()

@when(u'I visit the "home page"')
def step_impl(context):
    context.resp = context.app.get('/')

@then(u'I should see "{message}"')
def step_impl(context, message):
    assert message in context.resp.data

@when(u'I post a new account to \'{url}\'')
def step_impl(context, url):
    new_account = {'name': context.table[0]['name'], 'balance': context.table[0]['balance'], 'active': context.table[0]['active']}
    context.resp = context.app.post(url, data=json.dumps(new_account), content_type='application/json')

@then(u'I should see \'{name}\' with balance \'{balance}\' and active: \'{active}\'')
def step_impl(context, name, balance, active):
    new_json = json.loads(context.resp.data)
    # check the return message and return code
    assert context.resp.status_code == HTTP_201_CREATED
    assert new_json['name'] == name
    assert new_json['balance'] == balance
    assert new_json['active'] == active

@then(u'I should not see "{message}"')
def step_impl(context, message):
    assert message not in context.resp.data
    
@when(u'I get an account with a valid id')
def step_impl(context):
    context.id = str(int(context.server.get_next_id()) - 1)
    context.resp = context.app.get('/accounts/' + context.id)

@then(u'I should see an account which has that valid id')
def step_impl(context):
    account_json = json.loads(context.resp.data)
    assert context.resp.status_code == HTTP_200_OK
    assert account_json['id'] == context.id

@when(u'I deactivate an account with a valid id')
def step_impl(context):
    context.id = str(int(context.server.get_next_id()) - 1)
    context.resp = context.app.put('/accounts/' + context.id + '/deactivate')

@then(u'I should see an inactive account')
def step_impl(context):
    account_json = json.loads(context.resp.data)
    assert context.resp.status_code == HTTP_200_OK
    assert account_json['active'] == '0'