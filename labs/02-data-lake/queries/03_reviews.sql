-- Lab 2, step 5: the reviews, which are JSON files.
-- Run ONE statement at a time.

-- Statement 1: how many reviews of each rating
SELECT rating, count(*) AS reviews
FROM reviews
GROUP BY rating
ORDER BY rating;

-- Statement 2: the review of order 10482. Only some reviews have tags.
SELECT * FROM reviews WHERE order_id = 10482;

-- Statement 3: the most common tags. UNNEST turns each element of the array
-- into its own row.
SELECT tag, count(*) AS reviews
FROM reviews
CROSS JOIN UNNEST(tags) AS t (tag)
GROUP BY tag
ORDER BY reviews DESC;

-- Statement 4: reviews and average rating by city. The city is in the CSV
-- files and the rating in the JSON files: Athena joins both.
SELECT o.city,
       count(*) AS reviews,
       round(avg(r.rating), 2) AS average_rating
FROM reviews AS r
JOIN (SELECT DISTINCT order_id, city FROM orders) AS o
  ON o.order_id = r.order_id
GROUP BY o.city
ORDER BY reviews DESC;
