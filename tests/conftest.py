import pytest
import boto3
from services.config import *
from services.db import get_dynamodb_resource


@pytest.fixture(scope="session", autouse=True)
def setup_localstack_resources():
    # Adding dummy credentials for LocalStack
    dynamo_client = boto3.client(
        "dynamodb",
        endpoint_url=AWS_ENDPOINT_URL,
        region_name=AWS_REGION,
        aws_access_key_id="test",
        aws_secret_access_key="test",
    )

    existing_tables = dynamo_client.list_tables()["TableNames"]
    if SHIPPING_TABLE_NAME not in existing_tables:
        dynamo_client.create_table(
            TableName=SHIPPING_TABLE_NAME,
            KeySchema=[{"AttributeName": "shipping_id", "KeyType": "HASH"}],
            AttributeDefinitions=[
                {"AttributeName": "shipping_id", "AttributeType": "S"}
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        dynamo_client.get_waiter("table_exists").wait(TableName=SHIPPING_TABLE_NAME)

    # Adding dummy credentials for SQS client as well
    sqs_client = boto3.client(
        "sqs",
        endpoint_url=AWS_ENDPOINT_URL,
        region_name=AWS_REGION,
        aws_access_key_id="test",
        aws_secret_access_key="test",
    )

    response = sqs_client.create_queue(QueueName=SHIPPING_QUEUE)
    queue_url = response["QueueUrl"]

    yield  # Всі тести йдуть тут

    dynamo_client.delete_table(TableName=SHIPPING_TABLE_NAME)
    sqs_client.delete_queue(QueueUrl=queue_url)


@pytest.fixture
def dynamo_resource():
    # Also need to update the db.py or modify this fixture
    resource = boto3.resource(
        "dynamodb",
        endpoint_url=AWS_ENDPOINT_URL,
        region_name=AWS_REGION,
        aws_access_key_id="test",
        aws_secret_access_key="test",
    )
    return resource
