-- Lab 3, step 2: look inside the table with its metadata tables.
-- Run ONE statement at a time.

-- Statement 1: the versions (snapshots) of the table
SELECT * FROM "orders_iceberg$snapshots";

-- Statement 2: the files of the table. content 0 is a data file.
SELECT content, file_path, file_format, record_count
FROM "orders_iceberg$files";

-- Statement 3: the history of the table
SELECT * FROM "orders_iceberg$history";
