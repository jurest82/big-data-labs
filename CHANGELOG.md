# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Lab 10: Apache Kafka on your computer, with its diagram in `docs/`, a single-node Kafka service in the development container and four Python scripts (create the topic, a producer of order events with the order id as the key, a consumer of a group that confirms its position and a command that shows the offsets and the lag) that show partitions, keys, offsets, confirmed positions, consumer groups and the rebalance
- Lab 11: from Kafka to PostgreSQL, with its diagram in `docs/`, a notebook that starts a generator of random order events and two consumers that insert them into two tables of the local PostgreSQL, stops the consumers like a crash would, shows the repeated events in the table without a key and none in the one with `event_id` as its primary key, adds a second consumer to a group and reprocesses every event from the beginning
- Lab 12: order events in real time with Kinesis Data Streams, with its own stack (a stream with two shards, a DynamoDB table and a Lambda function that reads the stream and writes each event to the table), a Python producer with its tests, and its diagram in `docs/`
- Development container: the Kafka service (`apache/kafka:4.3.2`) and the `confluent-kafka` client in the image

## [1.1.0] - 18/10/2026

### Added

- Flights data generator (`labs/shared/generator/generate_flights.py`) with tests: deterministic flights of an airline in nine monthly CSV files (10 million by default), plus airports, airlines and aircraft
- Lab 6: Apache Spark on your computer, with its diagram in `docs/`, a notebook with the flights that shows lazy evaluation, partitions, stages and the shuffle in the web UI of Spark, Spark SQL, a broadcast join, a window function and a comparison with pandas
- Lab 7: Parquet and partitioning with Spark, with its diagram in `docs/` and a notebook that writes the flights as Parquet flat, by month and by day, shows partition pruning in the plan and in the web UI of Spark, and compares four compression codecs
- Lab 8: PostgreSQL and Spark SQL on the same flights, with its diagram in `docs/` and a notebook that loads 1, 5, 10, 15 and 20 million flights into both engines, runs an analytic query and a lookup by `flight_id` in each one, and builds the comparison tables itself
- Lab 9: a batch pipeline with AWS Glue, with its own stack (an S3 bucket, a Glue job, a Step Functions state machine with a retry, an EventBridge schedule and their IAM roles), a Spark script that computes the average departure delay of each airline by month, and its diagram in `docs/`
- Development container: Java 17, PySpark, pandas, pyarrow, the Jupyter kernel and the AWS Glue library in the image, the Jupyter extension for Visual Studio Code, and port 4040 for the web UI of Spark

## [1.0.0] - 11/10/2026

### Added

- Development environment: a multi-stage Docker image and a dev container with the local PostgreSQL and pgAdmin services, formatting and linting (Prettier, yapf, pylint and markdownlint), spell checking with cspell and a project dictionary, and LF line endings on every platform
- Data generator (`labs/shared/generator/`) with tests: deterministic data for an online store (orders in monthly CSV files, reviews in JSON Lines and product photos), a file from a second branch with different columns, and a batch of orders with defects
- Base Serverless stack (`labs/shared/serverless/base/`): an S3 bucket for the lake, a Glue database and an Athena workgroup, shared by labs 2 to 4 through SSM parameters
- Lab 1A: OLTP anomalies, normalization and JOINs, on the local PostgreSQL
- Lab 1B: a star schema and a data mart, on the local PostgreSQL
- Lab 2: a data lake with S3, a Glue crawler and Athena, including a data swamp
- Lab 3: an Apache Iceberg table in Athena, with `UPDATE`, time travel and a new column
- Lab 4: bronze, silver and gold layers with SQL in Athena, with quality rules, the rejected rows kept apart and a comparison of the data scanned by each layer
- Lab 5: click events delivered to S3 by Amazon Data Firehose, with its own stack, a Python producer and queries in Athena. It needs the paid plan of the AWS account, and its README explains how to upgrade
- Diagrams of every lab (`docs/`), generated with Graphviz by `docs/architecture.py`: the data model of labs 1A and 1B and the architecture of labs 2 to 5, in a full and a small size, shown in each lab README and in the root README
