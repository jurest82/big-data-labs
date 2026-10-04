-- Lab 1A, step 1: one flat table with everything about an order.
-- Re-running this script recreates the lab schema from scratch.

DROP SCHEMA IF EXISTS lab_01a CASCADE;
CREATE SCHEMA lab_01a;

CREATE TABLE lab_01a.flat_orders (
    order_id         integer NOT NULL,
    order_date       date    NOT NULL,
    customer_name    text    NOT NULL,
    customer_address text    NOT NULL,
    product_name     text    NOT NULL,
    quantity         integer NOT NULL,
    amount           integer NOT NULL
);

INSERT INTO lab_01a.flat_orders VALUES
    (10482, '2026-09-14', 'Ana Pérez',  'Calle 10 # 5-20, Bogotá',      'T-shirt',  2,  60000),
    (10482, '2026-09-14', 'Ana Pérez',  'Calle 10 # 5-20, Bogotá',      'Cap',      1,  35000),
    (10497, '2026-09-21', 'Ana Pérez',  'Calle 10 # 5-20, Bogotá',      'Backpack', 1, 120000),
    (10483, '2026-09-15', 'Luis Gómez', 'Carrera 7 # 12-30, Medellín',  'Shoes',    1, 150000),
    (10484, '2026-09-16', 'Luis Gómez', 'Carrera 7 # 12-30, Medellín',  'T-shirt',  1,  30000),
    (10485, '2026-09-17', 'Marta Ruiz', 'Avenida 3 # 4-5, Cali',        'Cap',      3, 105000);

-- Run this query to see the table
SELECT * FROM lab_01a.flat_orders ORDER BY order_id, product_name;
