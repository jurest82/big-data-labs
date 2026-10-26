"""Settings shared by the scripts of the Kafka and PostgreSQL lab."""
import os

BOOTSTRAP_SERVERS = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
TOPIC = 'orders'
