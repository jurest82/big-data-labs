"""Generate the sample data of the airline used by the Spark labs.

It writes four folders, one CSV file or more each:

- flights/: one CSV file per month, with one row per flight.
- airports/airports.csv: the airports of the routes.
- airlines/airlines.csv: the airlines.
- aircraft/aircraft.csv: the aircraft of each airline.

The data is deterministic: the same seed produces the same files. The
airlines and the aircraft are made up. The airports are real, and their
coordinates are approximate.
"""
import argparse
import math
import random
from collections import namedtuple
from datetime import date, timedelta
from pathlib import Path

DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / 'output'
FIRST_FLIGHT_ID = 1000000
YEAR = 2026
FIRST_MONTH = 1
LAST_MONTH = 9
CANCELLED_RATE = 0.015
FLIGHTS_PER_AIRCRAFT_PER_DAY = 6
DAYS = 273

# airport_code, airport_name, city, country, latitude, longitude, weight
AIRPORTS = [
    ('BOG', 'El Dorado International', 'Bogota', 'Colombia', 4.70, -74.15, 30),
    ('MDE', 'Jose Maria Cordova International', 'Medellin', 'Colombia', 6.16,
     -75.42, 18),
    ('CLO', 'Alfonso Bonilla Aragon International', 'Cali', 'Colombia', 3.54,
     -76.38, 12),
    ('CTG', 'Rafael Nunez International', 'Cartagena', 'Colombia', 10.44,
     -75.51, 12),
    ('BAQ', 'Ernesto Cortissoz International', 'Barranquilla', 'Colombia',
     10.89, -74.78, 7),
    ('SMR', 'Simon Bolivar International', 'Santa Marta', 'Colombia', 11.12,
     -74.23, 4),
    ('BGA', 'Palonegro International', 'Bucaramanga', 'Colombia', 7.13, -73.18,
     4),
    ('PEI', 'Matecana International', 'Pereira', 'Colombia', 4.81, -75.74, 4),
    ('CUC', 'Camilo Daza International', 'Cucuta', 'Colombia', 7.93, -72.51, 3),
    ('ADZ', 'Gustavo Rojas Pinilla International', 'San Andres', 'Colombia',
     12.58, -81.71, 3),
    ('PTY', 'Tocumen International', 'Panama City', 'Panama', 9.07, -79.38, 4),
    ('MIA', 'Miami International', 'Miami', 'United States', 25.80, -80.29, 4),
    ('MCO', 'Orlando International', 'Orlando', 'United States', 28.43, -81.31,
     2),
    ('JFK', 'John F. Kennedy International', 'New York', 'United States', 40.64,
     -73.78, 3),
    ('MEX', 'Benito Juarez International', 'Mexico City', 'Mexico', 19.44,
     -99.07, 3),
    ('LIM', 'Jorge Chavez International', 'Lima', 'Peru', -12.02, -77.11, 3),
    ('SCL', 'Arturo Merino Benitez International', 'Santiago', 'Chile', -33.39,
     -70.79, 2),
    ('GRU', 'Sao Paulo Guarulhos International', 'Sao Paulo', 'Brazil', -23.44,
     -46.47, 2),
    ('EZE', 'Ministro Pistarini International', 'Buenos Aires', 'Argentina',
     -34.82, -58.54, 2),
    ('MAD', 'Adolfo Suarez Madrid-Barajas', 'Madrid', 'Spain', 40.50, -3.57, 3),
]

# airline_code, airline_name, share of the flights, punctuality: the more
# positive, the fewer delays
AIRLINES = [
    ('AND', 'Andes Air', 22, 0.04),
    ('CAR', 'Caribe Airways', 18, -0.06),
    ('PAC', 'Pacific Wings', 14, 0.10),
    ('SUR', 'Sur Express', 12, -0.12),
    ('NOR', 'Norte Jet', 10, 0.00),
    ('ORI', 'Oriente Air', 9, -0.02),
    ('CEN', 'Centro Lineas Aereas', 8, 0.06),
    ('LLA', 'Llanos Connect', 7, -0.08),
]

# model, seats
AIRCRAFT_MODELS = [('A320', 180), ('A321', 220), ('B737', 189), ('E190', 100),
                   ('ATR72', 70), ('A330', 250)]

