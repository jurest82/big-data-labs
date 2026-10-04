-- Lab 1A, step 5: rebuild an order with JOIN.
-- In pgAdmin, run ONE block at a time.

-- Block 1: order 10482, the same query as the slide
SELECT c.name, o.order_date, p.name AS product, oi.quantity
FROM lab_01a.orders AS o
JOIN lab_01a.customers   AS c  ON c.customer_id = o.customer_id
JOIN lab_01a.order_items AS oi ON oi.order_id = o.order_id
JOIN lab_01a.products    AS p  ON p.product_id = oi.product_id
WHERE o.order_id = 10482;


-- Block 2: a view that rebuilds the original flat table from the four tables
CREATE OR REPLACE VIEW lab_01a.flat_orders_rebuilt AS
SELECT o.order_id,
       o.order_date,
       c.name AS customer_name,
       c.address AS customer_address,
       p.name AS product_name,
       oi.quantity,
       oi.quantity * p.price AS amount
FROM lab_01a.orders AS o
JOIN lab_01a.customers   AS c  ON c.customer_id = o.customer_id
JOIN lab_01a.order_items AS oi ON oi.order_id = o.order_id
JOIN lab_01a.products    AS p  ON p.product_id = oi.product_id;


-- Block 3: did we lose anything? Both queries must return 0 rows.
SELECT * FROM lab_01a.flat_orders
EXCEPT
SELECT * FROM lab_01a.flat_orders_rebuilt;

SELECT * FROM lab_01a.flat_orders_rebuilt
EXCEPT
SELECT * FROM lab_01a.flat_orders;
