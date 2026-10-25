"""Show the partitions of the topic and, for a group, its members and lag.

For each partition it prints the first offset, the next offset (the one the
next event will get), and, when a group is given, the confirmed offset of the
group and its lag (next offset minus confirmed offset).
"""
import argparse

from confluent_kafka import Consumer, TopicPartition
from confluent_kafka.admin import AdminClient

from common import BOOTSTRAP_SERVERS, TOPIC


def show_members(admin, group):
    description = admin.describe_consumer_groups([group])[group].result()
    print(f'group {group}: {description.state.name}, '
          f'{len(description.members)} members')
    for member in sorted(description.members, key=lambda m: m.client_id):
        assigned = sorted(p.partition
                          for p in member.assignment.topic_partitions)
        print(f'  {member.client_id}: partitions {assigned}')
    print()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group')
    args = parser.parse_args()

    admin = AdminClient({
        'bootstrap.servers': BOOTSTRAP_SERVERS
    })
    metadata = admin.list_topics(TOPIC, timeout=10)
    partitions = sorted(metadata.topics[TOPIC].partitions)

    if args.group:
        show_members(admin, args.group)

    consumer = Consumer({
        'bootstrap.servers': BOOTSTRAP_SERVERS,
        'group.id': args.group or 'describe'
    })
    committed = {}
    if args.group:
        topic_partitions = [TopicPartition(TOPIC, p) for p in partitions]
        committed = {
            p.partition: p.offset
            for p in consumer.committed(topic_partitions, timeout=10)
        }

    header = f'{"partition":>9} {"first":>6} {"next":>6}'
    if args.group:
        header += f' {"confirmed":>9} {"lag":>5}'
    print(header)
    for partition in partitions:
        topic_partition = TopicPartition(TOPIC, partition)
        first, following = consumer.get_watermark_offsets(topic_partition,
                                                          timeout=10)
        line = f'{partition:>9} {first:>6} {following:>6}'
        if args.group:
            offset = committed.get(partition, -1)
            if offset < 0:
                line += f' {"-":>9} {following - first:>5}'
            else:
                line += f' {offset:>9} {following - offset:>5}'
        print(line)
    consumer.close()


if __name__ == '__main__':
    main()
