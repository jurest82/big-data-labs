-- Lab 4, step 5: the same question on each layer.
-- After each statement, look at the data scanned that Athena shows.
-- Run ONE statement at a time.

-- Statement 1: bronze, with no rules of quality
SELECT category, sum(try_cast(amount AS bigint)) AS sales
FROM bronze_orders
GROUP BY category
ORDER BY sales DESC;

-- Statement 2: silver
SELECT category, sum(amount) AS sales
FROM silver_orders
GROUP BY category
ORDER BY sales DESC;

-- Statement 3: gold
SELECT category, sales
FROM gold_sales_by_category_month
ORDER BY sales DESC;
