-- Lab 1B, step 2: the star schema of the warehouse.
-- The grain of the fact table is one row per order line.
-- Re-running this script recreates the warehouse tables, empty.

DROP SCHEMA IF EXISTS lab_01b CASCADE;
CREATE SCHEMA lab_01b;

CREATE TABLE lab_01b.dim_customer (
    customer_id integer PRIMARY KEY,
    name        text    NOT NULL,
    address     text    NOT NULL
);

CREATE TABLE lab_01b.dim_product (
    product_id integer PRIMARY KEY,
    name       text    NOT NULL,
    category   text    NOT NULL,
    price      integer NOT NULL
);

CREATE TABLE lab_01b.dim_city (
    city_id integer PRIMARY KEY,
    name    text    NOT NULL
);

-- The key is the date written as yyyymmdd, for example 20260914
CREATE TABLE lab_01b.dim_date (
    date_id    integer PRIMARY KEY,
    full_date  date    NOT NULL,
    year       integer NOT NULL,
    month      integer NOT NULL,
    month_name text    NOT NULL
);

CREATE TABLE lab_01b.fact_sales (
    date_id     integer NOT NULL REFERENCES lab_01b.dim_date (date_id),
    product_id  integer NOT NULL REFERENCES lab_01b.dim_product (product_id),
    customer_id integer NOT NULL REFERENCES lab_01b.dim_customer (customer_id),
    city_id     integer NOT NULL REFERENCES lab_01b.dim_city (city_id),
    quantity    integer NOT NULL,
    amount      integer NOT NULL
);

-- Run this query to see the five tables and their columns
SELECT table_name, column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'lab_01b'
ORDER BY table_name, ordinal_position;
