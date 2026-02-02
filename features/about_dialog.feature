Feature: About Dialog Information
  As a user
  I want to see the About details
  So that I can contact the developer and verify the version

  Scenario: Opening the About Dialog
    Given the About Dialog is initialized
    When I show the dialog
    Then the title should be "About"
    And it should display the app name "TomodOrange"
    And it should display the developer name "Anh Nguyen (Michael)"
    And it should display a link to "https://1dragon.xyz"
