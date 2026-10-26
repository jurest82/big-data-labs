"""Send order events, some of them repeated and some of them late, to a stream.

It sends the same kind of events as lab 12: new orders arrive at --rate per
second, and each one sends order_created, order_confirmed and then
order_delivered or order_cancelled. Some events are sent twice with the same
event_id, and some new orders arrive 2 minutes after they happened. At the end
it prints how many orders each minute should have in the windows of Flink.
With --dry-run it prints the events and does not call AWS.
"""
import argparse
import json
import random
import time
import uuid
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

import boto3

MAX_BATCH = 500
RESTAURANTS = [
    'Burger Corner', 'Sushi House', 'Pizza Place', 'Taco Stand', 'Salad Bar'
]
CANCELLED_RATE = 0.08
REPEATED_RATE = 0.05
LATE_RATE = 0.05
LATE_BY = timedelta(minutes=2)
LATE_ORDER_OFFSET = 100000


def plan(rng, seconds, rate, first_order_id):
    """Return the events of each second as (event_type, order) pairs."""
    schedule = defaultdict(list)
    next_order_id = first_order_id
    for second in range(seconds):
        new_orders = int(rate) + (rng.random() < rate - int(rate))
        for _ in range(new_orders):
            order = new_order(rng, next_order_id)
            next_order_id += 1
            confirmed = second + rng.randint(1, 4)
            closed = confirmed + rng.randint(2, 8)
            closing = ('order_cancelled'
                       if rng.random() < CANCELLED_RATE else 'order_delivered')
            schedule[second].append(('order_created', order))
            schedule[confirmed].append(('order_confirmed', order))
            schedule[closed].append((closing, order))
    return [schedule[second] for second in range(max(schedule) + 1)]


def new_order(rng, order_id):
    return {
        'order_id': order_id,
        'restaurant': rng.choice(RESTAURANTS),
        'amount': round(rng.uniform(8, 40), 2)
    }


def make_event(rng, event_type, order, moment):
    return {
        'event_id': str(uuid.UUID(int=rng.getrandbits(128), version=4)),
        'event_type': event_type,
        **order, 'occurred_at': moment.isoformat(timespec='milliseconds')
    }


def second_events(rng, pairs, now, late_order_id):
    """Return the events of one second as (kind, event) pairs.

    The kind is normal, repeated (a copy of the event before it) or late (a
    new order that happened LATE_BY before now).
    """
    events = []
    for event_type, order in pairs:
        event = make_event(rng, event_type, order, now)
        events.append(('normal', event))
        if rng.random() < REPEATED_RATE:
            events.append(('repeated', event))
        if event_type == 'order_created' and rng.random() < LATE_RATE:
            order = new_order(rng, late_order_id)
            late_order_id += 1
            events.append(
                ('late', make_event(rng, 'order_created', order,
                                    now - LATE_BY)))
    return events, late_order_id


def to_record(event):
    return {
        'Data': json.dumps(event, ensure_ascii=False).encode('utf-8'),
        'PartitionKey': str(event['order_id'])
    }


def send_batch(client, stream, records, attempts=5):
    """Send records, retrying the ones Kinesis rejects. Return the failures."""
    pending = list(records)
    for attempt in range(attempts):
        response = client.put_records(StreamName=stream, Records=pending)
        pending = [
            record for record, result in zip(pending, response['Records'])
            if 'ErrorCode' in result
        ]
        if not pending:
            break
        time.sleep(0.2 * (attempt + 1))
    return len(pending)


def send_events(client, stream, events):
    records = [to_record(event) for _, event in events]
    failed = 0
    for start in range(0, len(records), MAX_BATCH):
        failed += send_batch(client, stream, records[start:start + MAX_BATCH])
    return failed


def count_expected(counts, events):
    """Count by minute the orders that the windows of Flink must count."""
    for kind, event in events:
        if kind == 'normal' and event['event_type'] == 'order_created':
            counts[event['occurred_at'][11:16]] += 1


def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__.split('\n', maxsplit=1)[0])
    parser.add_argument('--stream', default='big-data-labs-flink-orders')
    parser.add_argument('--rate', type=float, default=2.0)
    parser.add_argument('--seconds', type=int, default=180)
    parser.add_argument('--first-order-id', type=int, default=2001)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--dry-run', action='store_true')
    return parser.parse_args()


def print_events(rng, seconds, first_order_id):
    now = datetime.now(timezone.utc)
    late_order_id = first_order_id + LATE_ORDER_OFFSET
    for pairs in seconds:
        events, late_order_id = second_events(rng, pairs, now, late_order_id)
        for kind, event in events:
            print(f'{kind:9}{json.dumps(event)}')


def print_summary(sent, kinds, expected, failed):
    print(f'{sent} events sent, {failed} failed: {kinds["repeated"]} repeated '
          f'and {kinds["late"]} late')
    print('Orders that each window of Flink must count (UTC):')
    for minute, orders in sorted(expected.items()):
        print(f'  {minute}  {orders}')


def main():
    args = parse_args()
    rng = random.Random(args.seed)
    seconds = plan(rng, args.seconds, args.rate, args.first_order_id)
    if args.dry_run:
        print_events(rng, seconds[:10], args.first_order_id)
        return
    client = boto3.client('kinesis')
    late_order_id = args.first_order_id + LATE_ORDER_OFFSET
    sent = failed = 0
    kinds = Counter()
    expected = Counter()
    for second, pairs in enumerate(seconds, start=1):
        started = time.monotonic()
        events, late_order_id = second_events(rng, pairs,
                                              datetime.now(timezone.utc),
                                              late_order_id)
        failed += send_events(client, args.stream, events)
        count_expected(expected, events)
        kinds.update(kind for kind, _ in events)
        sent += len(events)
        if second % 10 == 0 or second == len(seconds):
            print(f'{second}s: {sent} events sent, {failed} failed')
        time.sleep(max(0.0, 1.0 - (time.monotonic() - started)))
    print_summary(sent, kinds, expected, failed)


if __name__ == '__main__':
    main()
