"""Publish random order events to the topic until it is stopped.

New orders arrive at random moments. Each order publishes order_created and,
after a random delay, order_confirmed. Then it publishes order_delivered, or
order_cancelled in a few of them. Every event has a unique event_id, and the
key of each event is the order id.
"""
import argparse
import heapq
import json
import random
import time
import uuid
from datetime import datetime, timezone

from confluent_kafka import Producer

from common import BOOTSTRAP_SERVERS, TOPIC

RESTAURANTS = [
    'Burger Corner', 'Sushi House', 'Pizza Place', 'Taco Stand', 'Salad Bar'
]
CANCELLED_RATE = 0.08


def report(error, message):
    if error is not None:
        print(f'Delivery failed: {error}', flush=True)
        return
    event = json.loads(message.value())
    print(
        f'order {event["order_id"]} {event["event_type"]} -> '
        f'partition {message.partition()}, offset {message.offset()}',
        flush=True)


def next_stage(event_type, rng):
    if event_type == 'order_created':
        return 'order_confirmed', rng.uniform(1, 4)
    if rng.random() < CANCELLED_RATE:
        return 'order_cancelled', rng.uniform(1, 3)
    return 'order_delivered', rng.uniform(2, 8)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--orders-per-second', type=float, default=2.0)
    parser.add_argument('--first-order-id', type=int, default=5001)
    parser.add_argument('--seed', type=int)
    args = parser.parse_args()

    rng = random.Random(args.seed)
    producer = Producer({
        'bootstrap.servers': BOOTSTRAP_SERVERS,
        'partitioner': 'murmur2_random'
    })

    pending = []
    tie_breaker = 0
    next_order_id = args.first_order_id
    next_arrival = time.monotonic()
    while True:
        now = time.monotonic()
        if now >= next_arrival:
            order = {
                'order_id': next_order_id,
                'restaurant': rng.choice(RESTAURANTS),
                'amount': round(rng.uniform(8, 40), 2)
            }
            next_order_id += 1
            heapq.heappush(pending, (now, tie_breaker, 'order_created', order))
            tie_breaker += 1
            next_arrival = now + rng.expovariate(args.orders_per_second)
        while pending and pending[0][0] <= now:
            _, _, event_type, order = heapq.heappop(pending)
            event = {
                'event_id': str(uuid.uuid4()),
                'event_type': event_type,
                **order, 'occurred_at': datetime.now(timezone.utc).isoformat()
            }
            producer.produce(TOPIC,
                             key=str(order['order_id']),
                             value=json.dumps(event),
                             on_delivery=report)
            if event_type in ('order_created', 'order_confirmed'):
                following, delay = next_stage(event_type, rng)
                heapq.heappush(pending,
                               (now + delay, tie_breaker, following, order))
                tie_breaker += 1
        producer.poll(0)
        time.sleep(0.05)


if __name__ == '__main__':
    main()
