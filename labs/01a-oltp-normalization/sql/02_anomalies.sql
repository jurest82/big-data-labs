-- Lab 1A, step 2: the three anomalies of a flat table.
-- The experiments run on a copy, so the original table stays intact.
-- In pgAdmin, run ONE block at a time.

-- Block 0: make the copy (run it once)
DROP TABLE IF EXISTS lab_01a.flat_orders_copy;
CREATE TABLE lab_01a.flat_orders_copy (LIKE lab_01a.flat_orders INCLUDING ALL);
INSERT INTO lab_01a.flat_orders_copy SELECT * FROM lab_01a.flat_orders;


-- Block 1: update anomaly.
-- Ana moves, but someone updates only one of her three rows.
UPDATE lab_01a.flat_orders_copy
SET customer_address = 'Carrera 15 # 90-10, Bogotá'
WHERE order_id = 10482 AND product_name = 'Cap';

-- How many addresses does Ana have now?
SELECT DISTINCT customer_name, customer_address
FROM lab_01a.flat_orders_copy
WHERE customer_name = 'Ana Pérez';


-- Block 2: delete anomaly.
-- Marta's only order is cancelled and its row is deleted.
DELETE FROM lab_01a.flat_orders_copy WHERE order_id = 10485;

-- Is Marta still a customer?
SELECT DISTINCT customer_name FROM lab_01a.flat_orders_copy ORDER BY customer_name;


-- Block 3: insert anomaly.
-- A new customer registers, but has not bought anything yet.
-- This statement fails. Read the error message.
INSERT INTO lab_01a.flat_orders_copy (customer_name, customer_address)
VALUES ('Sofía Torres', 'Calle 50 # 10-20, Medellín');
