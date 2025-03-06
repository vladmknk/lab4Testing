"""
Налаштування середовища для тестів behave.
"""
from unittest.mock import MagicMock
from services.service import ShippingService


def before_all(context):
    """
    Налаштування глобального контексту перед усіма тестами.
    """
    # Створюємо мок сервісу доставки, який можна використовувати в тестах
    context.shipping_service_mock = MagicMock(spec=ShippingService)
    context.shipping_service_mock.create_shipping.return_value = "shipping-123"
    context.shipping_service_mock.check_status.return_value = "in_progress"


def before_scenario(context, scenario):
    """
    Налаштування контексту перед кожним сценарієм.
    """
    # Скидаємо будь-який стан з попередніх сценаріїв
    if hasattr(context, 'product'):
        delattr(context, 'product')
    if hasattr(context, 'cart'):
        delattr(context, 'cart')
    if hasattr(context, 'order'):
        delattr(context, 'order')
    if hasattr(context, 'shipment'):
        delattr(context, 'shipment')


def after_scenario(context, scenario):
    """
    Очищення після кожного сценарію.
    """
    # Додаткове очищення, якщо потрібно
    pass 