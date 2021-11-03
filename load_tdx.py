
import os
import sys
import numpy as np
import pandas as pd
import sqlite3
from math import log10 as lg
from tqdm import tqdm


dir_sql = 'stock_data_tdx.db'
dir_tdx = 'data/tongdaxin'


def load_stack_list_a(cursor):
    cursor.execute('create table if not exists stock_list_a ( \
                    id integer primary key autoincrement not null, \
                    code char(6) not null, \
                    name char(20), \
                    first_date date)')

    list_code = os.listdir(dir_tdx)
    for i in tqdm(range(0, len(list_code))):
        file_name = list_code[i]
        file = open(os.path.join(dir_tdx, file_name))

        # code, name, _, __ = file.readline().split()
        first_line = file.readline().split()
        code = first_line[0]
        name = first_line[1]
        if len(first_line) > 4:
            name += first_line[2]

        file.readline()

        first_date = ''
        for l in range(0, 1):
            line = file.readline()
            if line:
                if len(line.split(',')) < 7:
                    break
                date, price_open, price_highest, price_lowest, price_close, turnover, volume = line.split(',')
                date = date.replace('/', '-')
                # print(date)
                if l == 0:
                    first_date = date
        file.close()

        # print(f'{file_name[3:9]}')
        # print(code)
        # print(name)
        cursor.execute(f'insert into stock_list_a(code, name, first_date) \
                       values("{file_name[3:9]}", "{name}", "{first_date}")')


def load_day_price(cursor):
    list_code = os.listdir(dir_tdx)
    for i in tqdm(range(0, len(list_code))):
        file_name = list_code[i]
        file = open(os.path.join(dir_tdx, file_name))

        # code, name, _, __ = file.readline().split()
        first_line = file.readline().split()
        code = first_line[0]
        name = first_line[1]
        if len(first_line) > 4:
            name += first_line[2]

        cursor.execute(f'create table if not exists day_{code} ( \
                         id integer primary key autoincrement not null, \
                         date date, \
                         price double, \
                         turnover long)')

        file.readline()

        first_date = ''
        while True:
            line = file.readline()
            if line:
                if len(line.split(',')) < 7:
                    break
                date, price_open, price_highest, price_lowest, price_close, turnover, volume = line.split(',')
                date = date.replace('/', '-')
                cursor.execute(f'insert into day_{code}(date, price, turnover) \
                       values("{date}", "{price_close}", "{turnover}")')
        file.close()

        sql.commit()


def compute_rate(cursor):
    list_code = os.listdir(dir_tdx)
    for i in tqdm(range(0, len(list_code))):
        code = list_code[i][3:9]
        # print(code)
        # cursor.execute(f'alter table day_{code} drop column rate')
        # cursor.execute(f'alter table day_{code} drop column rate_lg')
        # cursor.execute(f'select rate from day_{code}')
        cursor.execute(f'select * from sqlite_master where name = "day_{code}" and sql like "%rate%"')
        res = cursor.fetchall()
        if i < 2:
            print(i, res)
        if not res:
            cursor.execute(f'alter table day_{code} \
                             add rate double')
            cursor.execute(f'alter table day_{code} \
                             add rate_lg double')
        cursor.execute(f'select count(*) from day_{code}')
        amount = cursor.fetchall()[0][0]
        if amount < 2:
            continue
        cursor.execute(f'select price from day_{code}')
        price = cursor.fetchall()
        price = [x[0] for x in price]
        # print(price)
        # exit(0)
        for day in range(1, amount):
            try:
                cursor.execute(f'update day_{code} set rate = {price[day]/price[day-1]} \
                                 where id = {day+1}')
                cursor.execute(f'update day_{code} set rate_lg = {lg(price[day]/price[day-1])} \
                                 where id = {day+1}')
            except:
                print(code, day, price[day], price[day-1])
                exit(0)


if __name__ == '__main__':
    sql = sqlite3.connect(dir_sql)
    cursor = sql.cursor()

    # load_stack_list_a(cursor)

    # load_day_price(cursor)

    compute_rate(cursor)

    sql.commit()
    sql.close()


