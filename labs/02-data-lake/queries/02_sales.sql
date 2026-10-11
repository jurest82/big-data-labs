-- Lab 2, step 5: sales by category and month.
-- Run ONE statement at a time.

-- Statement 1: sales by category and month
SELECT category,
       year(CAST(order_date AS date)) AS year,
       month(CAST(order_date AS date)) AS month,
       sum(amount) AS sales
FROM orders
GROUP BY 1, 2, 3
ORDER BY 3, 4 DESC;

-- Statement 2: sales by city
SELECT city, sum(amount) AS sales
FROM orders
GROUP BY city
ORDER BY sales DESC;
