import base64
import json
from decimal import Decimal
from types import SimpleNamespace

import consumer

SEQUENCE = '49590338271490256608559692538361571095921575989136588898'


def kinesis_record(event, shard='shardId-000000000001'):
    data = json.dumps(event).encode('utf-8')
    return {
        'kinesis': {
            'kinesisSchemaVersion': '1.0',
            'partitionKey': str(event['order_id']),
            'sequenceNumber': SEQUENCE,
            'data': base64.b64encode(data).decode('ascii'),
        },
        'eventSource': 'aws:kinesis',
        'eventID': f'{shard}:{SEQUENCE}',
    }


EVENT = {
    'event_id': 'b1f4e5de-3c0e-4a52-8d3b-2f0f2c3f2f11',
    'event_type': 'order_created',
    'order_id': 1001,
    'restaurant': 'Sushi House',
    'amount': 23.5,
    'occurred_at': '2026-10-26T12:00:00.000+00:00',
}


def fake_table():
    items = []
    return SimpleNamespace(
        items=items, put_item=lambda **kwargs: items.append(kwargs['Item']))


def test_the_item_has_the_event_and_where_it_was_read():
    item = consumer.to_item(kinesis_record(EVENT))
    assert item['order_id'] == 1001
    assert item['event_type'] == 'order_created'
    assert item['amount'] == Decimal('23.5')
    assert item['shard_id'] == 'shardId-000000000001'
    assert item['sequence_number'] == SEQUENCE


def test_the_handler_writes_one_item_per_record(monkeypatch):
    table = fake_table()
    monkeypatch.setattr(consumer, 'get_table', lambda: table)
    other = {
        **EVENT, 'order_id': 1002,
        'event_type': 'order_confirmed'
    }
    result = consumer.handler(
        {
            'Records': [kinesis_record(EVENT),
                        kinesis_record(other)]
        }, None)
    assert result == {
        'written': 2
    }
    assert [item['order_id'] for item in table.items] == [1001, 1002]
