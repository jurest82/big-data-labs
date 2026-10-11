-- Lab 5, step 5: from the visit to the purchase.
-- Run ONE statement at a time.

-- Statement 1: the funnel of each category
SELECT category,
       count_if(event_type = 'page_view') AS page_views,
       count_if(event_type = 'add_to_cart') AS add_to_cart,
       count_if(event_type = 'purchase') AS purchases,
       round(100.0 * count_if(event_type = 'purchase')
             / count_if(event_type = 'page_view'), 2) AS conversion_percent
FROM clicks
GROUP BY category
ORDER BY purchases DESC;

-- Statement 2: the sales of the purchases
SELECT category, sum(amount) AS sales
FROM clicks
WHERE event_type = 'purchase'
GROUP BY category
ORDER BY sales DESC;

-- Statement 3: clicks of visitors who were not signed in
SELECT count(*) AS clicks FROM clicks WHERE customer_id IS NULL;
