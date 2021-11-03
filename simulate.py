
import pandas as pd
from math import log10 as lg
import matplotlib.pyplot as plt


def simulate(data, frozen_days, strategy, strategy_data=None, ):
    money_change = []
    ratio_list = []
    for day in range(0, len(data['date'])):
        if day < frozen_days:
            ratio_list.append(0)
            money_change.append(0)
        else:
            ratio = strategy(data, day, strategy_data)
            ratio_list.append(ratio)
            money_change.append(ratio * lg(1+0.01*data['rate'][day]))

    money = []
    current = 0
    for change in money_change:
        current += change
        money.append(current)

    return money, ratio_list


def plot_date(data):
    df = pd.DataFrame(data)
    print(df)
    # data['date'] = pd.to_datetime(data['date'])









