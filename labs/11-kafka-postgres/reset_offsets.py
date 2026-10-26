"""Move the confirmed position of a group to the first event of each partition.

The group must have no active members.
"""
import argparse

from confluent_kafka import (Consumer, ConsumerGroupTopicPartitions,
                             TopicPartition)
from confluent_kafka.admin import AdminClient

from common import BOOTSTRAP_SERVERS, TOPIC


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', required=True)
    args = parser.parse_args()

    admin = AdminClient({
        'bootstrap.servers': BOOTSTRAP_SERVERS
    })
    partitions = sorted(
        admin.list_topics(TOPIC, timeout=10).topics[TOPIC].partitions)

    consumer = Consumer({
        'bootstrap.servers': BOOTSTRAP_SERVERS,
        'group.id': 'reset-offsets'
    })
    firsts = [
        TopicPartition(
            TOPIC, partition,
            consumer.get_watermark_offsets(TopicPartition(TOPIC, partition),
                                           timeout=10)[0])
        for partition in partitions
    ]
    consumer.close()

    request = ConsumerGroupTopicPartitions(args.group, firsts)
    result = admin.alter_consumer_group_offsets([request])[args.group].result()
    for topic_partition in result.topic_partitions:
        print(f'group {args.group}: partition {topic_partition.partition} '
              f'now at offset {topic_partition.offset}')


if __name__ == '__main__':
    main()
