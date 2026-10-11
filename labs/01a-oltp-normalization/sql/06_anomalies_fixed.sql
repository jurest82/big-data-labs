-- Lab 1A, step 6: the same three operations, on the four tables.
-- In pgAdmin, run ONE block at a time.

-- Block 1: update. Ana moves. One row changes, and all her orders see it.
UPDATE lab_01a.customers
SET address = 'Carrera 15 # 90-10, Bogotá'
WHERE name = 'Ana Pérez';

SELECT DISTINCT customer_name, customer_address
FROM lab_01a.flat_orders_rebuilt
WHERE customer_name = 'Ana Pérez';

-- Block 1b: put Ana's address back
UPDATE lab_01a.customers
SET address = 'Calle 10 # 5-20, Bogotá'
WHERE name = 'Ana Pérez';


-- Block 2: delete. Marta's only order is cancelled. Delete the lines first,
-- then the order.
DELETE FROM lab_01a.order_items WHERE order_id = 10485;
DELETE FROM lab_01a.orders WHERE order_id = 10485;

-- Is Marta still a customer?
SELECT * FROM lab_01a.customers ORDER BY customer_id;


-- Block 3: insert. A new customer registers, with no orders yet.
INSERT INTO lab_01a.customers (name, address)
VALUES ('Sofía Torres', 'Calle 50 # 10-20, Medellín')
RETURNING *;


-- Block 4: the keys protect the data.
-- This statement fails because Luis still has orders. Read the error message.
DELETE FROM lab_01a.customers WHERE name = 'Luis Gómez';


-- Block 5: restore the data. Run 04_migrate_data.sql again.
