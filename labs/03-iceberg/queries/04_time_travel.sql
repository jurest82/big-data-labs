-- Lab 3, step 4: query the table as it was before the correction.
-- Replace FIRST_SNAPSHOT_ID with the snapshot_id of the oldest version, and
-- FIRST_COMMITTED_AT with its committed_at, as in
-- 2026-10-10 20:15:32.123 UTC. Both come from statement 1.
-- Run ONE statement at a time.

-- Statement 1: the versions of the table
SELECT committed_at, snapshot_id, operation
FROM "orders_iceberg$snapshots"
ORDER BY committed_at;

-- Statement 2: order 10482 as of a version
SELECT order_id, product_name, quantity, amount
FROM orders_iceberg FOR VERSION AS OF FIRST_SNAPSHOT_ID
WHERE order_id = 10482
ORDER BY product_id;

-- Statement 3: order 10482 as of a moment
SELECT order_id, product_name, quantity, amount
FROM orders_iceberg FOR TIMESTAMP AS OF TIMESTAMP 'FIRST_COMMITTED_AT'
WHERE order_id = 10482
ORDER BY product_id;

-- Statement 4: order 10482 now
SELECT order_id, product_name, quantity, amount
FROM orders_iceberg
WHERE order_id = 10482
ORDER BY product_id;
