-- Lab 4, step 3: the silver layer, clean and validated.
-- Replace YOUR_BUCKET with the name of your bucket (run echo $BUCKET).
-- Run ONE statement at a time.

-- Statement 1: a view that applies the rules of quality to the bronze table.
-- Each line gets a reject_reason, or none if it passes every rule.
CREATE OR REPLACE VIEW bronze_orders_checked AS
WITH typed AS (
    SELECT *,
           try(CAST(order_date AS date)) AS date_value,
           try_cast(quantity AS integer) AS quantity_value,
           try_cast(unit_price AS bigint) AS unit_price_value,
           try_cast(amount AS bigint) AS amount_value
    FROM bronze_orders
),
checked AS (
    SELECT *,
           CASE
               WHEN date_value IS NULL THEN 'invalid_date'
               WHEN quantity_value IS NULL OR quantity_value <= 0
                   THEN 'invalid_quantity'
               WHEN amount_value IS NULL
                   OR amount_value <> quantity_value * unit_price_value
                   THEN 'amount_mismatch'
               WHEN trim(coalesce(customer_id, '')) = '' THEN 'missing_customer'
           END AS first_reason
    FROM typed
)
SELECT order_id, order_date, customer_id, customer_name, city, product_id,
       product_name, category, quantity, unit_price, amount,
       CASE
           WHEN first_reason IS NOT NULL THEN first_reason
           WHEN row_number() OVER (
               PARTITION BY order_id, product_id, first_reason
               ORDER BY order_date
           ) > 1 THEN 'duplicate'
       END AS reject_reason
FROM checked;

-- Statement 2: what happens to the lines of the bronze layer
SELECT coalesce(reject_reason, 'valid') AS result, count(*) AS order_lines
FROM bronze_orders_checked
GROUP BY 1
ORDER BY order_lines DESC;

-- Statement 3: the silver table, with the lines that passed, typed
CREATE TABLE silver_orders
WITH (
    table_type = 'ICEBERG',
    is_external = false,
    location = 's3://YOUR_BUCKET/silver/orders/',
    format = 'PARQUET'
) AS
SELECT CAST(order_id AS bigint) AS order_id,
       CAST(order_date AS date) AS order_date,
       CAST(customer_id AS bigint) AS customer_id,
       customer_name,
       city,
       CAST(product_id AS bigint) AS product_id,
       product_name,
       category,
       CAST(quantity AS integer) AS quantity,
       CAST(unit_price AS bigint) AS unit_price,
       CAST(amount AS bigint) AS amount
FROM bronze_orders_checked
WHERE reject_reason IS NULL;

-- Statement 4: the lines that did not pass, with the reason
CREATE TABLE silver_orders_rejected
WITH (
    table_type = 'ICEBERG',
    is_external = false,
    location = 's3://YOUR_BUCKET/silver/orders_rejected/',
    format = 'PARQUET'
) AS
SELECT *
FROM bronze_orders_checked
WHERE reject_reason IS NOT NULL;

-- Statement 5: the lines that passed and the lines that did not
SELECT 'silver_orders' AS table_name, count(*) AS order_lines
FROM silver_orders
UNION ALL
SELECT 'silver_orders_rejected', count(*) FROM silver_orders_rejected;

-- Statement 6: why the lines were rejected
SELECT reject_reason, count(*) AS order_lines
FROM silver_orders_rejected
GROUP BY reject_reason
ORDER BY order_lines DESC;
