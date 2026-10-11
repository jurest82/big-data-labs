-- Lab 5, step 6: the batches that Firehose delivered.
-- Run ONE statement at a time.

-- Statement 1: one row for each file in the bucket
SELECT "$path" AS file,
       count(*) AS clicks,
       min(event_time) AS first_click,
       max(event_time) AS last_click
FROM clicks
GROUP BY "$path"
ORDER BY first_click;
