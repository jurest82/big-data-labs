"""Create or delete the topic of the Kafka lab."""
import argparse

from confluent_kafka.admin import AdminClient, NewTopic

from common import BOOTSTRAP_SERVERS, PARTITIONS, TOPIC


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['create', 'delete'])
    args = parser.parse_args()

    admin = AdminClient({
        'bootstrap.servers': BOOTSTRAP_SERVERS
    })
    if args.action == 'create':
        futures = admin.create_topics(
            [NewTopic(TOPIC, num_partitions=PARTITIONS, replication_factor=1)])
    else:
        futures = admin.delete_topics([TOPIC])

    for future in futures.values():
        future.result()
    print(f'Topic {TOPIC}: {args.action} done')


if __name__ == '__main__':
    main()
