
import numpy as np
import time
from datetime import datetime
import pandas as pd
from math import log10 as lg
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from tqdm import tqdm

import get_stock
import mak_stock_identifier as si

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
#                       std: bool,
#                      },
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

    def is_std(self):
        return False

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
    if si.indicator in data.keys():
        keys.extend([x[si.name] for x in data[si.indicator]])
    return keys


def data_slice(data: dict, start: int, end: int):
    res = data
    dont_slice = [si.code, si.frozen_days, si.indicator, si.strategy]
    for name in data:
        if name not in dont_slice:
            res[name] = res[name][start:end]

    for indic in res[si.indicator]:
        indic[si.value] = indic[si.value][start:end]

    for strat in res[si.strategy]:
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


def find_data_name(data, name: str):
    if name in data.keys():
        return data[name]
    elif name_item(data[si.indicator], name):
        return name_item(data[si.indicator], name)[si.value]
    elif name_item(data[si.strategy], name):
        return name_item(data[si.strategy], name)[si.value]
    else:
        return None


def indicator_generate(data: dict, indicator: object_indicator):
    if si.indicator not in data.keys():
        data[si.indicator] = []
    if name_index(data[si.indicator], indicator.get_name()) == -1:
        data[si.indicator].append(_indicator_generate(data, indicator))


def _indicator_generate(data: dict, indicator: object_indicator):
    res = {si.name: indicator.get_name(), si.value: [], si.is_std: indicator.is_std()}
    for day in range(0, data[si.frozen_days]):
        res[si.value].append(0)
    for day in range(data[si.frozen_days], len(data[si.date])):
        prepare_data = indicator.indicator_data_prepare(data, day)
        res[si.value].append(indicator.indicator(prepare_data))

    return res


# indicator list format:
# [
#   [object_indicator, name, ...],
#   ...
# ]


def indicator_generate_batch(data, indicators: list):
    for i in indicators:
        indicator_generate(data, i[0](*i[1:]))


def indicator_batch_names(indicators: list):
    return [x[1] for x in indicators]


def stock_data_prepare(cursor, stock_list, stock_config):
    available_code = []
    available_data = []
    print('start preparing stock data for training: ')
    time.sleep(0.1)
    for i in tqdm(range(0, len(stock_list))):
        code = stock_list[i]
        data = get_stock.get_day(cursor, code, stock_config[si.start_date], stock_config[si.end_date],
                                 frozen_days=stock_config[si.frozen_days])
        if data:
            indicator_generate_batch(data, stock_config[si.indicator_list])
            available_code.append(code)
            available_data.append(data)

    print(f'stock data for training is prepared, {len(available_code)} stocks in total')
    time.sleep(0.1)

    return available_code, available_data


def simulate(data: dict, strategy: object_strategy):
    if si.strategy not in data:
        data[si.strategy] = []
    if name_index(data[si.strategy], strategy.get_name()) == -1:
        data[si.strategy].append(_simulate(data, strategy))


def _simulate(data: dict, strategy: object_strategy):
    res = {si.name: strategy.get_name(), si.ratio: [], si.money_change_lg: [], si.money: [], si.money_lg: []}
    for day in range(0, data[si.frozen_days]):
        res[si.ratio].append(0)
        res[si.money_change_lg].append(0)

    for day in range(data[si.frozen_days], len(data[si.date])):
        prepare_data = strategy.strategy_data_prepare(data, day)
        ratio = strategy.strategy(prepare_data)
        res[si.ratio].append(ratio)
        res[si.money_change_lg].append(res[si.ratio][-2] * data[si.rate_lg][day])

    total_change_lg = 0
    for change in res[si.money_change_lg]:
        total_change_lg += change
        res[si.money_lg].append(total_change_lg)
        res[si.money].append(10 ** total_change_lg)

    return res


