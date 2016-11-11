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
    Then I should see 'alex' with balance '10' and active: '1'
	
  Scenario: Get account by Id
    When I get an account with a valid id
	Then I should see an account which has that valid id

  Scenario: Deactivate an account
    When I deactivate an account with a valid id
    Then I should see an inactive account