import os
import sys
import time
import numpy as np
import pandas as pd
import sqlite3
from matplotlib import pyplot as plt

import akshare as ak
import mplfinance as mpf

from get_stock import get_day
from simulate import simulate, plot_date

dir_sql = 'stock_data_ak.db'


class ma:
    def __init__(self, ma_day):
        self.ma_day = ma_day

    def frozen_days(self):
        return self.ma_day

    def indicator_generate(self, data: dict):
        res = {'ma': []}
        for day in range(0, self.frozen_days()):
            res['ma'].append(0)

        for day in range(self.frozen_days(), len(data['date'])):
            res['ma'].append(sum(data['price'][day-5:day]) / self.ma_day)

        return res

    def strategy(self, data: dict, day: int, strategy_data):
        if data['price'][day] > data['ma'][day]:
            return 1
        else:
            return 0


if __name__ == '__main__':
    sql = sqlite3.connect(dir_sql)
    cursor = sql.cursor()

    model = ma(5)
    data = get_day(cursor, '000001', '2015-01-01', date_end='2021-01-01', day_before=model.frozen_days())
    data.update(model.indicator_generate(data))
    # print(len({i: data[i][5:] for i in data}['date']))
    data.update(simulate(data, 5, model.strategy))
    # print(data['money'], data['ratio'])

    # print(data)
    # for i in data:
    #     print(i, ': ', len(data[i]))
    plot_date(data)

    sql.close()
    #
    # stock_us_daily_df = ak.stock_us_daily(symbol="AAPL", adjust="qfq")
    # stock_us_daily_df = stock_us_daily_df[["open", "high", "low", "close", "volume"]]
    # stock_us_daily_df.columns = ["Open", "High", "Low", "Close", "Volume"]
    # stock_us_daily_df.index.name = "Date"
    # stock_us_daily_df = stock_us_daily_df["2020-04-01": "2020-04-29"]
    # mpf.plot(stock_us_daily_df, type='candle', mav=(3, 6, 9), volume=True, show_nontrading=False)
