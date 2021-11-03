# @ last edit time 2021/10/31 18:55

import os
import sys
import numpy as np
import pandas as pd
import sqlite3
from math import log10 as lg
from tqdm import tqdm


def create_table(cursor, table):
    cursor.execute(f'create table if not exists {table} ( \
                     id integer primary key autoincrement not null)')


def insert(cursor, table, column_list, value_list):
    # print(f'insert into {table} ({column_list}) \
    #                  values({value_list})')
    cursor.execute(f'insert into {table} ({column_list}) \
                     values({value_list})')


def update(cursor, table, column_list, value_list):
    print(f'insert into {table} ({column_list}) \
                     values({value_list})')
    cursor.execute(f'insert into {table} ({column_list}) \
                     values({value_list})')


def add_column(cursor, table, column, type):
    cursor.execute(f'select * from sqlite_master where name = "{table}" and sql like "%{column}%"')
    res = cursor.fetchall()
    if not res:
        cursor.execute(f'alter table {table} \
                         add "{column}" {type}')


def select(cursor, item, table, condition):
    print(f'select {item} from {table} {condition}')
    cursor.execute(f'select {item} from {table} {condition}')
    return cursor.fetchall()


def list_to_str(l):
    return str(l).strip('[').strip(']')


def list_to_str_no_quote(l):
    l_str = ''
    for x in l:
        l_str += str(x).strip() + ', '
    l_str = l_str[:-2]

    return l_str
