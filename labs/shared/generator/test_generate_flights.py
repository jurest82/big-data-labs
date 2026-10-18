import csv
import random
from datetime import datetime, timedelta

import generate_flights as gf


def build(tmp_path, flights=3000):
    gf.write_reference_tables(tmp_path, flights)
    gf.write_flights(random.Random(1), flights, tmp_path / 'flights')


def read_rows(path):
    with open(path, newline='', encoding='utf-8') as handle:
        return list(csv.DictReader(handle))


def read_flights(tmp_path):
    rows = []
    for path in sorted((tmp_path / 'flights').glob('flights-*.csv')):
        rows.extend(read_rows(path))
    return rows


def test_one_file_per_month_and_the_requested_number_of_flights(tmp_path):
    build(tmp_path)
    files = sorted((tmp_path / 'flights').glob('flights-*.csv'))
    assert [f.name for f in files
            ] == [f'flights-2026-{m:02d}.csv' for m in range(1, 10)]
    assert len(read_flights(tmp_path)) == 3000


def test_flight_ids_are_unique(tmp_path):
    build(tmp_path)
    ids = [row['flight_id'] for row in read_flights(tmp_path)]
    assert len(set(ids)) == len(ids)


def test_flights_use_known_airports_airlines_and_aircraft(tmp_path):
    build(tmp_path)
    airports = {
        r['airport_code']
        for r in read_rows(tmp_path / 'airports' / 'airports.csv')
    }
    airlines = {
        r['airline_code']
        for r in read_rows(tmp_path / 'airlines' / 'airlines.csv')
    }
    tails = {
        r['tail_number']: r['airline_code']
        for r in read_rows(tmp_path / 'aircraft' / 'aircraft.csv')
    }
    for row in read_flights(tmp_path):
        assert row['origin'] in airports
        assert row['destination'] in airports
        assert row['origin'] != row['destination']
        assert row['airline_code'] in airlines
        assert tails[row['tail_number']] == row['airline_code']


def test_flight_date_is_the_scheduled_day_in_its_month_file(tmp_path):
    build(tmp_path)
    for path in (tmp_path / 'flights').glob('flights-*.csv'):
        month = path.stem[-7:]
        for row in read_rows(path):
            assert row['flight_date'].startswith(month)
            assert row['scheduled_departure'].startswith(row['flight_date'])


def test_cancelled_flights_have_no_actual_departure(tmp_path):
    build(tmp_path)
    rows = read_flights(tmp_path)
    cancelled = [r for r in rows if r['cancelled'] == '1']
    assert cancelled
    for row in rows:
        assert (row['actual_departure'] == '') == (row['cancelled'] == '1')


def test_delays_are_within_the_expected_range(tmp_path):
    build(tmp_path)
    for row in read_flights(tmp_path):
        if row['cancelled'] == '1':
            continue
        scheduled = datetime.fromisoformat(row['scheduled_departure'])
        actual = datetime.fromisoformat(row['actual_departure'])
        assert timedelta(minutes=-8) <= actual - scheduled
        assert actual - scheduled <= timedelta(minutes=300)


def test_distance_between_bogota_and_medellin():
    bogota = next(a for a in gf.AIRPORTS if a[0] == 'BOG')
    medellin = next(a for a in gf.AIRPORTS if a[0] == 'MDE')
    assert 200 <= gf.distance_km(bogota, medellin) <= 230


def test_fleet_grows_with_the_number_of_flights():
    small = gf.make_aircraft(random.Random(1), 3000)
    large = gf.make_aircraft(random.Random(1), 10000000)
    assert sum(len(fleet) for fleet in small.values()) < sum(
        len(fleet) for fleet in large.values())


def test_same_seed_same_files(tmp_path):
    build(tmp_path / 'a')
    build(tmp_path / 'b')
    for path in (tmp_path / 'a').rglob('*.csv'):
        other = tmp_path / 'b' / path.relative_to(tmp_path / 'a')
        assert path.read_bytes() == other.read_bytes()
