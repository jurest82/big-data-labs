-- Lab 1A, step 3: split the flat table into four tables with keys.
-- Re-running this script recreates the four tables, empty.

DROP TABLE IF EXISTS lab_01a.order_items, lab_01a.orders, lab_01a.products, lab_01a.customers CASCADE;

CREATE TABLE lab_01a.customers (
    customer_id integer GENERATED ALWAYS AS IDENTITY (START WITH 101) PRIMARY KEY,
    name        text    NOT NULL,
    address     text    NOT NULL
);

CREATE TABLE lab_01a.products (
    product_id integer PRIMARY KEY,
    name       text    NOT NULL,
    category   text    NOT NULL,
    price      integer NOT NULL CHECK (price > 0)
);

CREATE TABLE lab_01a.orders (
    order_id    integer PRIMARY KEY,
    customer_id integer NOT NULL REFERENCES lab_01a.customers (customer_id),
    order_date  date    NOT NULL
);

-- The primary key is composite: (order_id, product_id)
CREATE TABLE lab_01a.order_items (
    order_id   integer NOT NULL REFERENCES lab_01a.orders (order_id),
    product_id integer NOT NULL REFERENCES lab_01a.products (product_id),
    quantity   integer NOT NULL CHECK (quantity > 0),
    PRIMARY KEY (order_id, product_id)
);

-- Run this query to see the four tables and their columns
SELECT table_name, column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'lab_01a'
  AND table_name IN ('customers', 'products', 'orders', 'order_items')
ORDER BY table_name, ordinal_position;
