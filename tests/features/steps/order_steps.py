from behave import given, when, then
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock
from app.eshop import Order, Shipment
from services.service import ShippingService


@given('I add product to the cart in amount "{amount}"')
def add_product_to_cart(context, amount):
    context.cart.add_product(context.product, int(amount))


@when('I place an order with shipping type "{shipping_type}"')
def place_order(context, shipping_type):
    # Створюємо мок сервісу доставки
    context.shipping_service = MagicMock(spec=ShippingService)
    context.shipping_service.create_shipping.return_value = "shipping-123"
    
    # Створюємо та розміщуємо замовлення
    context.order = Order(cart=context.cart, shipping_service=context.shipping_service)
    context.shipping_id = context.order.place_order(shipping_type)


@when('I place an order with shipping type "{shipping_type}" and due date "{due_date_str}"')
def place_order_with_due_date(context, shipping_type, due_date_str):
    # Створюємо мок сервісу доставки
    context.shipping_service = MagicMock(spec=ShippingService)
    context.shipping_service.create_shipping.return_value = "shipping-123"
    
    # Розбираємо дату доставки
    if due_date_str == "tomorrow":
        due_date = datetime.now(timezone.utc) + timedelta(days=1)
    else:
        due_date = datetime.now(timezone.utc) + timedelta(seconds=10)
    
    # Створюємо та розміщуємо замовлення
    context.order = Order(cart=context.cart, shipping_service=context.shipping_service)
    context.shipping_id = context.order.place_order(shipping_type, due_date)


@then("The order should be placed successfully")
def order_placed_successfully(context):
    assert context.shipping_id == "shipping-123", "Замовлення має бути успішно розміщене"


@given('A shipment with id "{shipping_id}"')
def create_shipment(context, shipping_id):
    context.shipping_service = MagicMock(spec=ShippingService)
    context.shipping_service.check_status.return_value = "in_progress"
    context.shipment = Shipment(shipping_id=shipping_id, shipping_service=context.shipping_service)


@when("I check the shipping status")
def check_shipping_status(context):
    context.shipping_status = context.shipment.check_shipping_status()


@then('The shipping status should be "{expected_status}"')
def verify_shipping_status(context, expected_status):
    assert context.shipping_status == expected_status, f"Очікуваний статус доставки {expected_status}, отримано {context.shipping_status}" 