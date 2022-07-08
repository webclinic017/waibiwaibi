# @ last edit time 2021/11/1 0:23


import os
import sys
import time
import numpy as np
import pandas as pd
import sqlite3
from math import log10 as lg

import requests.exceptions
from tqdm import tqdm

import akshare as ak

from mak_sqlite import create_table, insert, insert_not_repeat, add_column, select, list_to_str, list_to_str_no_quote


table_list_a = 'stock_list_a'

# database format:
# id,   date,         price,   exchange_rate,   ...
# 0,    2017-03-01,   9.49,    0.21,            ...
# 1,    2017-03-02,   9.43,    0.24,            ...
# 2,    2017-03-03,   9.40,    0.20,            ...


def load_stock_a(cursor):
    create_table(cursor, table_list_a)
    add_column(cursor, table_list_a, 'code', 'char(6)')
    add_column(cursor, table_list_a, 'name', 'char(20)')

    stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
#     序号      代码    名称     最新价    涨跌幅  ...      昨收    量比    换手率  市盈率-动态    市净率
# 0     1    001288   N运机    20.00    37.46  ...     14.55   NaN    48.53     48.51     1.84
# 1     2    688030  山石网科   25.97    20.01  ...     21.64   8.02    6.52   -168.94     3.33
# 2     3    301018  申菱环境   34.80    20.00  ...     29.00   1.09   46.01     74.82     6.05

    list_code = np.array(stock_zh_a_spot_em_df.iloc[0:, 1]).tolist()
    list_name = np.array(stock_zh_a_spot_em_df.iloc[0:, 2]).tolist()

    for i in range(0, len(list_code)):
        insert(cursor, table_list_a, ['code', 'name'], [list_code[i], list_name[i]])


def get_list_a(cursor):
    list_code = select(cursor, 'code', table_list_a, '')
    list_code = [x[0] for x in list_code]
    # print(list_code)
    return list_code


def load_basic(sql, cursor, start, end):
    list_code = get_list_a(cursor)
    for progress in tqdm(range(0, len(list_code))):
        code = list_code[progress]

        state_flag = 0
        try_max = 10
        while try_max:
            try:
                stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol=code, period="daily", start_date=start, end_date=end, adjust="")
            except ValueError:
                print("value error: ", code)
                state_flag = 1
                break
            except (TimeoutError, requests.exceptions.ConnectionError):
                time.sleep(30)
                print("reconnect:", 10-try_max)
                try_max -= 1
                continue
            else:
                break
        if state_flag:
            continue

#        日期     开盘     收盘     最高  ...    振幅   涨跌幅   涨跌额   换手率
# 0 2017-03-01   9.49    9.49    9.55  ...   0.84    0.11   0.01    0.21
# 1 2017-03-02   9.51    9.43    9.54  ...   1.26   -0.63  -0.06    0.24
# 2 2017-03-03   9.41    9.40    9.43  ...   0.74   -0.32  -0.03    0.20

        table_code_day = f'day_{code}'
        create_table(cursor, table_code_day)
        add_column(cursor, table_code_day, 'date', 'date')
        add_column(cursor, table_code_day, 'price', 'double')
        add_column(cursor, table_code_day, 'rate', 'double')
        add_column(cursor, table_code_day, 'exchange_rate', 'double')

        list_date = np.array(stock_zh_a_hist_df.iloc[0:, 0]).tolist()
        list_price = np.array(stock_zh_a_hist_df.iloc[0:, 2]).tolist()
        list_rate = np.array(stock_zh_a_hist_df.iloc[0:, 8]).tolist()
        list_exchange_rate = np.array(stock_zh_a_hist_df.iloc[0:, 10]).tolist()

        for i in range(0, len(list_date)):
            if list_price[i]:
                insert(cursor, table_code_day, ['date', 'price', 'rate', 'exchange_rate'],
                       [list_date[i], list_price[i], list_rate[i], list_exchange_rate[i]])

        sql.commit()


def load_index_list(cursor, index_code):
    index_stock_cons_df = ak.index_stock_cons(index=index_code)
    # print(index_stock_cons_df)
    del index_stock_cons_df['品种名称']
    index_list = np.array(index_stock_cons_df.iloc[:, :]).tolist()
    # print(index_list)

    table_index_list = f'index_list_{index_code}'
    create_table(cursor, table_index_list)
    add_column(cursor, table_index_list, 'code', 'char(6)')
    add_column(cursor, table_index_list, 'start', 'date')

    for i in range(0, len(index_list)):
        stock = index_list[i]
        insert(cursor, table_index_list, ['code', 'start'], stock)


def load_index_list_history(cursor, index_code):
    stock_index_hist_df = ak.index_stock_hist(index=index_code)
    index_list = np.array(stock_index_hist_df.iloc[:, :]).tolist()
    # print(index_list)

    table_index_list = f'index_list_{index_code}_history'
    create_table(cursor, table_index_list)
    add_column(cursor, table_index_list, 'code', 'char(6)')
    add_column(cursor, table_index_list, 'start', 'date')
    add_column(cursor, table_index_list, 'end', 'date')

    for i in range(0, len(index_list)):
        stock = index_list[i]
        insert(cursor, table_index_list, ['code', 'start', 'end'], stock)


def run():
    dir_sql = 'stock_data_ak.db'
    sql = sqlite3.connect(dir_sql)
    cursor = sql.cursor()

    load_stock_a(cursor)
    load_basic(sql, cursor, '20150401', '20150501')

    # stock_index_hist_df = hs300_list_history()

    load_index_list(cursor, '000300')
    load_index_list_history(cursor, 'sh000300')

    # print(get_index_list('sh000300'))
    # print(hs300_list())

    sql.commit()
    sql.close()


if __name__ == '__main__':
    run()


