import os
import sys
import time
import numpy as np
import pandas as pd
import sqlite3
from matplotlib import pyplot as plt

import akshare as ak
import mplfinance as mpf

import trade_simulate
from get_stock import get_day
from trade_simulate import indicator_generate, simulate, simulate_realistic, plot_date, name_item, object_indicator, object_strategy, name_index
import mak_stock_identifier as si
from indicators import ma_of


class ma(object_indicator, object_strategy):
    def __init__(self, name, ma_day):
        self.name = name
        self.ma_day = ma_day

    def get_name(self):
        return self.name

    def frozen_days(self):
        return self.ma_day-1

    def indicator_data_prepare(self, data: dict, day):
        return {'price': data['price_adjust'][day-self.frozen_days():day+1]}

    def indicator(self, indicator_data: dict):
        return sum(indicator_data['price']) / self.ma_day

    def strategy_data_prepare(self, data: dict, day):
        return {'price': data['price_adjust'][day], 'ma': name_item(data['indicator'], self.get_name())['value'][day]}

    def strategy(self, strategy_data: dict):
        if strategy_data['price'] > strategy_data['ma']:
            return 1
        else:
            return 0


class ma2(object_strategy):
    def __init__(self, name, ma_day_short, ma_day_long):
        self.name = name
        self.ma_day_short = ma_day_short
        self.ma_day_long = ma_day_long
        self.ma_short = ma(self.get_name_short(), self.ma_day_short)
        self.ma_long = ma(self.get_name_long(), self.ma_day_long)

    def get_name(self):
        return self.name

    def get_name_short(self):
        return self.name + '_short'

    def get_name_long(self):
        return self.name + '_long'

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

    def strategy_data_prepare(self, data: dict, day):
        return {'ma_short': name_item(data['indicator'], self.get_name_short())['value'][day],
                'ma_long': name_item(data['indicator'], self.get_name_long())['value'][day]}

    def strategy(self, strategy_data: dict):
        if strategy_data['ma_short'] > strategy_data['ma_long']:
            return 1
        else:
            return 0


def strategy_noob(data, day, strategy_data):
    return 1


def run():
    dir_sql = 'stock_data_ak.db'
    sql = sqlite3.connect(dir_sql)
    cursor = sql.cursor()

    model = ma('ma40', 40)
    data = get_day(cursor, '000001', '2015-01-01', date_end='2021-01-01', frozen_days=model.frozen_days())
    indicator_generate(data, model)
    simulate(data, model)

    model = ma2('ma2_5_40', 5, 40)
    indicator_generate(data, model.ma_long)
    indicator_generate(data, model.ma_short)
    simulate(data, model)
    plot_date(data)

    sql.close()


if __name__ == '__main__':
    run()