# Share of the flights that leave in each hour of the day
HOUR_WEIGHTS = [
    1, 1, 1, 1, 2, 4, 7, 8, 8, 7, 6, 6, 6, 6, 6, 6, 7, 8, 8, 7, 5, 3, 2, 1
]
MONTH_FACTOR = {
    1: 1.10,
    2: 0.95,
    3: 1.0,
    4: 1.0,
    5: 0.97,
    6: 1.05,
    7: 1.15,
    8: 1.08,
    9: 0.97
}

AIRPORT_COLUMNS = [
    'airport_code', 'airport_name', 'city', 'country', 'latitude', 'longitude'
]
AIRLINE_COLUMNS = ['airline_code', 'airline_name']
AIRCRAFT_COLUMNS = ['tail_number', 'airline_code', 'model', 'seats']
FLIGHT_COLUMNS = [
    'flight_id', 'flight_date', 'airline_code', 'flight_number', 'tail_number',
    'origin', 'destination', 'scheduled_departure', 'actual_departure',
    'distance_km', 'cancelled'
]


def distance_km(first, second):
    """Great-circle distance in km between two airport rows (haversine)."""
    lat1, lon1 = math.radians(first[4]), math.radians(first[5])
    lat2, lon2 = math.radians(second[4]), math.radians(second[5])
    a = (math.sin(
        (lat2 - lat1) / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(
            (lon2 - lon1) / 2)**2)
    return round(2 * 6371 * math.asin(math.sqrt(a)))


def make_routes():
    """Every ordered pair of airports, with a weight and its distance."""
    routes = []
    for origin in AIRPORTS:
        for destination in AIRPORTS:
            if origin[0] == destination[0]:
                continue
            both_colombia = (origin[3] == 'Colombia' and
                             destination[3] == 'Colombia')
            weight = origin[6] * destination[6] * (4 if both_colombia else 1)
            routes.append((origin[0], destination[0], weight,
                           distance_km(origin, destination)))
    return routes


def make_aircraft(rng, total):
    """The aircraft of each airline, with made-up tail numbers.

    The fleet of an airline is sized so that each aircraft makes about
    FLIGHTS_PER_AIRCRAFT_PER_DAY flights a day.
    """
    fleets = {}
    shares = sum(airline[2] for airline in AIRLINES)
    for code, _, share, _ in AIRLINES:
        size = max(
            5,
            round(total * share / shares / DAYS / FLIGHTS_PER_AIRCRAFT_PER_DAY))
        fleet = []
        for number in range(size):
            model, seats = rng.choice(AIRCRAFT_MODELS)
            fleet.append((f'{code}-{number + 1:03d}', code, model, seats))
        fleets[code] = fleet
    return fleets


def month_sizes(total):
    """Number of flights of each month, in proportion to its days."""
    months = range(FIRST_MONTH, LAST_MONTH + 1)
    weights = []
    for month in months:
        days = (date(YEAR + (month == 12), month % 12 + 1, 1) -
                date(YEAR, month, 1)).days
        weights.append(days * MONTH_FACTOR[month])
    sizes = [int(total * w / sum(weights)) for w in weights]
    sizes[-1] += total - sum(sizes)
    return dict(zip(months, sizes))


def cumulative(weights):
    result, running = [], 0
    for weight in weights:
        running += weight
        result.append(running)
    return result


def date_strings():
    """'YYYY-MM-DD' for each day from the day before the first one."""
    first = date(YEAR, FIRST_MONTH, 1) - timedelta(days=1)
    last = date(YEAR, LAST_MONTH, 30) + timedelta(days=2)
    days = (last - first).days + 1
    return first, [(first + timedelta(days=n)).isoformat() for n in range(days)]


FlightTables = namedtuple('FlightTables', [
    'routes', 'route_cum', 'airline_cum', 'minute_cum', 'tails', 'first_day',
    'day_text', 'clock'
])


def make_tables(total):
    routes = make_routes()
    fleets = make_aircraft(random.Random(YEAR), total)
    first_day, day_text = date_strings()
    return FlightTables(
        routes=routes,
        route_cum=cumulative([route[2] for route in routes]),
        airline_cum=cumulative([airline[2] for airline in AIRLINES]),
        minute_cum=cumulative(
            [HOUR_WEIGHTS[minute // 60] for minute in range(1440)]),
        tails=[[row[0] for row in fleets[airline[0]]] for airline in AIRLINES],
        first_day=first_day,
        day_text=day_text,
        clock=[f'{m // 60:02d}:{m % 60:02d}:00' for m in range(1440)])


def delay_minutes(rng, airline_id):
    """Minutes between the scheduled and the actual departure."""
    draw = rng.random() - AIRLINES[airline_id][3]
    if draw < 0.62:
        return rng.randrange(-8, 6)
    if draw < 0.85:
        return rng.randrange(6, 31)
    if draw < 0.96:
        return rng.randrange(31, 91)
    return rng.randrange(91, 301)


def flight_line(rng, tables, flight_id, pick):
    """One CSV line. pick is (day, route_id, airline_id, minute)."""
    day, route_id, airline_id, minute = pick
    route = tables.routes[route_id]
    airline = AIRLINES[airline_id][0]
    tail = rng.choice(tables.tails[airline_id])
    scheduled = f'{tables.day_text[day]} {tables.clock[minute]}'
    actual, cancelled = '', 1
    if rng.random() >= CANCELLED_RATE:
        shifted = minute + delay_minutes(rng, airline_id)
        actual = (f'{tables.day_text[day + shifted // 1440]} '
                  f'{tables.clock[shifted % 1440]}')
        cancelled = 0
    return (f'{flight_id},{tables.day_text[day]},{airline},'
            f'{airline}{rng.randrange(100, 1000)},{tail},{route[0]},'
            f'{route[1]},{scheduled},{actual},{route[3]},{cancelled}')


def write_month(handle, rng, tables, period):
    """Write the flights of one month. period is (month, size, first_id)."""
    month, size, first_id = period
    month_start = (date(YEAR, month, 1) - tables.first_day).days
    days = (date(YEAR + (month == 12), month % 12 + 1, 1) -
            date(YEAR, month, 1)).days
    route_ids = rng.choices(range(len(tables.routes)),
                            cum_weights=tables.route_cum,
                            k=size)
    airline_ids = rng.choices(range(len(AIRLINES)),
                              cum_weights=tables.airline_cum,
                              k=size)
    minutes = rng.choices(range(1440), cum_weights=tables.minute_cum, k=size)
    lines = []
    for n in range(size):
        pick = (month_start + rng.randrange(days), route_ids[n], airline_ids[n],
                minutes[n])
        lines.append(flight_line(rng, tables, first_id + n, pick))
        if len(lines) == 50000:
            handle.write('\n'.join(lines) + '\n')
            lines = []
    if lines:
        handle.write('\n'.join(lines) + '\n')


def write_flights(rng, total, folder):
    """Write one CSV file per month. Returns the number of rows written."""
    folder.mkdir(parents=True, exist_ok=True)
    tables = make_tables(total)
    flight_id = FIRST_FLIGHT_ID
    for month, size in month_sizes(total).items():
        path = folder / f'flights-{YEAR}-{month:02d}.csv'
        with open(path, 'w', encoding='utf-8', newline='') as handle:
            handle.write(','.join(FLIGHT_COLUMNS) + '\n')
            write_month(handle, rng, tables, (month, size, flight_id))
        flight_id += size
    return total


def write_table(path, columns, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='') as handle:
        handle.write(','.join(columns) + '\n')
        for row in rows:
            handle.write(','.join(str(value) for value in row) + '\n')


def write_reference_tables(output, total):
    write_table(output / 'airports' / 'airports.csv', AIRPORT_COLUMNS,
                [airport[:6] for airport in AIRPORTS])
    write_table(output / 'airlines' / 'airlines.csv', AIRLINE_COLUMNS,
                [airline[:2] for airline in AIRLINES])
    fleets = make_aircraft(random.Random(YEAR), total)
    write_table(output / 'aircraft' / 'aircraft.csv', AIRCRAFT_COLUMNS,
                [row for fleet in fleets.values() for row in fleet])


def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__.split('\n', maxsplit=1)[0])
    parser.add_argument('--flights', type=int, default=10000000)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main():
    args = parse_args()
    rng = random.Random(args.seed)
    write_reference_tables(args.output, args.flights)
    count = write_flights(rng, args.flights, args.output / 'flights')
    print(f'Wrote {count} flights to {args.output}')


if __name__ == '__main__':
    main()
