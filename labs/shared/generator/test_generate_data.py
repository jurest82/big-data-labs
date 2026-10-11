import csv
import json
import random
import struct
import zlib
from datetime import date

import generate_data as gd


def build(tmp_path, orders=600, reviews=100):
    rng = random.Random(1)
    customers = gd.make_customers(rng, 50)
    data = gd.make_orders(rng, orders, customers)
    gd.write_orders(data, tmp_path / 'orders')
    gd.write_reviews(rng, data, reviews, tmp_path / 'reviews')
    gd.write_photos(rng, tmp_path / 'photos')
    gd.write_swamp(rng, customers, tmp_path / 'swamp', 20)
    return data


def read_orders(tmp_path):
    rows = []
    for path in sorted((tmp_path / 'orders').glob('orders-*.csv')):
        with open(path, newline='', encoding='utf-8') as handle:
            rows.extend(csv.DictReader(handle))
    return rows


def test_fixed_order_matches_lab_1(tmp_path):
    build(tmp_path)
    lines = [r for r in read_orders(tmp_path) if r['order_id'] == '10482']
    assert [(r['product_name'], r['quantity'], r['amount'])
            for r in lines] == [('T-shirt', '2', '60000'),
                                ('Cap', '1', '35000')]
    assert {r['customer_name']
            for r in lines} == {'Ana Pérez'}
    assert {r['order_date']
            for r in lines} == {'2026-09-14'}


def test_amount_is_quantity_times_unit_price(tmp_path):
    build(tmp_path)
    for row in read_orders(tmp_path):
        assert int(
            row['amount']) == int(row['quantity']) * int(row['unit_price'])


def test_same_seed_same_files(tmp_path):
    build(tmp_path / 'a')
    build(tmp_path / 'b')
    for name in ['orders/orders-2026-09.csv', 'reviews/reviews-2026-09.json']:
        assert (tmp_path / 'a' / name).read_bytes() == (tmp_path / 'b' /
                                                        name).read_bytes()


def test_reviews_are_json_lines_with_optional_tags(tmp_path):
    build(tmp_path)
    reviews = []
    for path in (tmp_path / 'reviews').glob('reviews-*.json'):
        for line in path.read_text(encoding='utf-8').splitlines():
            reviews.append(json.loads(line))
    assert len(reviews) == 100
    assert any('tags' in r for r in reviews)
    assert any('tags' not in r for r in reviews)
    fixed = [r for r in reviews if r['order_id'] == 10482]
    assert len(fixed) == 1
    assert fixed[0]['rating'] == 4


def test_photos_are_valid_png_files(tmp_path):
    build(tmp_path)
    photos = list((tmp_path / 'photos').glob('product-*.png'))
    assert len(photos) == len(gd.PRODUCTS)
    for photo in photos:
        data = photo.read_bytes()
        assert data.startswith(b'\x89PNG\r\n\x1a\n')
        length = struct.unpack('>I', data[8:12])[0]
        header = data[16:16 + length]
        assert struct.unpack('>II', header[:8]) == (128, 128)
        idat = data.index(b'IDAT')
        size = struct.unpack('>I', data[idat - 4:idat])[0]
        assert len(zlib.decompress(data[idat + 4:idat + 4 +
                                        size])) == (128 * (1 + 128 * 3))


def test_swamp_file_has_other_columns(tmp_path):
    build(tmp_path)
    with open(tmp_path / 'swamp' / 'orders_branch_b.csv',
              newline='',
              encoding='utf-8') as handle:
        header = next(csv.reader(handle))
    assert header == gd.SWAMP_COLUMNS
    assert not set(header) & set(gd.ORDER_COLUMNS)


def classify(rows):
    """Apply the rules of the silver layer to the lines of the October batch."""
    seen = set()
    counts = {}
    for row in rows:
        reason = 'valid'
        try:
            date.fromisoformat(row['order_date'])
        except ValueError:
            reason = 'invalid_date'
        if reason == 'valid' and int(row['quantity']) <= 0:
            reason = 'invalid_quantity'
        if reason == 'valid' and int(
                row['amount']) != int(row['quantity']) * int(row['unit_price']):
            reason = 'amount_mismatch'
        if reason == 'valid' and row['customer_id'] == '':
            reason = 'missing_customer'
        if reason == 'valid':
            key = (row['order_id'], row['product_id'])
            if key in seen:
                reason = 'duplicate'
            seen.add(key)
        counts[reason] = counts.get(reason, 0) + 1
    return counts


def october_batch(tmp_path, count=3000):
    rng = random.Random(1)
    customers = gd.make_customers(rng, 50)
    counts = gd.write_october_batch(rng, customers, tmp_path / 'october', count)
    path = tmp_path / 'october' / 'orders-2026-10.csv'
    with open(path, newline='', encoding='utf-8') as handle:
        return counts, list(csv.DictReader(handle))


def test_october_batch_defects_match_the_silver_rules(tmp_path):
    counts, rows = october_batch(tmp_path)
    found = classify(rows)
    assert len(rows) == counts['lines']
    for defect in gd.DEFECT_RATES:
        assert found[defect] == counts[defect] > 0
    assert sum(found.values()) == counts['lines']
    assert found['valid'] > 0.8 * counts['lines']


def test_october_batch_has_its_own_order_ids(tmp_path):
    _, rows = october_batch(tmp_path)
    ids = {int(row['order_id'])
           for row in rows}
    assert min(ids) == gd.OCTOBER_FIRST_ORDER_ID
    assert max(ids) == gd.OCTOBER_FIRST_ORDER_ID + 2999


def test_october_batch_is_deterministic(tmp_path):
    october_batch(tmp_path / 'a')
    october_batch(tmp_path / 'b')
    name = 'october/orders-2026-10.csv'
    assert (tmp_path / 'a' / name).read_bytes() == (tmp_path / 'b' /
                                                    name).read_bytes()
