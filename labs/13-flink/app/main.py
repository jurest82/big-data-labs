"""Count and average the orders of each restaurant in windows of one minute.

The application reads the order events of a Kinesis data stream, ignores the
repeated ones, groups the new orders in windows of one minute by the time at
which they happened, and writes one item per restaurant and window to a
DynamoDB table.
"""
import json

from pyflink.table import EnvironmentSettings, TableEnvironment  # pylint: disable=import-error

PROPERTIES_FILE = '/etc/flink/application_properties.json'
PROPERTY_GROUP = 'lab13'

SOURCE = """
CREATE TABLE orders (
    event_id STRING,
    event_type STRING,
    order_id BIGINT,
    restaurant STRING,
    amount DOUBLE,
    occurred_at STRING,
    event_time AS TO_TIMESTAMP(
        REPLACE(REPLACE(occurred_at, 'T', ' '), '+00:00', '')),
    WATERMARK FOR event_time AS event_time - INTERVAL '5' SECOND
) WITH (
    'connector' = 'kinesis',
    'stream.arn' = '{stream_arn}',
    'aws.region' = '{region}',
    'source.init.position' = 'TRIM_HORIZON',
    'format' = 'json'
)
"""

SINK = """
CREATE TABLE order_windows (
    restaurant STRING,
    window_start STRING,
    orders BIGINT,
    avg_amount DOUBLE
) PARTITIONED BY (restaurant, window_start) WITH (
    'connector' = 'dynamodb',
    'table-name' = '{table_name}',
    'aws.region' = '{region}'
)
"""

# The first copy of each event_id: a repeated event has the same event_id
NEW_ORDERS = """
CREATE TEMPORARY VIEW new_orders AS
SELECT event_id, restaurant, amount, event_time
FROM (
    SELECT *, ROW_NUMBER() OVER (
        PARTITION BY event_id ORDER BY event_time ASC) AS copy
    FROM orders
    WHERE event_type = 'order_created'
)
WHERE copy = 1
"""

WINDOWS = """
INSERT INTO order_windows
SELECT
    restaurant,
    DATE_FORMAT(window_start, 'yyyy-MM-dd HH:mm'),
    COUNT(*),
    ROUND(AVG(amount), 2)
FROM TABLE(TUMBLE(TABLE new_orders, DESCRIPTOR(event_time), INTERVAL '1' MINUTE))
GROUP BY restaurant, window_start, window_end
"""


def read_properties():
    with open(PROPERTIES_FILE, encoding='utf-8') as file:
        groups = json.load(file)
    for group in groups:
        if group['PropertyGroupId'] == PROPERTY_GROUP:
            return group['PropertyMap']
    raise KeyError(PROPERTY_GROUP)


def main():
    properties = read_properties()
    environment = TableEnvironment.create(
        EnvironmentSettings.in_streaming_mode())
    environment.execute_sql(
        SOURCE.format(stream_arn=properties['stream.arn'],
                      region=properties['region']))
    environment.execute_sql(
        SINK.format(table_name=properties['table.name'],
                    region=properties['region']))
    environment.execute_sql(NEW_ORDERS)
    environment.execute_sql(WINDOWS)


if __name__ == '__main__':
    main()
