# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Flights data generator (`labs/shared/generator/generate_flights.py`) with tests: deterministic flights of an airline in nine monthly CSV files (10 million by default), plus airports, airlines and aircraft
- Lab 6: Apache Spark on your computer, with its diagram in `docs/`, a notebook with the flights that shows lazy evaluation, partitions, stages and the shuffle in the web UI of Spark, Spark SQL, a broadcast join, a window function and a comparison with pandas
- Lab 7: Parquet and partitioning with Spark, with its diagram in `docs/` and a notebook that writes the flights as Parquet flat, by month and by day, shows partition pruning in the plan and in the web UI of Spark, and compares four compression codecs
- Development container: Java 17, PySpark, pandas, pyarrow and the Jupyter kernel in the image, the Jupyter extension for Visual Studio Code, and port 4040 for the web UI of Spark

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
