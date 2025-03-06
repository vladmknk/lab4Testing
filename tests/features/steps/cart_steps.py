from behave import given, when, then
from app.eshop import Product, ShoppingCart


@given('The product has availability of "{availability}"')
def create_product_for_cart(context, availability):
    # Перетворюємо availability у число
    context.product = Product(name="any", price=123, available_amount=int(availability))


@given('A product with price "{price}" and availability "{availability}"')
def create_product_with_price(context, price, availability):
    # Перетворюємо availability та price у числа
    context.product = Product(name="any", price=float(price), available_amount=int(availability))


@given('A second product with availability "{availability}", price "{price}", and name "{name}"')
def create_second_product(context, availability, price, name):
    context.second_product = Product(name=name, price=float(price), available_amount=int(availability))


@given("An empty shopping cart")
def empty_cart(context):
    context.cart = ShoppingCart()


@when('I add product to the cart in amount "{product_amount}"')
def add_product(context, product_amount):
    try:
        context.cart.add_product(context.product, int(product_amount))
        context.add_successfully = True
    except ValueError:
        context.add_successfully = False


@when('I add the second product to the cart in amount "{product_amount}"')
def add_second_product(context, product_amount):
    try:
        context.cart.add_product(context.second_product, int(product_amount))
        context.add_successfully = True
    except ValueError:
        context.add_successfully = False


@then("Product is added to the cart successfully")
def add_successful(context):
    assert context.add_successfully == True, "Продукт має бути успішно доданий"


@then("Product is not added to cart successfully")
def add_failed(context):
    assert context.add_successfully == False, "Продукт не має бути успішно доданий"


@then('The cart total should be "{expected_total}"')
def check_cart_total(context, expected_total):
    total = context.cart.calculate_total()
    assert float(expected_total) == total, f"Очікувана загальна сума {expected_total}, отримано {total}"


@when("I remove the product from the cart")
def remove_product(context):
    context.cart.remove_product(context.product)


@then("The cart should be empty")
def check_cart_empty(context):
    assert len(context.cart.products) == 0, "Кошик має бути порожнім"


@when("I submit the cart order")
def submit_cart_order(context):
    context.product_ids = context.cart.submit_cart_order() 