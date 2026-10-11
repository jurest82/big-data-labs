"""Generate the sample data of the online store used by the data lake labs.

It writes three kinds of files, one folder each:

- orders/: CSV files with one row per order line, one file per month.
- reviews/: JSON Lines files, one review per line, one file per month.
- photos/: one small PNG per product.

It also writes swamp/orders_branch_b.csv, a file of orders with other column
names, used to show what happens to a lake without rules.

It also writes orders_october/orders-2026-10.csv, a batch of orders with the
defects of real data (duplicated lines, invalid dates, invalid quantities,
amounts that do not match, and missing customers), used to build the layers of
a medallion architecture.

The data is deterministic: the same seed produces the same files.
"""
import argparse
import csv
import json
import random
import struct
import zlib
from contextlib import ExitStack
from datetime import date, timedelta
from pathlib import Path

from faker import Faker

DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / 'output'
FIRST_ORDER_ID = 10000
FIRST_CUSTOMER_ID = 101
OCTOBER_FIRST_ORDER_ID = 210000
OCTOBER_START = date(2026, 10, 1)
OCTOBER_END = date(2026, 10, 31)
START_DATE = date(2026, 7, 1)
END_DATE = date(2026, 9, 30)

# product_id, name, category, unit price. The first four match lab 1.
PRODUCTS = [
    (7, 'T-shirt', 'Clothing', 30000),
    (9, 'Cap', 'Accessories', 35000),
    (12, 'Backpack', 'Accessories', 120000),
    (15, 'Shoes', 'Footwear', 150000),
    (21, 'Jeans', 'Clothing', 90000),
    (22, 'Jacket', 'Clothing', 180000),
    (23, 'Hoodie', 'Clothing', 110000),
    (31, 'Belt', 'Accessories', 45000),
    (32, 'Sunglasses', 'Accessories', 85000),
    (33, 'Wallet', 'Accessories', 70000),
    (34, 'Watch', 'Accessories', 220000),
    (41, 'Sneakers', 'Footwear', 170000),
    (42, 'Sandals', 'Footwear', 60000),
    (43, 'Boots', 'Footwear', 210000),
]
PRODUCTS_BY_ID = {
    product[0]: product
    for product in PRODUCTS
}

CITIES = [
    'Bogotá', 'Medellín', 'Cali', 'Barranquilla', 'Cartagena', 'Bucaramanga',
    'Pereira'
]

# The customers of lab 1 keep their identifiers.
FIXED_CUSTOMERS = [
    (101, 'Ana Pérez', 'Bogotá'),
    (102, 'Luis Gómez', 'Medellín'),
    (103, 'Marta Ruiz', 'Cali'),
]

# The order that lab 3 updates: the same one used in lab 1.
FIXED_ORDER_ID = 10482
FIXED_ORDER_DATE = date(2026, 9, 14)
FIXED_ORDER_CUSTOMER_ID = 101
FIXED_ORDER_LINES = [(7, 2), (9, 1)]
FIXED_REVIEW = {
    'rating': 4,
    'comment': 'Arrived fast, but the box was damaged',
    'tags': ['shipping', 'packaging'],
}

ORDER_COLUMNS = [
    'order_id', 'order_date', 'customer_id', 'customer_name', 'city',
    'product_id', 'product_name', 'category', 'quantity', 'unit_price', 'amount'
]
SWAMP_COLUMNS = ['order_number', 'date', 'client', 'item', 'qty', 'total']

COMMENTS = {
    1: ['Never arrived on time', 'The product broke after two days'],
    2: ['Not what I expected', 'The size was wrong'],
    3: ['It is fine for the price', 'Average quality'],
    4: ['Good product, would buy again', 'Fast delivery and fair price'],
    5: ['Excellent quality', 'Exactly what I was looking for'],
}
TAGS = ['shipping', 'packaging', 'price', 'quality', 'size', 'support']
RATING_WEIGHTS = [5, 8, 17, 35, 35]
LINES_PER_ORDER_WEIGHTS = [45, 30, 18, 7]

# The share of the lines of the October batch that have each defect.
DEFECT_RATES = {
    'duplicate': 0.03,
    'invalid_date': 0.01,
    'invalid_quantity': 0.01,
    'amount_mismatch': 0.02,
    'missing_customer': 0.02,
}


def random_date(rng, first, last):
    return first + timedelta(days=rng.randint(0, (last - first).days))


def month_key(day):
    return day.strftime('%Y-%m')


def make_customers(rng, count):
    fake = Faker('es_CO')
    fake.seed_instance(rng.randint(0, 2**32 - 1))
    customers = list(FIXED_CUSTOMERS)
    next_id = FIRST_CUSTOMER_ID + len(customers)
    while len(customers) < count:
        customers.append((next_id, fake.name(), rng.choice(CITIES)))
        next_id += 1
    return customers


