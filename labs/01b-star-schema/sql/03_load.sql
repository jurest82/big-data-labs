-- Lab 1B, step 3: load the warehouse from the transactional tables.
-- Re-running this script empties the five tables and loads them again.

TRUNCATE lab_01b.fact_sales, lab_01b.dim_customer, lab_01b.dim_product, lab_01b.dim_city, lab_01b.dim_date;

INSERT INTO lab_01b.dim_customer (customer_id, name, address)
SELECT customer_id, name, address
FROM lab_01b_oltp.customers;

INSERT INTO lab_01b.dim_product (product_id, name, category, price)
SELECT product_id, name, category, price
FROM lab_01b_oltp.products;

-- The city is the last part of the address, after the comma
INSERT INTO lab_01b.dim_city (city_id, name)
SELECT row_number() OVER (ORDER BY city), city
FROM (
    SELECT DISTINCT split_part(address, ', ', 2) AS city
    FROM lab_01b_oltp.customers
) AS cities;

INSERT INTO lab_01b.dim_date (date_id, full_date, year, month, month_name)
SELECT DISTINCT
       to_char(order_date, 'YYYYMMDD')::integer,
       order_date,
       extract(year FROM order_date),
       extract(month FROM order_date),
       to_char(order_date, 'FMMonth')
FROM lab_01b_oltp.orders;

-- One row per order line, with the key of each dimension
INSERT INTO lab_01b.fact_sales (date_id, product_id, customer_id, city_id, quantity, amount)
SELECT to_char(o.order_date, 'YYYYMMDD')::integer,
       oi.product_id,
       o.customer_id,
       ci.city_id,
       oi.quantity,
       oi.quantity * p.price
FROM lab_01b_oltp.order_items AS oi
JOIN lab_01b_oltp.orders    AS o ON o.order_id = oi.order_id
JOIN lab_01b_oltp.products  AS p ON p.product_id = oi.product_id
JOIN lab_01b_oltp.customers AS c ON c.customer_id = o.customer_id
JOIN lab_01b.dim_city       AS ci ON ci.name = split_part(c.address, ', ', 2);

-- Run this query to count the rows: 3 customers, 4 products, 3 cities, 5 dates, 6 sales
SELECT 'dim_customer' AS table_name, count(*) AS row_count FROM lab_01b.dim_customer
UNION ALL SELECT 'dim_product', count(*) FROM lab_01b.dim_product
UNION ALL SELECT 'dim_city',    count(*) FROM lab_01b.dim_city
UNION ALL SELECT 'dim_date',    count(*) FROM lab_01b.dim_date
UNION ALL SELECT 'fact_sales',  count(*) FROM lab_01b.fact_sales;
