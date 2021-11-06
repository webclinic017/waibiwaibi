import numpy as np
from datetime import datetime
from dateutil import rrule
import pandas as pd
# from pandas.plotting import
from math import log10 as lg
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


# data dict format:
# data: [
#         code: str,
#         date: [str],
#         frozen_days: int,
#         stock: [
#                  price: [double],
#                  rate: [double],
#                  ...], (get and process from database)
#         indicator: [
#                      ma: []
#
#
#


def simulate(data, strategy, strategy_data=None, frozen_days=1):
    res = {'ratio': [], 'money_change_lg': [], 'money': [], 'money_lg': []}
    for day in range(0, len(data['date']) - 1):
        if day < frozen_days:
            res['ratio'].append(0)
            res['money_change_lg'].append(0)
        else:
            ratio = strategy(data, day, strategy_data)
            res['ratio'].append(ratio)
            res['money_change_lg'].append(ratio * data['rate_lg'][day + 1])
    res['ratio'].append(res['ratio'][-1])
    res['money_change_lg'].append(res['money_change_lg'][-1])

    total_change_lg = 0
    for change in res['money_change_lg']:
        total_change_lg += change
        res['money_lg'].append(total_change_lg)
        res['money'].append(10 ** total_change_lg - 1)

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
        res['money'].append(10 ** total_change_lg - 1)

    return res


def plot_date(data: dict):
    fig = plt.figure(figsize=(12, 8))
    axs = []
    axs.append(plt.subplot2grid((5, 1), (0, 0), colspan=1, rowspan=2))
    axs.append(plt.subplot2grid((5, 1), (2, 0), colspan=1, rowspan=2))
    axs.append(plt.subplot2grid((5, 1), (4, 0), colspan=1, rowspan=1))

    data['date'] = [datetime.strptime(x, '%Y-%m-%d') for x in data['date']]

    axs[0].plot('date', 'price', data=data)
    axs[0].plot('date', 'ma_long', data=data)
    axs[0].plot('date', 'ma_short', data=data)

    axs[1].plot('date', 'price_std_lg', data=data)
    axs[1].plot('date', 'money_lg', data=data)

    axs[2].plot('date', 'ratio', data=data, drawstyle='steps-pre')

    for i in range(0, len(axs)):
        ax = axs[i]

        datemin = np.datetime64(data['date'][0], 'Y')
        datemax = np.datetime64(data['date'][-1], 'Y') + np.timedelta64(1, 'Y')
        # print(datemin, datemax)

        ax.set_xlim(data['date'][0], data['date'][-1])

        ax.xaxis.set_major_locator(mdates.MonthLocator(int(str(datemax)) - int(str(datemin))))
        ax.xaxis.set_minor_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))

        ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
        ax.format_ydata = lambda x: f'${x:.2f}'  # Format the price.
        ax.grid(True)

    fig.autofmt_xdate()

    plt.show()
