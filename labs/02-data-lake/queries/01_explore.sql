-- Lab 2, step 5: explore the tables the crawler created.
-- In the Athena query editor, choose the workgroup big-data-labs and the
-- database big_data_labs, and run ONE statement at a time.

-- Statement 1: the tables of the database
SHOW TABLES;

-- Statement 2: the first rows of orders
SELECT * FROM orders LIMIT 10;

-- Statement 3: how many order lines and how many orders
SELECT count(*) AS order_lines, count(DISTINCT order_id) AS orders
FROM orders;
