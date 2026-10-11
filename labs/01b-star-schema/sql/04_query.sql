-- Lab 1B, step 4: sales by category and month.
-- In pgAdmin, run ONE block at a time.

-- Block 1: sales by category and month on the star schema.
-- It joins the fact table with two dimensions.
SELECT p.category, d.year, d.month, SUM(f.amount) AS sales
FROM lab_01b.fact_sales AS f
JOIN lab_01b.dim_product AS p ON p.product_id = f.product_id
JOIN lab_01b.dim_date    AS d ON d.date_id = f.date_id
GROUP BY p.category, d.year, d.month
ORDER BY sales DESC;


-- Block 2: the same question on the transactional tables.
-- The result must be the same, so the load lost nothing.
SELECT p.category,
       extract(year FROM o.order_date)  AS year,
       extract(month FROM o.order_date) AS month,
       SUM(oi.quantity * p.price)       AS sales
FROM lab_01b_oltp.order_items AS oi
JOIN lab_01b_oltp.orders      AS o ON o.order_id = oi.order_id
JOIN lab_01b_oltp.products    AS p ON p.product_id = oi.product_id
GROUP BY p.category, extract(year FROM o.order_date), extract(month FROM o.order_date)
ORDER BY sales DESC;
