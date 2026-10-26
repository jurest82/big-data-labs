import random
from collections import Counter
from datetime import datetime, timezone
from types import SimpleNamespace

import send_events as se

NOW = datetime(2026, 10, 30, 12, 0, 59, tzinfo=timezone.utc)


def make_events(seed=1, seconds=120, rate=2.0):
    rng = random.Random(seed)
    events = []
    late_order_id = 100000
    for pairs in se.plan(rng, seconds, rate, 1):
        second, late_order_id = se.second_events(rng, pairs, NOW, late_order_id)
        events += second
    return events


def test_the_events_are_the_same_for_the_same_seed():
    assert make_events() == make_events()
    assert make_events(seed=1) != make_events(seed=2)


def test_a_repeated_event_is_a_copy_of_the_event_before_it():
    events = make_events()
    repeated = [(i, event)
                for i, (kind, event) in enumerate(events)
                if kind == 'repeated']
    assert len(repeated) >= 5
    for i, event in repeated:
        assert events[i - 1][1] == event
        assert events[i - 1][0] in ('normal', 'late')


def test_only_the_repeated_events_share_an_event_id():
    events = make_events()
    ids = Counter(event['event_id'] for _, event in events)
    repeated = sum(1 for kind, _ in events if kind == 'repeated')
    assert sum(count - 1 for count in ids.values()) == repeated


def test_a_late_event_is_a_new_order_created_two_minutes_before():
    events = make_events()
    normal_ids = {
        event['order_id']
        for kind, event in events
        if kind == 'normal'
    }
    late = [event for kind, event in events if kind == 'late']
    assert len(late) >= 5
    for event in late:
        assert event['event_type'] == 'order_created'
        assert event['order_id'] not in normal_ids
        assert event['occurred_at'] == '2026-10-30T11:58:59.000+00:00'


def test_the_expected_orders_leave_out_repeated_and_late_events():
    events = make_events()
    counts = Counter()
    se.count_expected(counts, events)
    created = sum(
        1 for kind, event in events
        if kind == 'normal' and event['event_type'] == 'order_created')
    assert sum(counts.values()) == created
    assert set(counts) == {'12:00'}


def test_the_record_uses_the_order_id_as_its_partition_key():
    event = make_events()[0][1]
    assert se.to_record(event)['PartitionKey'] == str(event['order_id'])


def test_send_batch_retries_the_records_that_are_rejected():
    calls = []

    def put_records(**kwargs):
        size = len(kwargs['Records'])
        calls.append(size)
        failed = len(calls) == 1
        return {
            'Records': [{
                'ErrorCode': 'x'
            } if failed else {}] * size
        }

    client = SimpleNamespace(put_records=put_records)
    assert se.send_batch(client, 'orders', [{}, {}]) == 0
    assert calls == [2, 2]
