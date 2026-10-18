"""Glue job: the average departure delay of each airline by month."""
import sys

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark import SparkContext
from pyspark.sql import functions as F

SCHEMA = ('flight_id long, flight_date date, airline_code string, '
          'flight_number string, tail_number string, origin string, '
          'destination string, scheduled_departure timestamp, '
          'actual_departure timestamp, distance_km int, cancelled int')

args = getResolvedOptions(sys.argv, ['JOB_NAME', 'input_path', 'output_path'])
glue = GlueContext(SparkContext.getOrCreate())
spark = glue.spark_session
job = Job(glue)
job.init(args['JOB_NAME'], args)

flights = spark.read.csv(args['input_path'], header=True, schema=SCHEMA)
print(f'Flights read: {flights.count()}')

delay_seconds = (F.unix_timestamp('actual_departure') -
                 F.unix_timestamp('scheduled_departure'))
completed = flights.where(F.col('cancelled') == 0)
by_month = completed.groupBy(
    'airline_code',
    F.date_format('flight_date', 'yyyy-MM').alias('month'))
delays = by_month.agg(
    F.count('*').alias('flights'),
    F.round(F.avg(delay_seconds / 60), 1).alias('avg_delay_min'))
result = delays.orderBy('airline_code', 'month').coalesce(1)
result.write.mode('overwrite').parquet(args['output_path'])

job.commit()
