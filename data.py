
import os
import sys
import numpy as np
import pandas as pd
#import tushare as ts not free
import sqlalchemy
import sqlite3

dir_sql = 'stock_data.db'

if __name__ == '__main__':

    sql = sqlite3.connect(dir_sql)
    cursor = sql.cursor()

    cursor.execute('create table if not exists stock_list_a ( \
                    code char(6) not null, \
                    name char(20), \
                    first_date date)')
    # cursor.execute('insert into stock_list_a(code, name) \
    #                values("000002", "万科")')
    # cursor.execute('insert into stock_list_a(code, name) \
    #                values("000001", "平安银行")')
    # cursor.execute('alter table stock_list_a add \
    #                date_market date')
    # cursor.execute('update stock_list_a set name = "万科A" \
    #                where code = "000002"')

    sql.commit()
    sql.close()




