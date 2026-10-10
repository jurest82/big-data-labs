-- Lab 3, step 3: correct order 10482.
-- The customer asks for 3 T-shirts instead of 2.
-- Run ONE statement at a time.

-- Statement 1: the order before the correction
SELECT order_id, product_name, quantity, amount
FROM orders_iceberg
WHERE order_id = 10482
ORDER BY product_id;

-- Statement 2: the correction
UPDATE orders_iceberg
SET quantity = 3, amount = 90000
WHERE order_id = 10482 AND product_id = 7;

-- Statement 3: the order after the correction
SELECT order_id, product_name, quantity, amount
FROM orders_iceberg
WHERE order_id = 10482
ORDER BY product_id;

-- Statement 4: the versions of the table and the files each one added
SELECT committed_at,
       operation,
       summary['added-data-files'] AS added_data_files,
       coalesce(summary['added-delete-files'], '0') AS added_delete_files
FROM "orders_iceberg$snapshots"
ORDER BY committed_at;

-- Statement 5: the data files of the table. The file of deletes is not listed.
SELECT content, file_path, record_count
FROM "orders_iceberg$files"
ORDER BY record_count DESC;
