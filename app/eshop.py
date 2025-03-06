"""
E-commerce module providing functionality for an online shop.
This module contains classes for products, shopping carts, orders, and shipments.
"""
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Dict, List
import uuid

from services.service import ShippingService


@dataclass()
class Product:
    """
    Represents a product in the e-shop with its properties and available quantity.
    
    Attributes:
        available_amount: Number of items available in stock
        name: Name of the product
        price: Price of the product
    """
    available_amount: int
    name: str
    price: float

    def __init__(self, name, price, available_amount):
        """
        Initialize a new Product instance.
        
        Args:
            name: Name of the product
            price: Price of the product
            available_amount: Number of items available in stock
        
        Raises:
            ValueError: If available_amount cannot be converted to an integer
        """
        self.name = name
        self.price = float(price)
        try:
            self.available_amount = int(available_amount)
        except Exception as exc:
            raise ValueError("available_amount must be an integer") from exc

    def is_available(self, requested_amount):
        """
        Check if the requested amount of product is available.
        
        Args:
            requested_amount: Amount of product requested
            
        Returns:
            bool: True if requested amount is available, False otherwise
            
        Raises:
            ValueError: If requested_amount cannot be converted to an integer
        """
        try:
            requested = int(requested_amount)
        except Exception as exc:
            raise ValueError("requested_amount must be an integer") from exc
        return self.available_amount >= requested

    def buy(self, requested_amount):
        """
        Reduce the available amount of product by the requested amount.
        
        Args:
            requested_amount: Amount of product to buy
            
        Raises:
            ValueError: If not enough product is available
        """
        requested = int(requested_amount)
        if self.available_amount < requested:
            raise ValueError("Not enough product available")
        self.available_amount -= requested

    def __eq__(self, other):
        """Check if two products are equal based on their names."""
        return isinstance(other, Product) and self.name == other.name

    def __ne__(self, other):
        """Check if two products are not equal."""
        return not self.__eq__(other)

    def __hash__(self):
        """Generate hash based on product name."""
        return hash(self.name)

    def __str__(self):
        """Return string representation of the product."""
        return self.name


@dataclass()
class ShoppingCart:
    """
    Represents a shopping cart containing products and their quantities.
    
    Attributes:
        products: Dictionary mapping Product objects to their quantities
    """
    products: Dict[Product, int]

    def __init__(self):
        """Initialize an empty shopping cart."""
        self.products = {}

    def contains_product(self, product):
        """
        Check if a product is in the cart.
        
        Args:
            product: The product to check for
            
        Returns:
            bool: True if the product is in the cart, False otherwise
        """
        return product in self.products

    def calculate_total(self):
        """
        Calculate the total price of all products in the cart.
        
        Returns:
            float: The total price
        """
        return sum(p.price * count for p, count in self.products.items())

    def add_product(self, product: Product, amount):
        """
        Add a product to the cart.
        
        Args:
            product: The product to add
            amount: The quantity to add
            
        Raises:
            ValueError: If amount is not a positive integer or if not enough product is available
        """
        try:
            amt = int(amount)
        except Exception as exc:
            raise ValueError("Amount must be an integer") from exc
        if amt <= 0:
            raise ValueError("Amount must be positive")
        if not product.is_available(amt):
            raise ValueError(
                f"Product {product} has only {product.available_amount} items"
            )
        self.products[product] = amt

    def remove_product(self, product):
        """
        Remove a product from the cart.
        
        Args:
            product: The product to remove
        """
        if product in self.products:
            del self.products[product]

    def submit_cart_order(self):
        """
        Submit the cart as an order, reducing product availability.
        
        Returns:
            List[str]: List of product names in the order
        """
        product_ids = []
        for product, count in self.products.items():
            product.buy(count)
            product_ids.append(str(product))
        self.products.clear()

        return product_ids


@dataclass()
class Order:
    """
    Represents an order with a shopping cart and shipping information.
    
    Attributes:
        cart: The shopping cart for this order
        shipping_service: Service to handle shipping
        order_id: Unique identifier for the order
    """
    cart: ShoppingCart
    shipping_service: ShippingService
    order_id: str = str(uuid.uuid4())

    def place_order(self, shipping_type, due_date: datetime = None):
        """
        Place the order and create a shipping request.
        
        Args:
            shipping_type: Type of shipping to use
            due_date: Due date for the shipping, defaults to 3 seconds from now
            
        Returns:
            The result of creating a shipping request
        """
        if not due_date:
            due_date = datetime.now(timezone.utc) + timedelta(seconds=3)
        product_ids = self.cart.submit_cart_order()
        print(due_date)
        return self.shipping_service.create_shipping(
            shipping_type, product_ids, self.order_id, due_date
        )


@dataclass()
class Shipment:
    """
    Represents a shipment of products.
    
    Attributes:
        shipping_id: Unique identifier for the shipment
        shipping_service: Service to handle shipping
    """
    shipping_id: str
    shipping_service: ShippingService

    def check_shipping_status(self):
        """
        Check the status of the shipment.
        
        Returns:
            The status of the shipment
        """
        return self.shipping_service.check_status(self.shipping_id)
