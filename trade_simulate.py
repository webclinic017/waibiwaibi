import numpy as np
from datetime import datetime
from dateutil import rrule
import pandas as pd
# from pandas.plotting import
from math import log10 as lg
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


# data dict format:
# data: {
#         code: str,
#         frozen_days: int,
#         date: [str],
#         price: [float],
#         rate: [float],
#         ..., (get and process from database)
#         indicator: [
#                      {name: str,
#                       value: [float],
#                      ],
#                      ...,
#                     },
#          strategy: [
#                     {name: str,
#                      ratio: [float],
#                      money: [float],
#                      money_lg: [float],
#                      money_change_lg: [float],
#                      ...,
#                     },
#                     ...,
#                    ],
#
#
#        }

class object_indicator:
    def get_name(self):
        return ''

    def frozen_days(self):
        return 0

    def indicator_data_prepare(self, data: dict, day):
        return {}

    def indicator(self, indicator_data: dict):
        return 0


class object_strategy:
    def get_name(self):
        return ''

    def strategy_data_prepare(self, data: dict, day):
        return {}

    def strategy(self, strategy_data: dict):
        return 0


def data_keys(data: dict):
    keys = list(data.keys())
    if 'indicator' in data.keys():
        keys.extend([x['name'] for x in data['indicator']])
    return keys


def data_slice(data: dict, start: int, end: int):
    res = data
    dont_slice = ['code', 'frozen_days', 'indicator', 'strategy']
    for name in data:
        if name not in dont_slice:
            res[name] = res[name][start:end]

    for indic in res['indicator']:
        indic['value'] = indic['value'][start:end]

    for strat in res['strategy']:
        for item in strat:
            strat[item] = strat[item][start:end]

    return res


def name_index(data: dict, name: str):
    if not data:
        return -1
    for i in range(0, len(data)):
        if data[i]['name'] == name:
            return i
    return -1


def name_item(data: dict, name: str):
    index = name_index(data, name)
    if index == -1:
        return None
    else:
        return data[index]


def indicator_generate(data: dict, indicator: object_indicator):
    if 'indicator' not in data.keys():
        data['indicator'] = []
    if name_index(data['indicator'], indicator.get_name()) == -1:
        data['indicator'].append(_indicator_generate(data, indicator))


def _indicator_generate(data: dict, indicator: object_indicator):
    res = {'name': indicator.get_name(), 'value': []}
    for day in range(0, data['frozen_days']):
        res['value'].append(0)
    for day in range(data['frozen_days'], len(data['date'])):
        prepare_data = indicator.indicator_data_prepare(data, day)
        res['value'].append(indicator.indicator(prepare_data))

    return res


def simulate(data: dict, strategy: object_strategy):
    if 'strategy' not in data:
        data['strategy'] = []
    if name_index(data['strategy'], strategy.get_name()) == -1:
        data['strategy'].append(_simulate(data, strategy))


def _simulate(data: dict, strategy: object_strategy):
    res = {'name': strategy.get_name(), 'ratio': [], 'money_change_lg': [], 'money': [], 'money_lg': []}
    for day in range(0, data['frozen_days']):
        res['ratio'].append(0)
        res['money_change_lg'].append(0)

    for day in range(data['frozen_days'], len(data['date'])):
        prepare_data = strategy.strategy_data_prepare(data, day)
        ratio = strategy.strategy(prepare_data)
        res['ratio'].append(ratio)
        res['money_change_lg'].append(res['ratio'][-2] * data['rate_lg'][day])

    total_change_lg = 0
    for change in res['money_change_lg']:
        total_change_lg += change
        res['money_lg'].append(total_change_lg)
        res['money'].append(10 ** total_change_lg)

    return res


def simulate_realistic(data, strategy, strategy_data=None, frozen_days=1, commision_buy=0.0005, commision_sell=0.0015):
    res = {'ratio': [], 'money_change_lg': [], 'money': [], 'money_lg': [], 'commision': []}
    for day in range(0, len(data['date'])):
        if day < frozen_days:
            res['ratio'].append(0)
            res['money_change_lg'].append(0)
            res['commision'].append(0)
        else:
            ratio = strategy(data, day, strategy_data)
            res['ratio'].append(ratio)
            ratio_change = res['ratio'][day] - res['ratio'][day - 1]
            if ratio_change > 0:
                res['commision'].append(ratio_change * lg(1 + commision_buy))
            else:
                res['commision'].append(-ratio_change * lg(1 + commision_sell))
            res['money_change_lg'].append(ratio * (data['rate_lg'][day] + res['commision'][day]))

    total_change_lg = 0
    for change_lg in res['money_change_lg']:
        total_change_lg += change_lg
        res['money_lg'].append(total_change_lg)
        res['money'].append(10 ** total_change_lg)

    return res


def plot_date(data: dict):
    data = data_slice(data, data['frozen_days'], len(data['date']))

    fig = plt.figure(figsize=(12, 8))

    strategy_amount = len(data['strategy'])
    axs = [plt.subplot2grid((1 + strategy_amount, 1), (0, 0), colspan=1, rowspan=1)]
    for i in range(0, strategy_amount):
        axs.append(plt.subplot2grid((1 + strategy_amount, 1), (i+1, 0), colspan=1, rowspan=1))

    data['date'] = [datetime.strptime(x, '%Y-%m-%d') for x in data['date']]

    axs[0].plot('date', 'price_adjust', data=data)
    for indicator in data['indicator']:
        axs[0].plot(data['date'], indicator['value'])

    for i in range(0, strategy_amount):
        axs[i+1].plot(data['date'], data['price_std_lg'])
        axs[i+1].plot(data['date'], data['strategy'][i]['money_lg'])
        ax_ratio = axs[i+1].twinx()
        ax_ratio.plot(data['date'],  data['strategy'][i]['ratio'], drawstyle='steps-pre', linewidth='0.5')

    for i in range(0, len(axs)):
        ax = axs[i]

        datemin = np.datetime64(data['date'][0], 'Y')
        datemax = np.datetime64(data['date'][-1], 'Y') + np.timedelta64(1, 'Y')
        # print(datemin, datemax)

        ax.set_xlim(data['date'][0], data['date'][-1])

        ax.xaxis.set_major_locator(mdates.MonthLocator(int(str(datemax)) - int(str(datemin))))
        ax.xaxis.set_minor_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))

        ax.format_xdata = mdates.DateFormatter('%Y-%m')
        ax.format_ydata = lambda x: f'${x:.2f}'  # Format the price.
        ax.grid(True)

    fig.autofmt_xdate()

    plt.show()
