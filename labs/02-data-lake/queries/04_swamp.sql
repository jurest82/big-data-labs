-- Lab 2, steps 6 and 7: what changed in the lake.
-- Run these statements before and after the second file of orders.
-- Run ONE statement at a time.

-- Statement 1: the tables of the database
SHOW TABLES;

-- Statement 2: the columns of orders
DESCRIBE orders;

-- Statement 3: the rows of orders
SELECT count(*) AS order_lines FROM orders;

-- Statement 4: a sample of orders
SELECT * FROM orders LIMIT 10;

-- Statement 5: the orders of the other branch. Their ids start at 900000.
SELECT * FROM orders WHERE order_id >= 900000 LIMIT 10;
