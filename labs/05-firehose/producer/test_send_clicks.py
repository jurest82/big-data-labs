import json
import random
from datetime import datetime, timezone
from types import SimpleNamespace

import send_clicks as sc

NOW = datetime(2026, 10, 10, 12, 0, 0, tzinfo=timezone.utc)


def fake_firehose(reject_first=0):
    """A client that rejects the first attempt of some records."""
    calls = []

    def put_record_batch(**request):
        calls.append(len(request['Records']))
        rejected = reject_first if len(calls) == 1 else 0
        results = [{
            'ErrorCode': 'ServiceUnavailableException'
        } if index < rejected else {
            'RecordId': 'x'
        } for index in range(len(request['Records']))]
        return {
            'FailedPutCount': rejected,
            'RequestResponses': results
        }

    return SimpleNamespace(put_record_batch=put_record_batch, calls=calls)


def test_events_are_valid_json_with_the_expected_fields():
    rng = random.Random(1)
    events = [sc.make_event(rng, NOW) for _ in range(2000)]
    for event in events:
        record = sc.to_record(event)['Data']
        assert json.loads(record.decode('utf-8')) == event
        assert event['event_type'] in sc.EVENT_TYPES
        assert event['event_time'] == '2026-10-10T12:00:00.000+00:00'
    assert {e['event_type']
            for e in events} == set(sc.EVENT_TYPES)


def test_only_purchases_have_an_amount_and_some_events_have_no_customer():
    rng = random.Random(2)
    events = [sc.make_event(rng, NOW) for _ in range(3000)]
    assert all(
        ('amount' in e) == (e['event_type'] == 'purchase') for e in events)
    assert any('customer_id' not in e for e in events)
    assert any('customer_id' in e for e in events)


def test_the_same_seed_gives_the_same_events():
    first = [sc.make_event(random.Random(3), NOW) for _ in range(5)]
    second = [sc.make_event(random.Random(3), NOW) for _ in range(5)]
    assert first == second


def test_a_second_is_sent_in_batches_of_at_most_500():
    client = fake_firehose()
    failed = sc.send_second(client, 'stream', random.Random(4), 1200)
    assert failed == 0
    assert client.calls == [500, 500, 200]


def test_rejected_records_are_sent_again():
    client = fake_firehose(reject_first=3)
    records = [sc.to_record(sc.make_event(random.Random(5), NOW))] * 10
    assert sc.send_batch(client, 'stream', records) == 0
    assert client.calls == [10, 3]
