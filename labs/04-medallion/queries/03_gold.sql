-- Lab 4, step 4: the gold layer, ready for the analytics.
-- Replace YOUR_BUCKET with the name of your bucket (run echo $BUCKET).
-- Run ONE statement at a time.

-- Statement 1: sales by category and month, calculated from the silver layer
CREATE TABLE gold_sales_by_category_month
WITH (
    table_type = 'ICEBERG',
    is_external = false,
    location = 's3://YOUR_BUCKET/gold/sales_by_category_month/',
    format = 'PARQUET'
) AS
SELECT category,
       year(order_date) AS year,
       month(order_date) AS month,
       count(*) AS order_lines,
       sum(quantity) AS units,
       sum(amount) AS sales
FROM silver_orders
GROUP BY category, year(order_date), month(order_date);

-- Statement 2: the gold table
SELECT * FROM gold_sales_by_category_month ORDER BY sales DESC;
