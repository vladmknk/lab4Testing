Feature: Product functionality
  We want to test product availability and buying

  Scenario: Product is available when requested amount is within availability
    Given A product with name "TestProduct", price "50", and availability "10"
    When I request availability check for "5"
    Then The availability result should be true

  Scenario: Product is not available when requested amount exceeds availability
    Given A product with name "TestProduct", price "50", and availability "10"
    When I request availability check for "15"
    Then The availability result should be false
    
  Scenario: Product is available when requested amount equals availability
    Given A product with name "TestProduct", price "50", and availability "10"
    When I request availability check for "10"
    Then The availability result should be true
    
  Scenario: Buying a product reduces its available amount
    Given A product with name "TestProduct", price "50", and availability "10"
    When I buy "5" units of the product
    Then The product available amount should be "5"
    
  Scenario: Buying more than available should fail
    Given A product with name "TestProduct", price "50", and availability "10"
    When I try to buy "15" units of the product
    Then The buying operation should fail 