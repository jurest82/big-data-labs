-- Lab 1B, step 5: a data mart for the marketing team.
-- In pgAdmin, run ONE block at a time.

-- Block 1: the data mart, a view with sales by category and city
CREATE OR REPLACE VIEW lab_01b.mart_marketing_sales AS
SELECT p.category, ci.name AS city, SUM(f.quantity) AS units, SUM(f.amount) AS sales
FROM lab_01b.fact_sales AS f
JOIN lab_01b.dim_product AS p  ON p.product_id = f.product_id
JOIN lab_01b.dim_city    AS ci ON ci.city_id = f.city_id
GROUP BY p.category, ci.name;


-- Block 2: marketing queries the data mart, with no JOIN
SELECT * FROM lab_01b.mart_marketing_sales ORDER BY sales DESC;
