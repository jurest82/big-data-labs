"""Read the order events from the topic and insert them into PostgreSQL.

The consumer confirms its position in Kafka after every --commit-every
events. With --idempotent, an event whose event_id is already in the table is
ignored, and the table must have event_id as its primary key. With
--stop-when-idle, it confirms its position and stops after that many seconds
without new events.
"""
import argparse
import json
import time

import psycopg
from confluent_kafka import Consumer
from psycopg import sql

from common import BOOTSTRAP_SERVERS, TOPIC


def build_insert(table, idempotent):
    query = sql.SQL(
        'INSERT INTO lab_11.{} (event_id, event_type, order_id, '
        'restaurant, amount, occurred_at, kafka_partition, '
        'kafka_offset) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)').format(
            sql.Identifier(table))
    if idempotent:
        query += sql.SQL(' ON CONFLICT (event_id) DO NOTHING')
    return query


def partition_numbers(partitions):
    return sorted(partition.partition for partition in partitions)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', required=True)
    parser.add_argument('--name', default='sink')
    parser.add_argument('--table', required=True)
    parser.add_argument('--idempotent', action='store_true')
    parser.add_argument('--commit-every', type=int, default=50)
    parser.add_argument('--stop-when-idle', type=float)
    args = parser.parse_args()

    insert = build_insert(args.table, args.idempotent)
    connection = psycopg.connect(autocommit=True)
    consumer = Consumer({
        'bootstrap.servers': BOOTSTRAP_SERVERS,
        'group.id': args.group,
        'client.id': args.name,
        'enable.auto.commit': False,
        'auto.offset.reset': 'earliest',
        'session.timeout.ms': 10000
    })

    last_event = time.monotonic()

    def on_assign(_, partitions):
        nonlocal last_event
        last_event = time.monotonic()
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
                idle = time.monotonic() - last_event
                if args.stop_when_idle and idle >= args.stop_when_idle:
                    break
                continue
            if message.error():
                print(f'[{args.name}] {message.error()}', flush=True)
                continue
            last_event = time.monotonic()
            event = json.loads(message.value())
            connection.execute(
                insert,
                (event['event_id'], event['event_type'], event['order_id'],
                 event['restaurant'], event['amount'], event['occurred_at'],
                 message.partition(), message.offset()))
            processed += 1
            if processed % args.commit_every == 0:
                consumer.commit(asynchronous=False)
    except KeyboardInterrupt:
        pass
    finally:
        if args.stop_when_idle and processed:
            consumer.commit(asynchronous=False)
        consumer.close()
        connection.close()
    print(f'[{args.name}] stopped after {processed} events', flush=True)


if __name__ == '__main__':
    main()
