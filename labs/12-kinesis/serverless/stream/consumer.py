"""Lambda function that writes each order event of a Kinesis stream to DynamoDB.

The table has the order id as its partition key and the event type as its sort
key, so an event that arrives twice replaces the item it had already written.
"""
import base64
import json
import os
from decimal import Decimal

import boto3


def get_table():
    return boto3.resource('dynamodb').Table(os.environ['TABLE_NAME'])


def to_item(record):
    """Return the DynamoDB item of a Kinesis record of the Lambda event."""
    data = base64.b64decode(record['kinesis']['data'])
    event = json.loads(data, parse_float=Decimal)
    shard_id, sequence_number = record['eventID'].split(':')
    return {
        **event, 'shard_id': shard_id,
        'sequence_number': sequence_number
    }


def handler(event, context):
    del context
    table = get_table()
    for record in event['Records']:
        table.put_item(Item=to_item(record))
    result = {
        'written': len(event['Records'])
    }
    print(json.dumps(result))
    return result
