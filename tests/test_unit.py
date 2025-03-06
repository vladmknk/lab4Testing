import unittest
from unittest.mock import MagicMock
from app.eshop import Product, Shipment, ShoppingCart, Order
from services.service import ShippingService


class TestProduct(unittest.TestCase):
    def setUp(self):
        # Створюємо продукт з початковою кількістю 20
        self.product = Product(name="TestProduct", price=10.0, available_amount=20)

    def test_is_available_true(self):
        # Arrange: запитуємо 5 одиниць продукту
        result = self.product.is_available(5)
        self.assertTrue(result, "Продукт має бути доступний для 5 одиниць")

    def test_is_available_false(self):
        # Запитуємо кількість, яка перевищує наявну
        self.assertFalse(
            self.product.is_available(25),
            "Продукт не має бути доступний для 25 одиниць",
        )

    def test_buy_reduces_amount(self):
        # Купуємо 5 одиниць
        self.product.buy(5)
        self.assertEqual(
            self.product.available_amount, 15, "Після покупки залишилось 15 одиниць"
        )

    def test_buy_insufficient_amount(self):
        # Намагаємося купити більше, ніж є в наявності
        with self.assertRaises(ValueError):
            self.product.buy(25)

    def test_product_equality(self):
        # Перевірка рівності продуктів з однаковим ім'ям
        product1 = Product(name="SameProduct", price=10.0, available_amount=5)
        product2 = Product(name="SameProduct", price=20.0, available_amount=10)
        self.assertEqual(
            product1, product2, "Продукти з однаковим ім'ям мають бути рівні"
        )

    def test_product_inequality(self):
        # Перевірка нерівності продуктів з різними іменами
        product1 = Product(name="Product1", price=10.0, available_amount=5)
        product2 = Product(name="Product2", price=10.0, available_amount=5)
        self.assertNotEqual(
            product1, product2, "Продукти з різними іменами не мають бути рівні"
        )

    def test_product_hash(self):
        # Перевірка хеш-функції продукту
        product = Product(name="HashProduct", price=10.0, available_amount=5)
        self.assertEqual(
            hash(product),
            hash("HashProduct"),
            "Хеш продукту має дорівнювати хешу його імені",
        )

    def test_product_str(self):
        # Перевірка строкового представлення продукту
        product = Product(name="StrProduct", price=10.0, available_amount=5)
        self.assertEqual(
            str(product),
            "StrProduct",
            "Строкове представлення продукту має дорівнювати його імені",
        )


class TestShoppingCart(unittest.TestCase):
    def setUp(self):
        self.product = Product(name="CartProduct", price=20.0, available_amount=10)
        self.cart = ShoppingCart()

    def tearDown(self):
        self.cart.remove_product(self.product)

    def test_add_product_valid_amount(self):
        # Додавання продукту з кількістю 5, яка доступна
        self.product.is_available = MagicMock(return_value=True)
        self.cart.add_product(self.product, 5)
        self.product.is_available.assert_called_with(5)
        self.assertTrue(
            self.cart.contains_product(self.product), "Продукт має бути у кошику"
        )

    def test_add_product_invalid_amount_non_positive(self):
        # Спроба додати продукт з кількістю 0 або негативною
        with self.assertRaises(ValueError):
            self.cart.add_product(self.product, 0)
        with self.assertRaises(ValueError):
            self.cart.add_product(self.product, -3)

    def test_add_product_insufficient_amount(self):
        # Додавання з кількістю, що перевищує наявну
        self.product.is_available = MagicMock(return_value=False)
        with self.assertRaises(ValueError):
            self.cart.add_product(self.product, 15)
        self.product.is_available.assert_called_with(15)
        self.assertFalse(
            self.cart.contains_product(self.product),
            "Продукт не має бути доданий у кошик",
        )

    def test_calculate_total(self):
        # Додаємо два продукти і перевіряємо загальну суму
        self.cart.add_product(self.product, 2)
        another_product = Product(name="AnotherProduct", price=15.0, available_amount=5)
        self.cart.add_product(another_product, 3)
        total = self.cart.calculate_total()
        self.assertAlmostEqual(total, 85.0, msg="Загальна сума має дорівнювати 85.0")

    def test_remove_product(self):
        # Додавання та подальше видалення продукту з кошика
        self.cart.add_product(self.product, 3)
        self.cart.remove_product(self.product)
        self.assertFalse(
            self.cart.contains_product(self.product),
            "Продукт має бути видалений з кошика",
        )

    def test_submit_cart_order(self):
        # Перевірка, що submit_cart_order повертає список імен продуктів
        self.cart.add_product(self.product, 3)
        product_ids = self.cart.submit_cart_order()
        self.assertEqual(len(product_ids), 1, "Має бути повернений один продукт")
        self.assertEqual(
            product_ids[0], "CartProduct", "Ім'я продукту має бути CartProduct"
        )
        self.assertEqual(
            len(self.cart.products),
            0,
            "Кошик має бути порожнім після submit_cart_order",
        )


class TestOrder(unittest.TestCase):
    def setUp(self):
        # Створюємо продукт і кошик, додаємо продукт у кошик
        self.product = Product(name="OrderProduct", price=30.0, available_amount=10)
        self.cart = ShoppingCart()
        self.cart.add_product(self.product, 4)
        self.shipping_service = MagicMock(spec=ShippingService)
        self.shipping_service.create_shipping.return_value = "shipping-123"
        self.order = Order(cart=self.cart, shipping_service=self.shipping_service)

    def test_place_order_reduces_product_amount(self):
        # Перед виконанням замовлення маємо available_amount 10, після замовлення має бути 6
        original_submit = self.cart.submit_cart_order
        self.cart.submit_cart_order = MagicMock(return_value=["OrderProduct"])
        self.order.place_order("Standard")
        self.cart.submit_cart_order.assert_called_once()
        self.shipping_service.create_shipping.assert_called_once()

    def test_place_order_with_due_date(self):
        # Перевірка розміщення замовлення з вказаною датою доставки
        from datetime import datetime, timezone

        due_date = datetime.now(timezone.utc)
        self.order.place_order("Express", due_date)
        self.shipping_service.create_shipping.assert_called_with(
            "Express", ["OrderProduct"], self.order.order_id, due_date
        )


class TestShipment(unittest.TestCase):
    def setUp(self):
        self.shipping_service = MagicMock(spec=ShippingService)
        self.shipping_service.check_status.return_value = "in_progress"
        self.shipment = Shipment(
            shipping_id="shipping-123", shipping_service=self.shipping_service
        )

    def test_check_shipping_status(self):
        # Перевірка статусу доставки
        status = self.shipment.check_shipping_status()
        self.assertEqual(status, "in_progress", "Статус доставки має бути in_progress")
        self.shipping_service.check_status.assert_called_with("shipping-123")


if __name__ == "__main__":
    unittest.main()
