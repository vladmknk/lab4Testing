import uuid

import boto3
from app.eshop import Product, Shipment, ShoppingCart, Order
import random
from services import ShippingService
from services.repository import ShippingRepository
from services.publisher import ShippingPublisher
from datetime import datetime, time, timedelta, timezone
from services.config import AWS_ENDPOINT_URL, AWS_REGION, SHIPPING_QUEUE
import pytest


@pytest.mark.parametrize(
    "order_id, shipping_id",
    [
        ("order_1", "shipping_1"),
        ("order_i2hur2937r9", "shipping_1!!!!"),
        (8662354, 123456),
        (str(uuid.uuid4()), str(uuid.uuid4())),
    ],
)
def test_place_order_with_mocked_repo(mocker, order_id, shipping_id):
    mock_repo = mocker.Mock()
    mock_publisher = mocker.Mock()
    shipping_service = ShippingService(mock_repo, mock_publisher)

    mock_repo.create_shipping.return_value = shipping_id

    cart = ShoppingCart()
    cart.add_product(
        Product(available_amount=10, name="Product", price=random.random() * 10000),
        amount=9,
    )

    order = Order(cart, shipping_service, order_id)
    due_date = datetime.now(timezone.utc) + timedelta(seconds=3)
    actual_shipping_id = order.place_order(
        ShippingService.list_available_shipping_type()[0], due_date=due_date
    )

    assert (
        actual_shipping_id == shipping_id
    ), "Actual shipping id must be equal to mock return value"

    mock_repo.create_shipping.assert_called_with(
        ShippingService.list_available_shipping_type()[0],
        ["Product"],
        order_id,
        shipping_service.SHIPPING_CREATED,
        due_date,
    )
    mock_publisher.send_new_shipping.assert_called_with(shipping_id)


def test_place_order_with_unavailable_shipping_type_fails(dynamo_resource):
    shipping_service = ShippingService(ShippingRepository(), ShippingPublisher())
    cart = ShoppingCart()
    cart.add_product(
        Product(available_amount=10, name="Product", price=random.random() * 10000),
        amount=9,
    )
    order = Order(cart, shipping_service)
    shipping_id = None

    with pytest.raises(ValueError) as excinfo:
        shipping_id = order.place_order(
            "Новий тип доставки",
            due_date=datetime.now(timezone.utc) + timedelta(seconds=3),
        )
    assert shipping_id is None, "Shipping id must not be assigned"
    assert "Shipping type is not available" in str(excinfo.value)


def test_when_place_order_then_shipping_in_queue(dynamo_resource):
    shipping_service = ShippingService(ShippingRepository(), ShippingPublisher())
    cart = ShoppingCart()

    cart.add_product(
        Product(available_amount=10, name="Product", price=random.random() * 10000),
        amount=9,
    )

    order = Order(cart, shipping_service)
    shipping_id = order.place_order(
        ShippingService.list_available_shipping_type()[0],
        due_date=datetime.now(timezone.utc) + timedelta(minutes=1),
    )

    sqs_client = boto3.client(
        "sqs",
        endpoint_url=AWS_ENDPOINT_URL,
        region_name=AWS_REGION,
        aws_access_key_id="test",
        aws_secret_access_key="test",
    )
    queue_url = sqs_client.get_queue_url(QueueName=SHIPPING_QUEUE)["QueueUrl"]
    response = sqs_client.receive_message(
        QueueUrl=queue_url, MaxNumberOfMessages=1, WaitTimeSeconds=10
    )

    messages = response.get("Messages", [])
    assert len(messages) == 1, "Expected 1 SQS message"

    body = messages[0]["Body"]
    assert shipping_id == body


#
# Additional tests
#


@pytest.mark.parametrize(
    "order_id, shipping_type",
    [("order_1", "Нова Пошта"), ("order_2", "Укр Пошта"), (123456, "Meest Express")],
)
def test_shipping_repository_create_and_get_integration(
    dynamo_resource, order_id, shipping_type
):
    repo = ShippingRepository()

    product_ids = ["product1", "product2"]
    status = "created"
    due_date = datetime.now(timezone.utc) + timedelta(days=1)

    shipping_id = repo.create_shipping(
        shipping_type, product_ids, order_id, status, due_date
    )

    shipping = repo.get_shipping(shipping_id)

    assert shipping is not None
    assert shipping["shipping_id"] == shipping_id
    assert shipping["order_id"] == order_id
    assert shipping["shipping_type"] == shipping_type
    assert shipping["product_ids"] == ",".join(product_ids)
    assert shipping["shipping_status"] == status
    assert "created_date" in shipping
    assert "due_date" in shipping


def test_shipping_repository_update_status_integration(dynamo_resource):
    repo = ShippingRepository()

    shipping_type = "Укр Пошта"
    product_ids = ["product3"]
    order_id = str(uuid.uuid4())
    status = "created"
    due_date = datetime.now(timezone.utc) + timedelta(days=1)

    shipping_id = repo.create_shipping(
        shipping_type, product_ids, order_id, status, due_date
    )

    new_status = "in progress"
    repo.update_shipping_status(shipping_id, new_status)

    shipping = repo.get_shipping(shipping_id)

    assert shipping["shipping_status"] == new_status


