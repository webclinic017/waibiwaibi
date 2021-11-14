
import os
import sys
import time
import numpy as np
import pandas as pd
import sqlite3
from math import log10 as lg

from mak_sqlite import create_table, insert, insert_not_repeat, add_column, select, table_info, list_to_str, list_to_str_no_quote, table_list


date_today = time.strftime("%Y-%m-%d", time.localtime())


def get_code_list(cursor):
    code_list = select(cursor, 'code', 'stock_list_a', '')
    code_list = [x[0] for x in code_list]
    return code_list


def get_day(cursor, code, date_start, date_end='', period=0, frozen_days=0):
    table_exist = table_list(cursor)
    if f'day_{code}' not in table_exist:
        return None

    res = get_day_raw(cursor, code, date_start, date_end, period, frozen_days)
    if res is None:
        return None
    else:
        res.update(day_data_process(res))

        return res


def get_day_raw(cursor, code: str, date_start: str, date_end='', period=0, frozen_days=0):
    res = {'code': code, 'frozen_days': frozen_days}

    column_info = table_info(cursor, f'day_{code}')
    column_names = []
    column_indexs = []
    for column in column_info:
        column_names.append(column[1])
        column_indexs.append(column[0])

    all_data = select(cursor, '*', f'day_{code}', 'order by date(date)')
    # print(all_data[:5])

    index_start = -1
    index_end = -1
    for i in range(0, len(all_data)):
        if all_data[i][column_indexs[column_names.index('date')]] >= date_start:
            index_start = i
            break
    if date_end:
        for i in range(0, len(all_data)):
            if all_data[i][column_indexs[column_names.index('date')]] >= date_end:
                index_end = i-1
                break
    elif period > 0:
        index_end = index_start + period
    if index_start == -1 or index_end == -1 or index_start-frozen_days < 0 or index_end >= len(all_data):
        # print(f'database dont have data of {code} in: {date_start} - {date_end}, period: {period}, day_before: {frozen_days}')
        # print(index_start == -1, index_end == -1, index_start-frozen_days < 0, index_end >= len(all_data))
        # print(len(all_data), index_end)
        return None

    index_start -= frozen_days

    for i in range(0, len(column_names)):
        if column_names[i] == 'rate':
            res[column_names[i]] = [line[column_indexs[i]] * 0.01 for line in all_data[index_start:index_end]]
        elif column_names[i] != 'id':
            # print(i, column_names[i], index_start, index_end, column_indexs[i])
            res[column_names[i]] = [line[column_indexs[i]] for line in all_data[index_start:index_end]]

    return res


def day_data_process(data: dict):
    res = {}
    total_rate_lg = 0
    res['rate_lg'] = [0]
    res['price_std_lg'] = [0]
    res['price_adjust'] = [1]
    for day in range(1, len(data['date'])):
        rate_lg = lg(1 + data['rate'][day])
        total_rate_lg += rate_lg
        res['rate_lg'].append(rate_lg)
        res['price_adjust'].append(10 ** total_rate_lg)
        res['price_std_lg'].append(total_rate_lg)

    std = data['price'][data['frozen_days']] / res['price_adjust'][data['frozen_days']]
    res['price_adjust'] = [x * std for x in res['price_adjust']]
    std = res['price_std_lg'][data['frozen_days']]
    res['price_std_lg'] = [x - std for x in res['price_std_lg']]

    return res


def run():
    dir_sql = 'stock_data_ak.db'
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

    get_day_raw(cursor, '000001', '2015-04-01', '2015-06-01')

    # print(table_list(cursor))

    sql.close()


if __name__ == '__main__':
    run()





