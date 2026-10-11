-- Lab 4, step 2: the bronze layer, the data as it arrived.
-- Replace YOUR_BUCKET with the name of your bucket (run echo $BUCKET).
-- In the Athena query editor, choose the workgroup big-data-labs and the
-- database big_data_labs, and run ONE statement at a time.

-- Statement 1: a table over the folder of the batch, with every column as text
CREATE EXTERNAL TABLE bronze_orders (
    order_id      string,
    order_date    string,
    customer_id   string,
    customer_name string,
    city          string,
    product_id    string,
    product_name  string,
    category      string,
    quantity      string,
    unit_price    string,
    amount        string
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
    'separatorChar' = ',',
    'quoteChar' = '"',
    'escapeChar' = '\\'
)
STORED AS TEXTFILE
LOCATION 's3://YOUR_BUCKET/raw/orders_october/'
TBLPROPERTIES ('skip.header.line.count' = '1');

-- Statement 2: how many lines arrived
SELECT count(*) AS order_lines FROM bronze_orders;

-- Statement 3: the first lines
SELECT * FROM bronze_orders LIMIT 10;

-- Statement 4: lines of an order and a product that appear more than once
SELECT count(*) AS repeated_keys
FROM (
    SELECT order_id, product_id
    FROM bronze_orders
    GROUP BY order_id, product_id
    HAVING count(*) > 1
);

-- Statement 5: dates that are not valid
SELECT order_date, count(*) AS order_lines
FROM bronze_orders
WHERE try(CAST(order_date AS date)) IS NULL
GROUP BY order_date
ORDER BY order_lines DESC;

-- Statement 6: quantities that are not positive
SELECT quantity, count(*) AS order_lines
FROM bronze_orders
WHERE try_cast(quantity AS integer) <= 0
GROUP BY quantity
ORDER BY quantity;

-- Statement 7: lines with no customer
SELECT count(*) AS order_lines
FROM bronze_orders
WHERE trim(coalesce(customer_id, '')) = '';

-- Statement 8: lines whose amount is not quantity times unit price
SELECT count(*) AS order_lines
FROM bronze_orders
WHERE try_cast(amount AS bigint)
      <> try_cast(quantity AS bigint) * try_cast(unit_price AS bigint);
