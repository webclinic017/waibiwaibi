
import os
import sys
import time
import numpy as np
import pandas as pd
import sqlite3

import akshare as ak
import mplfinance as mpf

from get_stock import get_day
from simulate import simulate, plot_date


dir_sql = 'stock_data_ak.db'


class ma:
    def __init__(self, data, ma_day):
        data['ma'] = []
        for day in range(0, len(data['date'])):
            ma_total = 0
            for i in range((0 if day<ma_day else day-ma_day+1), day):
                ma_total += data['price'][i]
            data['ma'].append(ma_total / (day+1 if day<ma_day else ma_day))

    def strategy(self, data, day, strategy_data):
        if data['price'][day] > data['ma'][day]:
            return 1
        else:
            return 0


if __name__ == '__main__':
    sql = sqlite3.connect(dir_sql)
    cursor = sql.cursor()

    data = get_day(cursor, '000001', '2020-01-01', period=100, day_before=5)
    model = ma(data, 5)
    print(len({i: data[i][5:] for i in data}['date']))
    data['money'], data['ratio'] = simulate(data, 5, model.strategy)
    print(data['money'], data['ratio'])

    print(data)
    for i in data:
        print(i, ': ', len(data[i]))
    plot_date(data)


    sql.close()
    #
    # stock_us_daily_df = ak.stock_us_daily(symbol="AAPL", adjust="qfq")
    # stock_us_daily_df = stock_us_daily_df[["open", "high", "low", "close", "volume"]]
    # stock_us_daily_df.columns = ["Open", "High", "Low", "Close", "Volume"]
    # stock_us_daily_df.index.name = "Date"
    # stock_us_daily_df = stock_us_daily_df["2020-04-01": "2020-04-29"]
    # mpf.plot(stock_us_daily_df, type='candle', mav=(3, 6, 9), volume=True, show_nontrading=False)



