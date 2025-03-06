from behave import given, when, then
from app.eshop import Product


@given(
    'A product with name "{name}", price "{price}", and availability "{availability}"'
)
def step_create_product(context, name, price, availability):
    context.product = Product(name, float(price), int(availability))


@when('I request availability check for "{requested_amount}"')
def step_check_product_availability(context, requested_amount):
    try:
        requested = int(requested_amount)
        context.availability_result = context.product.is_available(requested)
    except Exception:
        context.availability_result = None


@then("The availability result should be {result}")
def step_verify_product_availability(context, result):
    expected = result.lower() == "true"
    assert (
        context.availability_result == expected
    ), f"Очікувалося {expected}, але отримано {context.availability_result}"


@when('I buy "{buy_amount}" units of the product')
def step_buy_product(context, buy_amount):
    try:
        context.product.buy(buy_amount)
        context.buy_success = True
    except Exception:
        context.buy_success = False


@when('I try to buy "{buy_amount}" units of the product')
def step_try_buy_product(context, buy_amount):
    try:
        context.product.buy(buy_amount)
        context.buy_success = True
    except Exception:
        context.buy_success = False


@then('The product available amount should be "{expected_amount}"')
def step_check_available_amount(context, expected_amount):
    assert (
        str(context.product.available_amount) == expected_amount
    ), f"Очікувана кількість {expected_amount}, отримано {context.product.available_amount}"


@then("The buying operation should fail")
def step_buying_should_fail(context):
    assert context.buy_success == False, "Очікувалося, що операція купівлі не вдасться" 