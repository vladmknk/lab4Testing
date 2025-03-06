Feature: Order functionality
  We want to test order placement and shipping

  Scenario: Place an order with default shipping date
    Given A product with name "OrderProduct", price "30", and availability "20"
    And An empty shopping cart
    And I add product to the cart in amount "5"
    When I place a standard order with shipping type "Standard"
    Then The order should be placed successfully
    And The cart should be empty
    And The product available amount should be "15"

  Scenario: Place an order with custom shipping date
    Given A product with name "OrderProduct", price "30", and availability "20"
    And An empty shopping cart
    And I add product to the cart in amount "5"
    When I place an express order for "Express" with delivery date "tomorrow"
    Then The order should be placed successfully
    And The cart should be empty
    
  Scenario: Check shipping status
    Given A shipment with id "shipping-123"
    When I check the shipping status
    Then The shipping status should be "in_progress" 