-- Lab 4: remove the view and the tables of the lab.
-- Dropping the Iceberg tables also removes their data. Dropping bronze_orders
-- does not: its files stay in raw/orders_october/.
-- Run ONE statement at a time.

DROP VIEW bronze_orders_checked;

DROP TABLE gold_sales_by_category_month;

DROP TABLE silver_orders_rejected;

DROP TABLE silver_orders;

DROP TABLE bronze_orders;
