# @ last edit time 2021/11/6 12:18

import sqlite3
import time
import multiprocessing
import neat
from tqdm import tqdm

import get_stock
import trade_simulate
from trade_simulate import indicator_generate, simulate, simulate_realistic, plot_date, name_item, object_indicator, \
    object_strategy, name_index, data_keys
from ma import ma, ma_of
import mak_stock_identifier as si
import neat_visualize


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
        profit_list = []
        for stock in self.available_data:
            result = trade_simulate._simulate(stock, net_strategy)
            profit = result['money'][-1]
            profit_list.append(profit)
        return sum(profit_list) / len(profit_list)

    def simulate_result(self, genome, config, stock_data):
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        net_strategy = neat_day('neat', net.activate, self.required_data)
        return trade_simulate._simulate(stock_data, net_strategy)


class neat_day_evaler_multi_process(neat_day_evaler, object):
    def __init__(self, available_data: list, required_data: list, num_workers: 1):
        super().__init__(available_data, required_data)
        self.num_workers = num_workers
        self.pool = multiprocessing.Pool(num_workers)

    def __call__(self, genomes, config):
        jobs = []
        for ignored_genome_id, genome in genomes:
            jobs.append(self.pool.apply_async(self.average_profit, (genome, config)))

        # assign the fitness back to each genome
        for job, (ignored_genome_id, genome) in zip(jobs, genomes):
            genome.fitness = job.get()

    # def __del__(self):
    #     self.pool.close()
    #     self.pool.join()

    def __getstate__(self):
        self_dict = self.__dict__.copy()
        del self_dict['pool']

        return self_dict

    def __setstate__(self, state):
        self.__dict__.update(state)


def run():
    dir_sql = 'stock_data_ak.db'
    sql = sqlite3.connect(dir_sql)
    cursor = sql.cursor()

    # stock_list = get_stock.get_code_list(cursor)
    stock_list = get_stock.get_code_list_hs300(cursor, '2010-01-01')
    stock_list.sort()
    available_code = []
    available_data = []
    print('start preparing stock data for training: ')
    time.sleep(0.1)
    for i in tqdm(range(0, len(stock_list))):
        code = stock_list[i]
        data = get_stock.get_day(cursor, code, '2010-01-01', '2020-01-01', frozen_days=300)
        if data:
            # indicator_generate(data, ma('ma5', 5))
            # indicator_generate(data, ma('ma20', 20))
            # indicator_generate(data, ma('ma60', 60))
            indicator_generate(data, ma_of('ma5', si.price_std_lg, 5))
            indicator_generate(data, ma_of('ma20', si.price_std_lg, 20))
            indicator_generate(data, ma_of('ma60', si.price_std_lg, 60))
            indicator_generate(data, ma_of('ma300', si.price_std_lg, 300))
            indicator_generate(data, ma_of('exchange_ma5', si.exchange_rate, 5))
            indicator_generate(data, ma_of('exchange_ma20', si.exchange_rate, 20))
            indicator_generate(data, ma_of('exchange_ma60', si.exchange_rate, 60))
            indicator_generate(data, ma_of('exchange_ma300', si.exchange_rate, 300))
            indicator_generate(data, ma_of('rate_lg_ma5', si.rate_lg, 5))
            indicator_generate(data, ma_of('rate_lg_ma20', si.rate_lg, 20))
            indicator_generate(data, ma_of('rate_lg_ma60', si.rate_lg, 60))
            indicator_generate(data, ma_of('rate_lg_ma300', si.rate_lg, 300))
            available_code.append(code)
            available_data.append(data)
    print(f'stock data for training is prepared, {len(available_code)} stocks in total')
    time.sleep(0.1)

    evaler = neat_day_evaler_multi_process(available_data,
                                           ['price_std_lg', 'rate_lg', 'ma5', 'ma20', 'ma60', 'ma300',
                                            'exchange_ma5', 'exchange_ma20', 'exchange_ma60', 'exchange_ma300',
                                            'rate_lg_ma5', 'rate_lg_ma20', 'rate_lg_ma60', 'rate_lg_ma300'],
                                           multiprocessing.cpu_count())

    config_path = 'neat_config'
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    p = neat.Population(config)
    # p = neat.Checkpointer(1).restore_checkpoint('neat_train_log/basic_day_7_input_1106/neat-checkpoint-16')

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(5, filename_prefix='neat_train_log/basic_day_15_input_1119/epoch_'))

    # pe = neat.ParallelEvaluator(multiprocessing.cpu_count(), evaler)
    # winner = p.run(pe.evaluate, 300)
    winner = p.run(evaler, 300)

    print('\nBest genome:\n{!s}'.format(winner))
    print('\nOutput:')
    print(f'winner average profit: {evaler.average_profit(winner, config)}')

    node_names = {-1: '1', -2: 'price_std_lg', -3: 'rate_lg', -4: 'ma5', -5: 'ma20', -6: 'ma60', -7: 'exchange_rate',
                  0: 'ratio'}
    neat_visualize.draw_net(config, winner, True, node_names=node_names)
    neat_visualize.plot_stats(stats, ylog=False, view=True)
    neat_visualize.plot_species(stats, view=True)

    sql.close()


if __name__ == '__main__':
    run()
