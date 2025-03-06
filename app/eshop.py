from dataclasses import dataclass
from datetime import datetime
from time import timezone
from typing import Dict
import uuid

from services.service import ShippingService


@dataclass()
class Product:
    available_amount: int
    name: str
    price: float

    def __init__(self, name, price, available_amount):
        self.name = name
        self.price = float(price)
        try:
            self.available_amount = int(available_amount)
        except Exception:
            raise ValueError("available_amount must be an integer")

    def is_available(self, requested_amount):
        try:
            requested = int(requested_amount)
        except Exception:
            raise ValueError("requested_amount must be an integer")
        return self.available_amount >= requested

    def buy(self, requested_amount):
        requested = int(requested_amount)
        if self.available_amount < requested:
            raise ValueError("Not enough product available")
        self.available_amount -= requested

    def __eq__(self, other):
        return isinstance(other, Product) and self.name == other.name

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.name


@dataclass()
class ShoppingCart:
    products: Dict[Product, int]

    def __init__(self):
        self.products = dict()

    def contains_product(self, product):
        return product in self.products

    def calculate_total(self):
        return sum([p.price * count for p, count in self.products.items()])

    def add_product(self, product: Product, amount):
        try:
            amt = int(amount)
        except Exception:
            raise ValueError("Amount must be an integer")
        if amt <= 0:
            raise ValueError("Amount must be positive")
        if not product.is_available(amt):
            raise ValueError(
                f"Product {product} has only {product.available_amount} items"
            )
        self.products[product] = amt

    def remove_product(self, product):
        if product in self.products:
            del self.products[product]

    def submit_cart_order(self):
        product_ids = []
        for product, count in self.products.items():
            product.buy(count)
            product_ids.append(str(product))
        self.products.clear()

        return product_ids


@dataclass()
class Order:
    cart: ShoppingCart
    shipping_service: ShippingService
    order_id: str = str(uuid.uuid4())

    def place_order(self, shipping_type, due_date: datetime = None):
        if not due_date:
            due_date = datetime.now(timezone.utc) + timedelta(seconds=3)
        product_ids = self.cart.submit_cart_order()
        print(due_date)
        return self.shipping_service.create_shipping(
            shipping_type, product_ids, self.order_id, due_date
        )


@dataclass()
class Shipment:
    shipping_id: str
    shipping_service: ShippingService

    def check_shipping_status(self):
        return self.shipping_service.check_status(self.shipping_id)
