-- Lab 1B, step 1: the transactional database of the store, the source of the warehouse.
-- It has the same four tables and data as lab 1A, in its own schema.
-- Re-running this script recreates the schema from scratch.

DROP SCHEMA IF EXISTS lab_01b_oltp CASCADE;
CREATE SCHEMA lab_01b_oltp;

CREATE TABLE lab_01b_oltp.customers (
    customer_id integer PRIMARY KEY,
    name        text    NOT NULL,
    address     text    NOT NULL
);

CREATE TABLE lab_01b_oltp.products (
    product_id integer PRIMARY KEY,
    name       text    NOT NULL,
    category   text    NOT NULL,
    price      integer NOT NULL CHECK (price > 0)
);

CREATE TABLE lab_01b_oltp.orders (
    order_id    integer PRIMARY KEY,
    customer_id integer NOT NULL REFERENCES lab_01b_oltp.customers (customer_id),
    order_date  date    NOT NULL
);

CREATE TABLE lab_01b_oltp.order_items (
    order_id   integer NOT NULL REFERENCES lab_01b_oltp.orders (order_id),
    product_id integer NOT NULL REFERENCES lab_01b_oltp.products (product_id),
    quantity   integer NOT NULL CHECK (quantity > 0),
    PRIMARY KEY (order_id, product_id)
);

INSERT INTO lab_01b_oltp.customers (customer_id, name, address) VALUES
    (101, 'Ana Pérez',  'Calle 10 # 5-20, Bogotá'),
    (102, 'Luis Gómez', 'Carrera 7 # 12-30, Medellín'),
    (103, 'Marta Ruiz', 'Avenida 3 # 4-5, Cali');

INSERT INTO lab_01b_oltp.products (product_id, name, category, price) VALUES
    (7,  'T-shirt',  'Clothing',    30000),
    (9,  'Cap',      'Accessories', 35000),
    (12, 'Backpack', 'Accessories', 120000),
    (15, 'Shoes',    'Footwear',    150000);

INSERT INTO lab_01b_oltp.orders (order_id, customer_id, order_date) VALUES
    (10482, 101, '2026-09-14'),
    (10483, 102, '2026-09-15'),
    (10484, 102, '2026-09-16'),
    (10485, 103, '2026-09-17'),
    (10497, 101, '2026-09-21');

INSERT INTO lab_01b_oltp.order_items (order_id, product_id, quantity) VALUES
    (10482, 7,  2),
    (10482, 9,  1),
    (10483, 15, 1),
    (10484, 7,  1),
    (10485, 9,  3),
    (10497, 12, 1);

-- Run this query to count the rows: 3 customers, 4 products, 5 orders, 6 order items
SELECT 'customers' AS table_name, count(*) AS row_count FROM lab_01b_oltp.customers
UNION ALL SELECT 'products',    count(*) FROM lab_01b_oltp.products
UNION ALL SELECT 'orders',      count(*) FROM lab_01b_oltp.orders
UNION ALL SELECT 'order_items', count(*) FROM lab_01b_oltp.order_items;
