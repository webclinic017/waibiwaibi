# @ last edit time 2021/10/31 18:24

import os
import sys
import time
import numpy as np
import pandas as pd
import sqlite3
from math import log10 as lg
from tqdm import tqdm
import csv

from mak_sqlite import create_table, insert, add_column, list_to_str, list_to_str_no_quote

type_name_match = [['收盘价', 'price'], ['涨跌幅', 'rate']]


def type_name_switch(chinese):
    for pair in type_name_match:
        if pair[0] == chinese:
            return pair[1]
    return None


def load_choice_basic(cursor, dir_csv):
    name_basic = 'basic'
    create_table(cursor, name_basic)

    file = open(dir_csv)
    reader = csv.reader(file)
    date_list = []
    date_len = 0
    for i, item in enumerate(reader):
        if i % 10 == 0:
            print(i)
        if i == 0:
            continue
        if i == 1:
            add_column(cursor, name_basic, 'code', 'char(6)')
            add_column(cursor, name_basic, 'name', 'char(20)')
            add_column(cursor, name_basic, 'type', 'char(20)')
            date_list = item[3:-1]
            date_len = len(date_list)
            print(date_list)
            # date_list = [time.strftime('%Y-%m-%d', time.strptime(x, '%Y/%m/%d')) for x in date_list]
            date_list = [time.strftime('%Y%m%d', time.strptime(x, '%Y-%m-%d')) for x in date_list]
            for date in date_list:
                add_column(cursor, name_basic, date, 'double')
            continue
        if not item[0]:
            break

        cursor.execute(f'pragma table_info({name_basic})')
        table_info = cursor.fetchall()
        # info: [column num, column name,
        for info in table_info:
            print(info)

        # print(['code', 'name', 'type']+date_list)
        insert(cursor, name_basic, list_to_str_no_quote(['code', 'name', 'type'] + date_list),
               list_to_str([item[0][0:6], item[1], type_name_switch(item[2])]) + ', ' + list_to_str_no_quote(item[3:]))

        cursor.execute(f'select * from {name_basic}')
        for row in cursor.fetchall():
            print(row)

        insert(cursor, name_basic, list_to_str_no_quote(date_list[0:2]), list_to_str_no_quote(item[3:5]))
        insert(cursor, name_basic, date_list, list_to_str_no_quote(item[3:]))
        exit(0)



    file.close()


if __name__ == '__main__':
    dir_sql = 'stock_data_choice.db'
    dir_choice = 'data/choice/hushen300_zhongzheng500_basic.csv'

    # print(time.strftime('%Y-%m-%d', time.strptime('2020/1/1', '%Y/%m/%d')))

    sql = sqlite3.connect(dir_sql)
    cursor = sql.cursor()

    load_choice_basic(cursor, dir_choice)

    sql.commit()
    sql.close()