def make_order_lines(rng, order_id):
    """Return the (product_id, quantity) lines of an order."""
    if order_id == FIXED_ORDER_ID:
        return list(FIXED_ORDER_LINES)
    line_count = rng.choices([1, 2, 3, 4], LINES_PER_ORDER_WEIGHTS)[0]
    products = rng.sample(PRODUCTS, line_count)
    return [(product[0], rng.randint(1, 3)) for product in products]


def make_orders(rng, count, customers):
    """Return a list of (order_id, order_date, customer, lines)."""
    orders = []
    for index in range(count):
        order_id = FIRST_ORDER_ID + index
        if order_id == FIXED_ORDER_ID:
            order_date = FIXED_ORDER_DATE
            customer = customers[FIXED_ORDER_CUSTOMER_ID - FIRST_CUSTOMER_ID]
        else:
            order_date = random_date(rng, START_DATE, END_DATE)
            customer = rng.choice(customers)
        orders.append(
            (order_id, order_date, customer, make_order_lines(rng, order_id)))
    return orders


class MonthlyFiles:
    """Open one file per month, the first time that month is needed."""

    def __init__(self, folder, pattern, newline=None):
        folder.mkdir(parents=True, exist_ok=True)
        self.folder = folder
        self.pattern = pattern
        self.newline = newline
        self.handles = {}
        self.stack = ExitStack()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.stack.close()

    def __contains__(self, key):
        return key in self.handles

    def __getitem__(self, key):
        if key not in self.handles:
            path = self.folder / self.pattern.format(key)
            self.handles[key] = self.stack.enter_context(
                open(path, 'w', newline=self.newline, encoding='utf-8'))
        return self.handles[key]


def order_rows(order):
    """Return the CSV rows of an order: one per order line."""
    order_id, order_date, customer, lines = order
    rows = []
    for product_id, quantity in lines:
        _, name, category, price = PRODUCTS_BY_ID[product_id]
        rows.append([
            order_id,
            order_date.isoformat(), customer[0], customer[1], customer[2],
            product_id, name, category, quantity, price, quantity * price
        ])
    return rows


def write_orders(orders, folder):
    count = 0
    writers = {}
    with MonthlyFiles(folder, 'orders-{}.csv', newline='') as files:
        for order in orders:
            key = month_key(order[1])
            if key not in files:
                writers[key] = csv.writer(files[key])
                writers[key].writerow(ORDER_COLUMNS)
            for row in order_rows(order):
                writers[key].writerow(row)
                count += 1
    return count


def make_review(rng, review_id, order):
    order_id, order_date, customer, _ = order
    if order_id == FIXED_ORDER_ID:
        review_date = order_date
        fixed = FIXED_REVIEW
        rating, comment, tags = fixed['rating'], fixed['comment'], fixed['tags']
    else:
        review_date = order_date + timedelta(days=rng.randint(1, 10))
        rating = rng.choices([1, 2, 3, 4, 5], RATING_WEIGHTS)[0]
        comment = rng.choice(COMMENTS[rating])
        tags = rng.sample(TAGS, rng.choice([0, 0, 1, 2]))
    review = {
        'review_id': review_id,
        'order_id': order_id,
        'customer_id': customer[0],
        'rating': rating,
        'review_date': review_date.isoformat(),
        'comment': comment,
    }
    # Only some reviews have tags: the JSON is semi-structured.
    if tags:
        review['tags'] = tags
    return review


def choose_reviewed_orders(rng, orders, count):
    """Pick the orders that have a review. The fixed order always has one."""
    if count <= 0:
        return []
    others = [order for order in orders if order[0] != FIXED_ORDER_ID]
    chosen = rng.sample(others, min(count - 1, len(others)))
    chosen.extend(order for order in orders if order[0] == FIXED_ORDER_ID)
    return chosen


def write_reviews(rng, orders, count, folder):
    chosen = choose_reviewed_orders(rng, orders, count)
    with MonthlyFiles(folder, 'reviews-{}.json') as files:
        for review_id, order in enumerate(chosen, start=1):
            review = make_review(rng, review_id, order)
            key = review['review_date'][:7]
            files[key].write(json.dumps(review, ensure_ascii=False) + '\n')
    return len(chosen)


def make_png(width, height, color):
    """Return the bytes of a solid color PNG."""

    def chunk(kind, data):
        body = kind + data
        return (struct.pack('>I', len(data)) + body +
                struct.pack('>I',
                            zlib.crc32(body) & 0xffffffff))

    row = b'\x00' + bytes(color) * width
    header = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', header) +
            chunk(b'IDAT', zlib.compress(row * height)) + chunk(b'IEND', b''))


