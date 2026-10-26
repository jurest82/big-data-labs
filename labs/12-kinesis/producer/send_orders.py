"""Send the events of the orders of a delivery app to a Kinesis data stream.

New orders arrive at --rate per second. Each order sends order_created and,
a few seconds later, order_confirmed, and then order_delivered or, in a few
orders, order_cancelled. The partition key of every record is the order id.
With --dry-run it prints the events and does not call AWS.
"""
import argparse
import json
import random
import time
import uuid
from collections import Counter, defaultdict
from datetime import datetime, timezone

import boto3

MAX_BATCH = 500
RESTAURANTS = [
    'Burger Corner', 'Sushi House', 'Pizza Place', 'Taco Stand', 'Salad Bar'
]
CANCELLED_RATE = 0.08
SAMPLE = 6


def plan(rng, seconds, rate, first_order_id):
    """Return the events of each second as (event_type, order) pairs."""
    schedule = defaultdict(list)
    next_order_id = first_order_id
    for second in range(seconds):
        new_orders = int(rate) + (rng.random() < rate - int(rate))
        for _ in range(new_orders):
            order = {
                'order_id': next_order_id,
                'restaurant': rng.choice(RESTAURANTS),
                'amount': round(rng.uniform(8, 40), 2)
            }
            next_order_id += 1
            confirmed = second + rng.randint(1, 4)
            closed = confirmed + rng.randint(2, 8)
            closing = ('order_cancelled'
                       if rng.random() < CANCELLED_RATE else 'order_delivered')
            schedule[second].append(('order_created', order))
            schedule[confirmed].append(('order_confirmed', order))
            schedule[closed].append((closing, order))
    return [schedule[second] for second in range(max(schedule) + 1)]


def make_event(rng, event_type, order, now):
    return {
        'event_id': str(uuid.UUID(int=rng.getrandbits(128), version=4)),
        'event_type': event_type,
        **order, 'occurred_at': now.isoformat(timespec='milliseconds')
    }


def to_record(event):
    return {
        'Data': json.dumps(event, ensure_ascii=False).encode('utf-8'),
        'PartitionKey': str(event['order_id'])
    }


def send_batch(client, stream, records, attempts=5):
    """Send records, retrying the ones Kinesis rejects.

    Return the number of records that failed and the results of the ones that
    were accepted, each with its record.
    """
    pending = list(records)
    accepted = []
    for attempt in range(attempts):
        response = client.put_records(StreamName=stream, Records=pending)
        retry = []
        for record, result in zip(pending, response['Records']):
            if 'ErrorCode' in result:
                retry.append(record)
            else:
                accepted.append((record, result))
        pending = retry
        if not pending:
            break
        time.sleep(0.2 * (attempt + 1))
    return len(pending), accepted


def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__.split('\n', maxsplit=1)[0])
    parser.add_argument('--stream', default='big-data-labs-orders')
    parser.add_argument('--rate', type=float, default=2.0)
    parser.add_argument('--seconds', type=int, default=60)
    parser.add_argument('--first-order-id', type=int, default=1001)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--dry-run', action='store_true')
    return parser.parse_args()


def send_second(client, stream, rng, pairs):
    """Send the events of one second. Return the failures and the accepted."""
    now = datetime.now(timezone.utc)
    records = [
        to_record(make_event(rng, event_type, order, now))
        for event_type, order in pairs
    ]
    failed = 0
    accepted = []
    for start in range(0, len(records), MAX_BATCH):
        lost, done = send_batch(client, stream,
                                records[start:start + MAX_BATCH])
        failed += lost
        accepted += done
    return failed, accepted


def print_events(rng, seconds):
    now = datetime.now(timezone.utc)
    for pairs in seconds:
        for event_type, order in pairs:
            print(json.dumps(make_event(rng, event_type, order, now)))


def print_shards(shards):
    for shard, count in sorted(shards.items()):
        print(f'{shard}: {count} events')


def main():
    args = parse_args()
    rng = random.Random(args.seed)
    seconds = plan(rng, args.seconds, args.rate, args.first_order_id)
    if args.dry_run:
        print_events(rng, seconds[:10])
        return
    client = boto3.client('kinesis')
    sent = failed = 0
    shards = Counter()
    for second, pairs in enumerate(seconds, start=1):
        started = time.monotonic()
        lost, accepted = send_second(client, args.stream, rng, pairs)
        failed += lost
        for record, result in accepted:
            if sent < SAMPLE:
                print(f'order {record["PartitionKey"]} -> '
                      f'{result["ShardId"]}, '
                      f'sequence {result["SequenceNumber"]}')
            sent += 1
            shards[result['ShardId']] += 1
        if second % 10 == 0 or second == len(seconds):
            print(f'{second}s: {sent} events sent, {failed} failed')
        time.sleep(max(0.0, 1.0 - (time.monotonic() - started)))
    print_shards(shards)


if __name__ == '__main__':
    main()
