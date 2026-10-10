-- Lab 3, step 1: create an Iceberg table from the CSV table of lab 2.
-- Replace YOUR_BUCKET with the name of your bucket (run echo $BUCKET).
-- In the Athena query editor, choose the workgroup big-data-labs and the
-- database big_data_labs, and run ONE statement at a time.

-- Statement 1: the source table
SELECT count(*) AS order_lines FROM orders;

-- Statement 2: create the Iceberg table with the same rows
CREATE TABLE orders_iceberg
WITH (
    table_type = 'ICEBERG',
    is_external = false,
    location = 's3://YOUR_BUCKET/iceberg/orders/',
    format = 'PARQUET'
) AS
SELECT order_id,
       CAST(order_date AS date) AS order_date,
       customer_id,
       customer_name,
       city,
       product_id,
       product_name,
       category,
       quantity,
       unit_price,
       amount
FROM orders;

-- Statement 3: the new table
SELECT count(*) AS order_lines FROM orders_iceberg;
