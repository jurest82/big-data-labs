"""Print the windows that the Flink application wrote to the DynamoDB table."""
import argparse
from collections import Counter

import boto3


def read_windows(table_name):
    table = boto3.resource('dynamodb').Table(table_name)
    response = table.scan()
    items = response['Items']
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items += response['Items']
    return sorted(items,
                  key=lambda item: (item['window_start'], item['restaurant']))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--table', default='big-data-labs-order-windows')
    args = parser.parse_args()
    windows = read_windows(args.table)
    totals = Counter()
    print('window_start      restaurant     orders  avg_amount')
    for item in windows:
        totals[item['window_start']] += int(item['orders'])
        print(f'{item["window_start"]}  {item["restaurant"]:<13}  '
              f'{int(item["orders"]):>6}  {item["avg_amount"]:>10}')
    print('\nOrders in each window:')
    for window_start, orders in sorted(totals.items()):
        print(f'  {window_start}  {orders}')


if __name__ == '__main__':
    main()
