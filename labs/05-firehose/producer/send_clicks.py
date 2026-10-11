"""Send the clicks of the online store to a Firehose stream, in real time.

Every second it sends --rate events with PutRecordBatch, for --seconds seconds.
With --dry-run it prints the events and does not call AWS.
"""
import argparse
import json
import random
import time
import uuid
from datetime import datetime, timezone

import boto3

MAX_BATCH = 500
PRODUCTS = [
    (7, 'T-shirt', 'Clothing', 30000),
    (9, 'Cap', 'Accessories', 35000),
    (12, 'Backpack', 'Accessories', 120000),
    (15, 'Shoes', 'Footwear', 150000),
    (21, 'Jeans', 'Clothing', 90000),
    (22, 'Jacket', 'Clothing', 180000),
    (23, 'Hoodie', 'Clothing', 110000),
    (31, 'Belt', 'Accessories', 45000),
    (32, 'Sunglasses', 'Accessories', 85000),
    (33, 'Wallet', 'Accessories', 70000),
    (34, 'Watch', 'Accessories', 220000),
    (41, 'Sneakers', 'Footwear', 170000),
    (42, 'Sandals', 'Footwear', 60000),
    (43, 'Boots', 'Footwear', 210000),
]
EVENT_TYPES = ['page_view', 'search', 'add_to_cart', 'purchase']
EVENT_WEIGHTS = [70, 15, 10, 5]
DEVICES = ['mobile', 'desktop', 'tablet']
DEVICE_WEIGHTS = [60, 33, 7]
SESSIONS = 2000
CUSTOMERS = 5000
ANONYMOUS_SHARE = 0.3


def make_event(rng, now):
    """Return one click, as a dictionary."""
    product = rng.choice(PRODUCTS)
    event_type = rng.choices(EVENT_TYPES, EVENT_WEIGHTS)[0]
    event = {
        'event_id': str(uuid.UUID(int=rng.getrandbits(128), version=4)),
        'event_time': now.isoformat(timespec='milliseconds'),
        'session_id': f'S{rng.randint(1, SESSIONS):05d}',
        'event_type': event_type,
        'product_id': product[0],
        'product_name': product[1],
        'category': product[2],
        'device': rng.choices(DEVICES, DEVICE_WEIGHTS)[0],
    }
    # A visitor who is not signed in has no customer.
    if rng.random() >= ANONYMOUS_SHARE:
        event['customer_id'] = 100 + rng.randint(1, CUSTOMERS)
    if event_type == 'purchase':
        event['amount'] = product[3] * rng.randint(1, 3)
    return event


def to_record(event):
    return {
        'Data': json.dumps(event, ensure_ascii=False).encode('utf-8')
    }


def send_batch(client, stream, records, attempts=5):
    """Send records, retrying the ones Firehose rejects. Return the failures."""
    pending = list(records)
    for attempt in range(attempts):
        response = client.put_record_batch(DeliveryStreamName=stream,
                                           Records=pending)
        if not response['FailedPutCount']:
            return 0
        pending = [
            record
            for record, result in zip(pending, response['RequestResponses'])
            if 'ErrorCode' in result
        ]
        time.sleep(0.2 * (attempt + 1))
    return len(pending)


def send_second(client, stream, rng, rate):
    """Send the events of one second. Return how many failed."""
    now = datetime.now(timezone.utc)
    records = [to_record(make_event(rng, now)) for _ in range(rate)]
    failed = 0
    for start in range(0, len(records), MAX_BATCH):
        failed += send_batch(client, stream, records[start:start + MAX_BATCH])
    return failed


def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__.split('\n', maxsplit=1)[0])
    parser.add_argument('--stream', default='big-data-labs-clicks')
    parser.add_argument('--rate', type=int, default=200)
    parser.add_argument('--seconds', type=int, default=300)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--dry-run', action='store_true')
    return parser.parse_args()


def main():
    args = parse_args()
    rng = random.Random(args.seed)
    if args.dry_run:
        now = datetime.now(timezone.utc)
        for _ in range(args.rate):
            print(json.dumps(make_event(rng, now), ensure_ascii=False))
        return
    client = boto3.client('firehose')
    sent = failed = 0
    for second in range(1, args.seconds + 1):
        started = time.monotonic()
        failed += send_second(client, args.stream, rng, args.rate)
        sent += args.rate
        if second % 10 == 0 or second == args.seconds:
            print(f'{second}s: {sent} events sent, {failed} failed')
        time.sleep(max(0.0, 1.0 - (time.monotonic() - started)))


if __name__ == '__main__':
    main()
