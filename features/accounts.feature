Feature: The banking system service back-end
  As a Banking System Owner
  I need a RESTful service
  So that I can Create, Read, Update, Delete, List, Query, Deactivate accounts

  Background:
    Given the server is started

  Scenario: The server is running
    When I visit the "home page"
    Then I should see "Banking System REST API Service"
    Then I should not see "404 Not Found"

  Scenario: Create a new account
    When I post a new account to '/accounts'
      | name          | balance  | active |
      | alex          | 10   | 1          |
    Then I should see 'alex' with balance '10.00' and active: '1'

  Scenario: List all accounts
    Given a database with only following accounts
      | name |  balance | active|
      |  Xi  |  1000    | 1     |
      | John |   980    | 1     |
      | Gina |  20000   | 1     |
      |  Xi  |  20000   | 1     |
    When I visit '/accounts'
    Then I should see '1'
    And I should see '2'
    And I should see '3'
    And I should see '4'

  Scenario: Search accounts of given name
    When I search for 'Xi'
    Then I should see '1'
    And I should see '4'
    
  Scenario: Search accounts of given type
    When I search for account types '0'
    Then I should get response HTTP_200_OK

  Scenario: Get account by Id
    When I get an account with a valid id
    Then I should see an account which has that valid id

  Scenario: Deactivate an account
    When I deactivate an account with a valid id
    Then I should see an inactive account
    
  Scenario: Update an existing account details
    When I update an account details with a valid id
    | name   |  balance  | active |
    | np     |  112233	 | 0	  |
    Then I should see an account with the updated data
	
  Scenario: Delete an existing account
    Given an account exists
	When I delete that account
	Then I should receive a valid delete response
	And that account should no longer exist

  Scenario: Delete a non-existing account
	When I delete an account that does not exist
	Then I should receive a valid delete response