def simulate_realistic(data: dict, strategy: object_strategy):
    if si.strategy not in data:
        data[si.strategy] = []
    if name_index(data[si.strategy], strategy.get_name()) == -1:
        data[si.strategy].append(_simulate_realistic(data, strategy))


def _simulate_realistic(data, strategy, strategy_data=None, frozen_days=1, commision_buy=0.0005, commision_sell=0.0015):
    res = {si.name: strategy.get_name(), si.ratio: [], si.money_change_lg: [], si.money: [], si.money_lg: [], si.commission: []}

    for day in range(0, data[si.frozen_days]):
        res[si.ratio].append(0)
        res[si.money_change_lg].append(0)
        res[si.commission].append(0)

    for day in range(data[si.frozen_days], len(data[si.date])):
        prepare_data = strategy.strategy_data_prepare(data, day)
        ratio = strategy.strategy(prepare_data)
        res[si.ratio].append(ratio)
        ratio_change = res[si.ratio][day] - res[si.ratio][day - 1]
        if ratio_change > 0:
            res[si.commission].append(ratio_change * lg(1 + commision_buy))
        elif ratio_change < 0:
            res[si.commission].append(-ratio_change * lg(1 + commision_sell))
        else:
            res[si.commission].append(0)
        res[si.money_change_lg].append(res[si.ratio][-2] * data[si.rate_lg][day] - res[si.commission][day])

    total_change_lg = 0
    for change in res[si.money_change_lg]:
        total_change_lg += change
        res[si.money_lg].append(total_change_lg)
        res[si.money].append(10 ** total_change_lg)

    return res


def plot_date(data: dict):
    data = data_slice(data, data[si.frozen_days], len(data[si.date]))

    fig = plt.figure(figsize=(12, 8))

    indicator_window = 0
    if True in [x[si.is_std] for x in data[si.indicator]]:
        indicator_window = 1
        for indic in data[si.indicator]:
            if abs(np.mean(np.array(indic[si.value]))) > 1:
                indicator_window = 2
                break
    strategy_amount = len(data[si.strategy])
    window_amount = 1 + indicator_window + strategy_amount
    indicator_window_range = range(1, 1+indicator_window)
    strategy_window_range = range(1+indicator_window, 1+indicator_window+strategy_amount)

    axs = [plt.subplot2grid((window_amount, 1), (0, 0), colspan=1, rowspan=1)]
    for i in indicator_window_range:
        axs.append(plt.subplot2grid((window_amount, 1), (i, 0), colspan=1, rowspan=1))
    for i in strategy_window_range:
        axs.append(plt.subplot2grid((window_amount, 1), (i, 0), colspan=1, rowspan=1))

    data[si.date] = [datetime.strptime(x, '%Y-%m-%d') for x in data[si.date]]

    axs[0].plot(data[si.date], data[si.price_adjust], label=si.price_adjust)
    for i in indicator_window_range:
        axs[i].plot(data[si.date], data[si.price_std_lg], label=si.price_std_lg)
    for indicator in data[si.indicator]:
        if indicator[si.is_std]:
            if abs(np.mean(np.array(indicator[si.value]))) > 1:
                ax = axs[indicator_window_range[0]]
            else:
                ax = axs[indicator_window_range[-1]]
        else:
            ax = axs[0]
        ax.plot(data[si.date], indicator[si.value], label=indicator[si.name])

    for i in range(0, len(data[si.strategy])):
        ax = axs[strategy_window_range[i]]
        ax.plot(data[si.date], data[si.price_std_lg], label=si.price_std_lg)
        print(data[si.strategy][i].keys())
        ax.plot(data[si.date], data[si.strategy][i][si.money_lg], label=data[si.strategy][i][si.name])
        ax_ratio = ax.twinx()
        ax_ratio.plot(data[si.date], data[si.strategy][i][si.ratio], label=si.ratio, drawstyle='steps-pre', linewidth='0.5')

    for i in range(0, len(axs)):
        ax = axs[i]
        ax.legend(ncol=2)

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
