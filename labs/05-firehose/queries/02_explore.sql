-- Lab 5, step 5: explore the clicks.
-- Run ONE statement at a time.

-- Statement 1: how many clicks arrived
SELECT count(*) AS clicks FROM clicks;

-- Statement 2: the first clicks
SELECT * FROM clicks LIMIT 10;

-- Statement 3: clicks by type
SELECT event_type, count(*) AS clicks
FROM clicks
GROUP BY event_type
ORDER BY clicks DESC;

-- Statement 4: clicks by minute
SELECT date_trunc('minute', from_iso8601_timestamp(event_time)) AS minute,
       count(*) AS clicks
FROM clicks
GROUP BY 1
ORDER BY 1;
