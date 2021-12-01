import numpy as np

import trade_simulate


class scale_of(trade_simulate.object_indicator):
    def __init__(self, name, data_name, ratio):
        self.name = name
        self.data_name = data_name
        self.ratio = ratio

    def is_std(self):
        return False

    def get_name(self):
        return self.name

    def frozen_days(self):
        return 0

    def indicator_data_prepare(self, data: dict, day):
        if trade_simulate.find_data_name(data, self.data_name) is None:
            print(f'data dont have item called {self.data_name}')
            exit(0)
        return {'value': trade_simulate.find_data_name(data, self.data_name)[day]}

    def indicator(self, indicator_data: dict):
        return indicator_data['value'] * self.ratio


class std_of(trade_simulate.object_indicator):
    def __init__(self, name, data_name, mean, variance):
        self.name = name
        self.data_name = data_name
        self.mean = mean
        self.variance = variance
        self.ratio = None
        self.shift = None

    def is_std(self):
        return True

    def get_name(self):
        return self.name

    def frozen_days(self):
        return 0

    def indicator_data_prepare(self, data: dict, day):
        if trade_simulate.find_data_name(data, self.data_name) is None:
            print(f'data dont have item called {self.data_name}')
            exit(0)
        if not self.ratio:
            temp = np.array(trade_simulate.find_data_name(data, self.data_name))
            self.ratio = 1 / np.std(temp)
            self.shift = self.mean - np.mean(temp)

        return {'value': trade_simulate.find_data_name(data, self.data_name)[day - self.frozen_days():day + 1]}

    def indicator(self, indicator_data: dict):
        return indicator_data['value'] * self.ratio + self.shift


class ma_of(trade_simulate.object_indicator):
    def __init__(self, name, data_name, ma_day):
        self.name = name
        self.data_name = data_name
        self.ma_day = ma_day

    def is_std(self):
        if 'std' in self.data_name or \
           'lg' in self.data_name or \
           'rate' in self.data_name:
            return True
        else:
            return False

    def get_name(self):
        return self.name

    def frozen_days(self):
        return self.ma_day - 1

    def indicator_data_prepare(self, data: dict, day):
        if trade_simulate.find_data_name(data, self.data_name) is None:
            print(f'data dont have item called {self.data_name}')
            exit(0)
        return {'value': trade_simulate.find_data_name(data, self.data_name)[day - self.frozen_days():day + 1]}

    def indicator(self, indicator_data: dict):
        return sum(indicator_data['value']) / self.ma_day
