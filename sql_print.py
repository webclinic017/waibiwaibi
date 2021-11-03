
import os
import sys
import numpy as np
import pandas as pd
import sqlite3


dir_sql = 'stock_data.db'

if __name__ == '__main__':

    sql = sqlite3.connect(dir_sql)
    cursor = sql.cursor()

    # cursor.execute('select * from stock_list_a')
    # for row in cursor.fetchall():
    #     print(row)

    cursor.execute('select name from sqlite_master where type = "table" order by name')
    for row in cursor.fetchall():
        print(row)

    sql.close()




