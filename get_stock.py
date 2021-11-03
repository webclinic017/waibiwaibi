
import os
import sys
import time
import numpy as np
import pandas as pd
import sqlite3


dir_sql = 'stock_data.db'
date_today = time.strftime("%Y-%m-%d", time.localtime())


def get_day(cursor, code, date_start, date_end='', period=0, day_before=0):
    if date_end == '' and period == 0:
        print('input wrong')
        return None


    cursor.execute(f'select count(*) from day_{code} \
                     where date <= "{date_start}"')
    index_start = cursor.fetchall()[0][0]
    if index_start < day_before:
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
    table_info = cursor.fetchall()
    # info: [column num, column name,
    res = {}
    for info in table_info:
        res[info[1]] = []

    cursor.execute(f'select * from day_{code} \
                     limit {start_point}, {offset}')

    for row in cursor.fetchall():
        for info in table_info:
            res[info[1]].append(row[info[0]])

    return res


# def data_slice(data, limit):
#     pass


if __name__ == '__main__':
    sql = sqlite3.connect(dir_sql)
    cursor = sql.cursor()

    print(get_day(cursor, '000001', '2020-01-01', '2020-01-05', period=10, day_before=5))
    print(len(get_day(cursor, '000001', '2020-01-01', period=10, day_before=5)['date']))

    cursor.execute(f'select count(*) from day_000001')
    amount = cursor.fetchall()[0][0]

    cursor.execute(f'select * from day_000001 \
                     limit {amount-2}, 5')
    for row in cursor.fetchall():
        print(row)

    sql.close()