def test_shipping_publisher_send_and_poll_integration():
    publisher = ShippingPublisher()

    shipping_id = str(uuid.uuid4())

    message_id = publisher.send_new_shipping(shipping_id)

    assert message_id is not None

    max_retries = 3
    messages = []

    for i in range(max_retries):
        messages = publisher.poll_shipping(batch_size=1)
        if messages and shipping_id in messages:
            break
        time.sleep(1)

    assert shipping_id in messages


def test_shipping_service_creation_bottom_up():
    repo = ShippingRepository()
    publisher = ShippingPublisher()

    service = ShippingService(repo, publisher)

    assert service.repository == repo
    assert service.publisher == publisher

    shipping_types = service.list_available_shipping_type()
    assert len(shipping_types) > 0
    assert "Нова Пошта" in shipping_types


def test_create_shipping_with_real_service():
    service = ShippingService(ShippingRepository(), ShippingPublisher())
    shipping_type = service.list_available_shipping_type()[0]
    product_ids = ["prod1", "prod2", "prod3"]
    order_id = str(uuid.uuid4())
    due_date = datetime.now(timezone.utc) + timedelta(hours=24)

    shipping_id = service.create_shipping(
        shipping_type, product_ids, order_id, due_date
    )

    assert shipping_id is not None

    shipping = service.repository.get_shipping(shipping_id)
    assert shipping is not None
    assert shipping["shipping_status"] == service.SHIPPING_IN_PROGRESS

    sqs_client = boto3.client(
        "sqs",
        endpoint_url=AWS_ENDPOINT_URL,
        region_name=AWS_REGION,
        aws_access_key_id="test",
        aws_secret_access_key="test",
    )
    queue_url = sqs_client.get_queue_url(QueueName=SHIPPING_QUEUE)["QueueUrl"]

    message_found = False
    for _ in range(3):
        response = sqs_client.receive_message(
            QueueUrl=queue_url, MaxNumberOfMessages=10, WaitTimeSeconds=1
        )

        if "Messages" in response:
            for msg in response["Messages"]:
                if msg["Body"] == shipping_id:
                    message_found = True
                    break

        if message_found:
            break
        time.sleep(1)

    assert message_found, "Shipping ID was not found in the queue"


def test_process_shipping_with_future_due_date():
    service = ShippingService(ShippingRepository(), ShippingPublisher())
    shipping_type = service.list_available_shipping_type()[0]
    product_ids = ["test_product"]
    order_id = str(uuid.uuid4())
    due_date = datetime.now(timezone.utc) + timedelta(days=1)

    shipping_id = service.create_shipping(
        shipping_type, product_ids, order_id, due_date
    )

    result = service.process_shipping(shipping_id)

    status = service.check_status(shipping_id)
    assert status == service.SHIPPING_COMPLETED
    assert result["HTTPStatusCode"] == 200


def test_process_shipping_with_past_due_date():
    repo = ShippingRepository()
    publisher = ShippingPublisher()
    service = ShippingService(repo, publisher)

    shipping_type = service.list_available_shipping_type()[0]
    product_ids = ["past_due_product"]
    order_id = str(uuid.uuid4())
    due_date = datetime.now(timezone.utc) - timedelta(days=1)

    shipping_id = repo.create_shipping(
        shipping_type, product_ids, order_id, service.SHIPPING_CREATED, due_date
    )

    result = service.process_shipping(shipping_id)

    status = service.check_status(shipping_id)
    assert status == service.SHIPPING_FAILED
    assert result["HTTPStatusCode"] == 200


def test_order_placement_end_to_end():
    shipping_service = ShippingService(ShippingRepository(), ShippingPublisher())

    product1 = Product(available_amount=10, name="Product1", price=100.0)
    product2 = Product(available_amount=5, name="Product2", price=50.0)

    cart = ShoppingCart()
    cart.add_product(product1, amount=2)
    cart.add_product(product2, amount=1)

    order = Order(cart, shipping_service)
    due_date = datetime.now(timezone.utc) + timedelta(hours=48)

    shipping_id = order.place_order(
        shipping_service.list_available_shipping_type()[0], due_date
    )

    shipment = Shipment(shipping_id, shipping_service)
    status = shipment.check_shipping_status()

    assert status == shipping_service.SHIPPING_IN_PROGRESS

    assert product1.available_amount == 8
    assert product2.available_amount == 4


def test_process_shipping_batch():
    service = ShippingService(ShippingRepository(), ShippingPublisher())
    shipping_type = service.list_available_shipping_type()[0]

    shipping_ids = []
    for i in range(3):
        product_ids = [f"batch_product_{i}"]
        order_id = f"batch_order_{i}"
        due_date = datetime.now(timezone.utc) + timedelta(hours=i + 1)
        shipping_id = service.create_shipping(
            shipping_type, product_ids, order_id, due_date
        )
        shipping_ids.append(shipping_id)

    results = service.process_shipping_batch()

    assert len(results) > 0

    for shipping_id in shipping_ids:
        status = service.check_status(shipping_id)
        assert status == service.SHIPPING_COMPLETED


def test_create_shipping_with_past_due_date_fails():
    service = ShippingService(ShippingRepository(), ShippingPublisher())
    shipping_type = service.list_available_shipping_type()[0]
    product_ids = ["prod_past_due"]
    order_id = str(uuid.uuid4())
    due_date = datetime.now(timezone.utc) - timedelta(minutes=10)

    with pytest.raises(ValueError) as excinfo:
        service.create_shipping(shipping_type, product_ids, order_id, due_date)

    assert "Shipping due datetime must be greater than datetime now" in str(
        excinfo.value
    )
