-- Lab 3, step 5: add a column to the table.
-- The store wants to know the channel of each order.
-- Run ONE statement at a time.

-- Statement 1: add the column
ALTER TABLE orders_iceberg ADD COLUMNS (channel string);

-- Statement 2: the old rows have no value for it
SELECT order_id, product_name, channel
FROM orders_iceberg
WHERE order_id = 10482
ORDER BY product_id;

-- Statement 3: give a channel to order 10482
UPDATE orders_iceberg SET channel = 'web' WHERE order_id = 10482;

-- Statement 4: a new order that arrives through the app
INSERT INTO orders_iceberg (
    order_id, order_date, customer_id, customer_name, city, product_id,
    product_name, category, quantity, unit_price, amount, channel
)
VALUES (
    300000, DATE '2026-10-01', 101, 'Ana Pérez', 'Bogotá', 12,
    'Backpack', 'Accessories', 1, 120000, 120000, 'app'
);

-- Statement 5: orders by channel
SELECT channel, count(*) AS order_lines
FROM orders_iceberg
GROUP BY channel
ORDER BY order_lines DESC;
