# @ last edit time 2021/11/6 12:18

import sqlite3
import time

import neat
from tqdm import tqdm

import get_stock
import trade_simulate
from trade_simulate import indicator_generate, simulate, simulate_realistic, plot_date, name_item, object_indicator, object_strategy, name_index, data_keys
from ma import ma


class neat_day(object_strategy):
    def __init__(self, name, net, required_data: list):
        self.name = name
        self.net = net
        self.required_data = required_data

    def get_name(self):
        return self.name

    def strategy_data_prepare(self, data: dict, day):
        res = [1]
        for item in data.keys():
            if item in self.required_data:
                res.append(data[item][day])
        if 'indicator' in data.keys():
            for item in [x['name'] for x in data['indicator']]:
                if item in self.required_data:
                    res.append(name_item(data['indicator'], item)['value'][data['frozen_days'] + 0])

        return {'input': res}

    def strategy(self, strategy_data: dict):
        output = self.net(strategy_data['input'])[0]
        # print(f'output: {output}')
        if output < 0:
            output = 0
        if output > 1:
            output = 1
        return output


class neat_day_evaler:
    def __init__(self, available_data: list, required_data: list):
        self.available_data = available_data
        self.required_data = required_data

    def __call__(self, genomes, config):
        for genome_id, genome in tqdm(genomes):
            genome.fitness = self.average_profit(genome, config)

    def average_profit(self, genome, config):
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        net_strategy = neat_day('neat', net.activate, self.required_data)
        fitness = []
        for stock in self.available_data:
            result = trade_simulate._simulate(stock, net_strategy)
            profit = result['money'][-1]
            fitness.append(profit)
        total_fitness = sum(fitness) / len(fitness)
        return total_fitness


def run():
    dir_sql = 'stock_data_ak.db'
    sql = sqlite3.connect(dir_sql)
    cursor = sql.cursor()

    stock_list = get_stock.get_code_list(cursor)
    stock_list.sort()
    available_code = []
    available_data = []
    print('start preparing stock data for training: ')
    time.sleep(0.1)
    for i in tqdm(range(0, len(stock_list))):
        code = stock_list[i]
        data = get_stock.get_day(cursor, code, '2010-01-01', '2020-01-01', frozen_days=100)
        if data:
            indicator_generate(data, ma('ma5', 5))
            indicator_generate(data, ma('ma20', 20))
            indicator_generate(data, ma('ma60', 60))
            available_code.append(code)
            available_data.append(data)
    print(f'stock data for training is prepared, {len(available_code)} stocks in total')
    time.sleep(0.1)

    evaler = neat_day_evaler(available_data, ['price_std_lg', 'rate_lg', 'ma5', 'ma20', 'ma60', 'exchange_rate'])

    config_path = 'neat_config'
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(5))

    winner = p.run(evaler, 300)

    print('\nBest genome:\n{!s}'.format(winner))
    print('\nOutput:')
    print(f'winner average profit: {evaler.average_profit(winner, config)}')

    sql.close()


if __name__ == '__main__':
    run()
