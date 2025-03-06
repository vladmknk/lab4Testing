Feature: Shopping cart
  We want to test that shopping cart functionality works correctly

  Scenario: Successful add product to cart
    Given The product has availability of "123"
    And An empty shopping cart
    When I add product to the cart in amount "123"
    Then Product is added to the cart successfully

  Scenario: Failed add product to cart
    Given The product has availability of "123"
    And An empty shopping cart
    When I add product to the cart in amount "124"
    Then Product is not added to cart successfully
    
  Scenario: Calculate total for multiple products
    Given The product has availability of "50"
    And A second product with availability "30", price "20", and name "SecondProduct"
    And An empty shopping cart
    When I add product to the cart in amount "2"
    And I add the second product to the cart in amount "3"
    Then The cart total should be "80"
    
  Scenario: Remove product from cart
    Given The product has availability of "50"
    And An empty shopping cart
    When I add product to the cart in amount "5"
    And I remove the product from the cart
    Then The cart should be empty
    
  Scenario: Submit cart order
    Given The product has availability of "50"
    And An empty shopping cart
    When I add product to the cart in amount "5"
    And I submit the cart order
    Then The cart should be empty
    And The product available amount should be "45" 