def write_photos(rng, folder):
    folder.mkdir(parents=True, exist_ok=True)
    for product_id, _, _, _ in PRODUCTS:
        color = tuple(rng.randint(60, 220) for _ in range(3))
        (folder / f'product-{product_id}.png').write_bytes(
            make_png(128, 128, color))
    return len(PRODUCTS)


def write_swamp(rng, customers, folder, count):
    """Orders of another branch, with other column names."""
    folder.mkdir(parents=True, exist_ok=True)
    with open(folder / 'orders_branch_b.csv', 'w', newline='',
              encoding='utf-8') as handle:
        writer = csv.writer(handle)
        writer.writerow(SWAMP_COLUMNS)
        for index in range(count):
            product = rng.choice(PRODUCTS)
            quantity = rng.randint(1, 3)
            writer.writerow([
                900000 + index,
                random_date(rng, START_DATE, END_DATE).strftime('%d/%m/%Y'),
                rng.choice(customers)[1], product[1], quantity,
                quantity * product[3]
            ])
    return count


def pick_defect(rng):
    """Return the defect of a line, or None when the line is clean."""
    roll = rng.random()
    threshold = 0.0
    for name, rate in DEFECT_RATES.items():
        threshold += rate
        if roll < threshold:
            return name
    return None


def apply_defect(rng, row, defect):
    """Return a copy of a CSV row of orders with a defect."""
    row = list(row)
    column = ORDER_COLUMNS.index
    if defect == 'invalid_date':
        row[column('order_date')] = rng.choice(['', '2026-10-32', '31/10/2026'])
    elif defect == 'invalid_quantity':
        quantity = rng.choice([0, -1, -2])
        row[column('quantity')] = quantity
        row[column('amount')] = quantity * int(row[column('unit_price')])
    elif defect == 'amount_mismatch':
        row[column('amount')] += rng.choice([-1000, 1000, 5000])
    elif defect == 'missing_customer':
        row[column('customer_id')] = ''
    return row


def write_october_batch(rng, customers, folder, count):
    """Write a batch of orders with defects and return its counts."""
    folder.mkdir(parents=True, exist_ok=True)
    counts = dict.fromkeys(DEFECT_RATES, 0)
    counts.update(orders=count, lines=0)
    with open(folder / 'orders-2026-10.csv', 'w', newline='',
              encoding='utf-8') as handle:
        writer = csv.writer(handle)
        writer.writerow(ORDER_COLUMNS)
        for index in range(count):
            order = (OCTOBER_FIRST_ORDER_ID + index,
                     random_date(rng, OCTOBER_START,
                                 OCTOBER_END), rng.choice(customers),
                     make_order_lines(rng, OCTOBER_FIRST_ORDER_ID + index))
            for row in order_rows(order):
                defect = pick_defect(rng)
                writer.writerow(
                    apply_defect(rng, row, defect) if defect else row)
                counts['lines'] += 1
                if defect:
                    counts[defect] += 1
                if defect == 'duplicate':
                    writer.writerow(row)
                    counts['lines'] += 1
    return counts


def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__.split('\n', maxsplit=1)[0])
    parser.add_argument('--orders', type=int, default=200000)
    parser.add_argument('--reviews', type=int, default=50000)
    parser.add_argument('--customers', type=int, default=5000)
    parser.add_argument('--swamp-rows', type=int, default=2000)
    parser.add_argument('--october-orders', type=int, default=50000)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main():
    args = parse_args()
    rng = random.Random(args.seed)
    customers = make_customers(rng, max(args.customers, len(FIXED_CUSTOMERS)))
    orders = make_orders(rng, args.orders, customers)
    lines = write_orders(orders, args.output / 'orders')
    reviews = write_reviews(rng, orders, args.reviews, args.output / 'reviews')
    photos = write_photos(rng, args.output / 'photos')
    swamp = write_swamp(rng, customers, args.output / 'swamp', args.swamp_rows)
    print(f'orders:  {args.orders} orders, {lines} lines')
    print(f'reviews: {reviews} reviews')
    print(f'photos:  {photos} images')
    print(f'swamp:   {swamp} rows')
    october = write_october_batch(rng, customers,
                                  args.output / 'orders_october',
                                  args.october_orders)
    print(f"october: {october['orders']} orders, {october['lines']} lines")
    for defect in DEFECT_RATES:
        print(f'         {defect}: {october[defect]}')
    print(f'Files written to {args.output}')


if __name__ == '__main__':
    main()
