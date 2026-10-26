"""Read the order events as a member of a consumer group.

The consumer confirms its position in Kafka after every --commit-every events.
Stopping it with Ctrl+C does not confirm the events read since the last
confirmation.
"""
import argparse
import json
import time

from confluent_kafka import Consumer

from common import BOOTSTRAP_SERVERS, TOPIC


def partition_numbers(partitions):
    return sorted(partition.partition for partition in partitions)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', required=True)
    parser.add_argument('--name', default='consumer')
    parser.add_argument('--delay', type=float, default=0.0)
    parser.add_argument('--commit-every', type=int, default=1)
    args = parser.parse_args()

    consumer = Consumer({
        'bootstrap.servers': BOOTSTRAP_SERVERS,
        'group.id': args.group,
        'client.id': args.name,
        'enable.auto.commit': False,
        'auto.offset.reset': 'earliest',
        'session.timeout.ms': 10000
    })

    def on_assign(_, partitions):
        print(
            f'[{args.name}] assigned partitions '
            f'{partition_numbers(partitions)}',
            flush=True)

    def on_revoke(_, partitions):
        print(
            f'[{args.name}] revoked partitions '
            f'{partition_numbers(partitions)}',
            flush=True)

    consumer.subscribe([TOPIC], on_assign=on_assign, on_revoke=on_revoke)

    processed = 0
    try:
        while True:
            message = consumer.poll(1.0)
            if message is None:
                continue
            if message.error():
                print(f'[{args.name}] {message.error()}', flush=True)
                continue
            event = json.loads(message.value())
            print(
                f'[{args.name}] partition {message.partition()}, '
                f'offset {message.offset()}: order {event["order_id"]} '
                f'{event["event_type"]}',
                flush=True)
            time.sleep(args.delay)
            processed += 1
            if processed % args.commit_every == 0:
                consumer.commit(asynchronous=False)
    except KeyboardInterrupt:
        print(f'[{args.name}] stopped', flush=True)
    finally:
        consumer.close()


if __name__ == '__main__':
    main()
