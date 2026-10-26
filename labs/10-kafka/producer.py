"""Publish the events of some orders of a delivery app to the topic.

Every order produces three events, order_created, order_confirmed and
order_delivered. The events are published by stage, so the events of one order
are separated by the events of the other orders. The key of each event is the
order id.
"""
import argparse
import json
import random
import time
from datetime import datetime, timezone

from confluent_kafka import Producer

from common import BOOTSTRAP_SERVERS, TOPIC

RESTAURANTS = [
    'Burger Corner', 'Sushi House', 'Pizza Place', 'Taco Stand', 'Salad Bar'
]
EVENT_TYPES = ['order_created', 'order_confirmed', 'order_delivered']
SEED = 7


def build_orders(count, first_order_id):
    rng = random.Random(SEED)
    return [{
        'order_id': first_order_id + n,
        'restaurant': rng.choice(RESTAURANTS),
        'amount': round(rng.uniform(8, 40), 2)
    } for n in range(count)]


def report(error, message):
    if error is not None:
        print(f'Delivery failed: {error}')
        return
    event = json.loads(message.value())
    print(f'order {event["order_id"]} {event["event_type"]} -> '
          f'partition {message.partition()}, offset {message.offset()}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--orders', type=int, default=6)
    parser.add_argument('--first-order-id', type=int, default=1201)
    parser.add_argument('--delay', type=float, default=0.5)
    args = parser.parse_args()

    producer = Producer({
        'bootstrap.servers': BOOTSTRAP_SERVERS,
        'partitioner': 'murmur2_random'
    })
    orders = build_orders(args.orders, args.first_order_id)

    for event_type in EVENT_TYPES:
        for order in orders:
            event = {
                'event_type': event_type,
                **order, 'occurred_at': datetime.now(timezone.utc).isoformat()
            }
            producer.produce(TOPIC,
                             key=str(order['order_id']),
                             value=json.dumps(event),
                             on_delivery=report)
            producer.flush()
            time.sleep(args.delay)


if __name__ == '__main__':
    main()
