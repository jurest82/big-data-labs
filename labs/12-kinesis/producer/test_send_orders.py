import json
import random
from datetime import datetime, timezone
from types import SimpleNamespace

import send_orders as so

NOW = datetime(2026, 10, 26, 12, 0, 0, tzinfo=timezone.utc)


def make_plan(seed=1, seconds=30, rate=2.0):
    return so.plan(random.Random(seed), seconds, rate, 1001)


def test_the_plan_is_the_same_for_the_same_seed():
    assert make_plan() == make_plan()
    assert make_plan(seed=1) != make_plan(seed=2)


def test_every_order_goes_through_its_three_events_in_order():
    seconds = make_plan(seconds=60)
    when = {}
    for second, pairs in enumerate(seconds):
        for event_type, order in pairs:
            when[(order['order_id'], event_type)] = second
    order_ids = {order_id
                 for order_id, _ in when}
    assert len(order_ids) >= 100
    for order_id in order_ids:
        created = when[(order_id, 'order_created')]
        confirmed = when[(order_id, 'order_confirmed')]
        closed = [
            when[(order_id, kind)]
            for kind in ('order_delivered', 'order_cancelled')
            if (order_id, kind) in when
        ]
        assert len(closed) == 1
        assert created < confirmed < closed[0]


def test_the_rate_is_the_average_of_new_orders_per_second():
    seconds = make_plan(seconds=200, rate=2.5)
    created = sum(1 for pairs in seconds for kind, _ in pairs
                  if kind == 'order_created')
    assert 2.3 <= created / 200 <= 2.7


def test_a_record_carries_the_event_and_the_order_id_as_its_key():
    rng = random.Random(1)
    event_type, order = make_plan()[0][0]
    event = so.make_event(rng, event_type, order, NOW)
    record = so.to_record(event)
    assert json.loads(record['Data'].decode('utf-8')) == event
    assert record['PartitionKey'] == str(order['order_id'])
    assert event['occurred_at'] == '2026-10-26T12:00:00.000+00:00'


def fake_kinesis(reject_first=0):
    calls = []

    def put_records(**request):
        calls.append(len(request['Records']))
        rejected = reject_first if len(calls) == 1 else 0
        results = [{
            'ErrorCode': 'ProvisionedThroughputExceededException'
        } if index < rejected else {
            'ShardId': 'shardId-000000000000',
            'SequenceNumber': str(index)
        } for index in range(len(request['Records']))]
        return {
            'FailedRecordCount': rejected,
            'Records': results
        }

    return SimpleNamespace(put_records=put_records, calls=calls)


def test_the_records_that_kinesis_rejects_are_sent_again(monkeypatch):
    monkeypatch.setattr(so.time, 'sleep', lambda seconds: None)
    client = fake_kinesis(reject_first=3)
    records = [{
        'Data': b'{}',
        'PartitionKey': str(n)
    } for n in range(10)]
    failed, accepted = so.send_batch(client, 'stream', records)
    assert failed == 0
    assert len(accepted) == 10
    assert client.calls == [10, 3]


def test_the_records_that_keep_failing_are_counted(monkeypatch):
    monkeypatch.setattr(so.time, 'sleep', lambda seconds: None)

    def always_fails(**request):
        return {
            'FailedRecordCount':
                len(request['Records']),
            'Records': [{
                'ErrorCode': 'InternalFailure'
            }] * len(request['Records'])
        }

    client = SimpleNamespace(put_records=always_fails)
    records = [{
        'Data': b'{}',
        'PartitionKey': '1'
    }]
    failed, accepted = so.send_batch(client, 'stream', records, attempts=2)
    assert failed == 1
    assert not accepted
