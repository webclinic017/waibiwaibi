# @ last edit time 2021/10/31 18:55

import os
import sys
import numpy as np
import pandas as pd
import sqlite3
from math import log10 as lg
from tqdm import tqdm


def create_table(cursor, table: str):
    cursor.execute(f'create table if not exists {table} ( \
                     id integer primary key autoincrement not null)')


def insert(cursor, table: str, column_list: list, value_list: list, condition='', not_repeat=True):
    # print(f'insert into {table} ({column_list}) \
    #                  values({value_list})')
    if not_repeat:
        cursor.execute(f'insert into {table} ({list_to_str_no_quote(column_list)}) \
                         select {list_to_str(value_list)} \
                         where not exists(select * from {table} where {column_list[0]} = "{value_list[0]}")')
    else:
        cursor.execute(f'insert into {table} ({list_to_str_no_quote(column_list)}) \
                         values({list_to_str(value_list)}) \
                         {condition}')


def insert_not_repeat(cursor, table: str, column_list: list, value_list: list, condition=''):
    # print(f' insert into {table} ({list_to_str_no_quote(column_list)}) \

    cursor.execute(f' insert into {table} ({list_to_str_no_quote(column_list)}) \
                       select {list_to_str(value_list)} \
                         where not exists(select * from {table} where {column_list[0]} = "{value_list[0]}")')
    # cursor.execute(f'insert or replace into {table} ({list_to_str_no_quote(column_list)}) \
    #                  values({list_to_str(value_list)}) \
    #                  {condition}')
    # print(f'if not exists(select * from {table} where {column_list[0]} = {value_list[0]}) \
    #                  then insert into {table} ({list_to_str_no_quote(column_list)}) \
    #                  values({list_to_str(value_list)}) \
    #                  {condition}')
    # cursor.execute(f'if not exists(select * from {table} where {column_list[0]} = {value_list[0]}) \
    #                  then insert into {table} ({list_to_str_no_quote(column_list)}) \
    #                  values({list_to_str(value_list)}) \
    #                  {condition}')


def update(cursor, table: str, column_list: list, value_list: list):
    # print(f'insert into {table} ({column_list}) \
    #                  values({value_list})')
    cursor.execute(f'insert into {table} ({list_to_str_no_quote(column_list)}) \
                     values({list_to_str(value_list)})')


def add_column(cursor, table: str, column: str, type: str):
    cursor.execute(f'select * from sqlite_master where name = "{table}" and sql like "%{column}%"')
    res = cursor.fetchall()
    if not res:
        cursor.execute(f'alter table {table} \
                         add "{column}" {type}')


def select(cursor, item: str, table: str, condition: str):
    # print(f'select {item} from {table} {condition}')
    cursor.execute(f'select {item} from {table} {condition}')
    return cursor.fetchall()


def table_info(cursor, table: str):
    cursor.execute(f'pragma table_info({table})')
    table_info = cursor.fetchall()
    return table_info



def list_to_str(l: list):
    return str(l).strip('[').strip(']')


def list_to_str_no_quote(l: list):
    l_str = ''
    for x in l:
        l_str += str(x).strip() + ', '
    l_str = l_str[:-2]

    return l_str
