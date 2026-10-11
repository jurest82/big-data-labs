-- Lab 1A, step 4: move the data from the flat table into the four tables.
-- Re-running this script empties the four tables and loads them again.

TRUNCATE lab_01a.order_items, lab_01a.orders, lab_01a.products, lab_01a.customers RESTART IDENTITY CASCADE;

-- Each customer is stored once
INSERT INTO lab_01a.customers (name, address)
SELECT DISTINCT customer_name, customer_address
FROM lab_01a.flat_orders
ORDER BY customer_name;

-- The flat table has no category or price, so the catalog is entered by hand.
-- The identifiers match the ones used in the course slides.
INSERT INTO lab_01a.products (product_id, name, category, price) VALUES
    (7,  'T-shirt',  'Clothing',    30000),
    (9,  'Cap',      'Accessories', 35000),
    (12, 'Backpack', 'Accessories', 120000),
    (15, 'Shoes',    'Footwear',    150000);

-- Each order is stored once
INSERT INTO lab_01a.orders (order_id, customer_id, order_date)
SELECT DISTINCT f.order_id, c.customer_id, f.order_date
FROM lab_01a.flat_orders AS f
JOIN lab_01a.customers AS c ON c.name = f.customer_name;

-- Each line of an order is one product with its quantity
INSERT INTO lab_01a.order_items (order_id, product_id, quantity)
SELECT f.order_id, p.product_id, f.quantity
FROM lab_01a.flat_orders AS f
JOIN lab_01a.products AS p ON p.name = f.product_name;

-- Run this query to count the rows: 3 customers, 4 products, 5 orders, 6 order items
SELECT 'customers' AS table_name, count(*) AS row_count FROM lab_01a.customers
UNION ALL SELECT 'products',    count(*) FROM lab_01a.products
UNION ALL SELECT 'orders',      count(*) FROM lab_01a.orders
UNION ALL SELECT 'order_items', count(*) FROM lab_01a.order_items;
