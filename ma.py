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
from simulate import simulate, simulate_realistic, plot_date, name_item

dir_sql = 'stock_data_ak.db'


class ma:
    def __init__(self, ma_day, name):
        self.ma_day = ma_day
        self.name = name

    def frozen_days(self):
        return self.ma_day

    def indicator_data_prepare(self, data: dict, day):

    def indicator(self, data: dict):
        res = []
        for day in range(self.frozen_days(), len(data['date'])):
            res.append(sum(data['price'][day-self.ma_day:day]) / self.ma_day)

        return res

    def strategy_data_prepare(self, data: dict, day):
        return {'price': data['price_adjust'][day], 'ma': name_item(data['indicator'], self.name)}

    def strategy(self, strategy_data):
        if strategy_data['price'] > strategy_data['ma']:
            return 1
        else:
            return 0


class ma2:
    def __init__(self, ma_day_short, ma_day_long):
        self.ma_day_short = ma_day_short
        self.ma_day_long = ma_day_long

    def frozen_days(self):
        return self.ma_day_long

    def indicator(self, data: dict):
        res = {'ma_short': [], 'ma_long': []}

        for day in range(0, self.ma_day_short):
            res['ma_short'].append(0)
        for day in range(self.ma_day_short, len(data['date'])):
            res['ma_short'].append(sum(data['price'][day-self.ma_day_short:day]) / self.ma_day_short)

        for day in range(0, self.ma_day_long):
            res['ma_long'].append(0)
        for day in range(self.ma_day_long, len(data['date'])):
            res['ma_long'].append(sum(data['price'][day-self.ma_day_long:day]) / self.ma_day_long)

        return res

    def strategy(self, data: dict, day: int, strategy_data):
        if data['indicator']['ma_short'][day] > data['ma_long'][day]:
            return 1
        else:
            return 0


def strategy_noob(data, day, strategy_data):
    return 1


def run():
    sql = sqlite3.connect(dir_sql)
    cursor = sql.cursor()

    # model = ma(40)
    # data = get_day(cursor, '000001', '2015-01-01', date_end='2021-01-01', day_before=model.frozen_days())
    # data.update(model.indicator_generate(data))
    # data.update(simulate(data, model.strategy, frozen_days=model.frozen_days()))

    # for short in range(1, 20):
    #     for long in range(short+1, 60):
    #         model = ma2(short, long)
    #         data = get_day(cursor, '000001', '2015-01-01', date_end='20r21-01-01', day_before=model.frozen_days())
    #         data.update(model.indicator_generate(data))
    #         data.update(simulate_realistic(data, model.strategy, frozen_days=model.frozen_days()))
    #         print(f'ma2({short}, {long}) money: {data["money"][-1]}')

    model = ma2(19, 37)
    data = get_day(cursor, '000001', '2015-01-01', date_end='2015-02-01', frozen_days=model.frozen_days())
    for i in data:
        print(i)
    exit(0)
    data.update(model.indicator(data))
    data.update(simulate_realistic(data, model.strategy, frozen_days=model.frozen_days()))
    print(f'ma2 money: {data["money"][-1]}')

    # plot_date(data)

    sql.close()


if __name__ == '__main__':
    run()

