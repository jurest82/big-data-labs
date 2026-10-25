"""Settings shared by the scripts of the Kafka lab."""
import os

BOOTSTRAP_SERVERS = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
TOPIC = 'orders'
PARTITIONS = 3
