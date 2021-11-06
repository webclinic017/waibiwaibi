
import os
import sys
import time
import numpy as np
import pandas as pd
import sqlite3
from math import log10 as lg

from mak_sqlite import create_table, insert, insert_not_repeat, add_column, select, table_info, list_to_str, list_to_str_no_quote


date_today = time.strftime("%Y-%m-%d", time.localtime())


def get_day(cursor, code, date_start, date_end='', period=0, day_before=0, extra_item=['exchange_rate'], item_process=True):
    res = {}

    if date_end == '' and period == 0:
        print('input wrong')
        return None

    cursor.execute(f'select count(*) from day_{code} \
                     where date <= "{date_start}"')
    index_start = cursor.fetchall()[0][0]
    if index_start < day_before:
        print('too early')
        return None
    start_point = index_start - day_before
    offset = day_before

    if date_end != '':
        cursor.execute(f'select count(*) from day_{code} \
                         where date <= "{date_end}"')
        index_end = cursor.fetchall()[0][0]

        if period > index_end - index_start or period == 0:
            offset += index_end - index_start
        else:
            offset += period
    elif period > 0:
        offset += period

    cursor.execute(f'pragma table_info(day_{code})')
    # table_info format: [column num, column name, ...,]
    columns = cursor.fetchall()
    items = ['date', 'price', 'rate']
    items.extend(extra_item)
    item_info = []
    for column in columns:
        if column[1] in items:
            item_info.append(column)

    for info in item_info:
        res[info[1]] = []

    cursor.execute(f'select * from day_{code} \
                     limit {start_point}, {offset}')
    for row in cursor.fetchall():
        for info in item_info:
            res[info[1]].append(row[info[0]])

    total_rate_lg = 0
    res['rate_lg'] = [0.0]
    res['price_std_lg'] = [0]
    res['price_adjust'] = [res['price'][0]]
    for day in range(1, len(res['date'])):
        rate = res['rate'][day]
        rate_lg = lg(1 + 0.01 * rate)
        total_rate_lg += rate_lg
        res['rate_lg'].append(rate_lg)
        res['price_std_lg'].append(total_rate_lg)
        res['price_adjust'].append(res['price'][0] * (10 ** total_rate_lg))

    res['price_adjust'] = [x*res['price'][day_before] for x in res['price_adjust']]
    std = res['price_std_lg'][day_before]
    res['price_std_lg'] = [x-std for x in res['price_std_lg']]

    return res


def get_day_raw(cursor, code, date_start, date_end='', period=0, day_before=0):
    res = {}

    column_info = table_info(cursor, f'day_{code}')
    column_names = []
    column_indexs = []
    for column in column_info:
        column_names.append(column[1])
        column_indexs.append(column[0])

    cursor.execute(f'select * from day_{code} \
                     order by date(date)')
    all_data = cursor.fetchall()

    for i in range(0, len(column_names)):
        res[f'{column_names[i]}'] = []

    # if date_end == '' and period == 0:
    #     print('both end date and period is not defined')
    #     return None
    #
    # cursor.execute(f'select count(*) from day_{code} \
    #                  where date <= "{date_start}"')
    # index_start = cursor.fetchall()[0][0]
    # if index_start < day_before:
    #     print('too early')
    #     return None
    # start_point = index_start - day_before
    # offset = day_before
    #
    # if date_end != '':
    #     cursor.execute(f'select count(*) from day_{code} \
    #                          where date <= "{date_end}"')
    #     index_end = cursor.fetchall()[0][0]
    #
    #     if period > index_end - index_start or period == 0:
    #         offset += index_end - index_start
    #     else:
    #         offset += period
    # elif period > 0:
    #     offset += period
    # cursor.execute(f'pragma table_info(day_{code})')
    # table_info = cursor.fetchall()
    # # info: [column num, column name,
    #
    # for info in table_info:
    #     res[info[1]] = []
    #
    # cursor.execute(f'select * from day_{code} \
    #                  limit {start_point}, {offset}')
    # for row in cursor.fetchall():
    #     for info in table_info:
    #         res[info[1]].append(row[info[0]])
    #
    # return res


def run():
    dir_sql = 'stock_data_ak_test.db'
    sql = sqlite3.connect(dir_sql)
    cursor = sql.cursor()

    # print(get_day(cursor, '000001', '2020-01-01', '2020-01-05', period=10, day_before=5))
    # print(len(get_day(cursor, '000001', '2020-01-01', period=10, day_before=5)['date']))
    #
    # cursor.execute(f'select count(*) from day_000001')
    # amount = cursor.fetchall()[0][0]
    #
    # cursor.execute(f'select * from day_000001 \
    #                  limit {amount-2}, 5')
    # for row in cursor.fetchall():
    #     print(row)

    get_day_raw(cursor, '603808', '2015-04-01', '2015-06-01')

    sql.close()


if __name__ == '__main__':
    run()





