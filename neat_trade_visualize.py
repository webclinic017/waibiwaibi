
import os
import sqlite3
import trade_simulate
import neat
import neat_wrapper
import mak_stock_identifier as si

import neat_train
import get_stock
from indicators import ma_of


def run():
    config_path = 'neat_config'
    logger = neat_wrapper.neat_logger('basic_day_15_input_1123', 'neat_train_log')
    dir_sql = 'stock_data_ak.db'

    if not os.path.isfile(logger.logger.dir_backup_model):
        print('dont have existing model')
        exit(0)

    p = logger.load_population()
    neat_config = neat_wrapper.load_population_from(logger.logger.dir_backup_model)[1]
    stock_config = logger.load_stock_config()


    # gene_list = p.population
    # gene_keys = list(gene_list.keys())
    # for k in gene_keys:
    #     if not gene_list[k].fitness:
    #         gene_list[k].fitness = 0
    # sorted(gene_list, key=lambda gene: gene.fitness)

    gene_list = list(p.population.values())
    # print(gene_list[0])
    # print([x.fitness for x in gene_list])
    for gene in gene_list:
        if not gene.fitness:
            gene.fitness = 0
    gene_list = sorted(gene_list, key=lambda x: x.fitness, reverse=True)

    # print([x.fitness for x in gene_list])
    # print(gene_list[0])

    net = neat.nn.FeedForwardNetwork.create(gene_list[0], neat_config)
    net_strategy = neat_train.neat_day('neat', net.activate, stock_config[si.stock_info_list] + trade_simulate.indicator_batch_names(
                                               stock_config[si.indicator_list]))

    sql = sqlite3.connect(dir_sql)
    cursor = sql.cursor()
    # stock_list = ['000001']
    stock_list = get_stock.get_code_list_hs300(cursor, stock_config[si.start_date])
    stock_list = stock_list[:10]
    # stock_list.sort()
    available_code, available_data = trade_simulate.stock_data_prepare(cursor, stock_list, stock_config)
    for i in range(0, len(available_data)):
        data = available_data[i]

        trade_simulate.simulate_realistic(data, net_strategy)

        print(available_code[i])
        print(f'money rate / lg: {data[si.strategy][0][si.money][-1]} / {data[si.strategy][0][si.money_lg][-1]}, \
                commission cost lg: {sum(data[si.strategy][0][si.commission])}, \
                max drawdown rate: {data[si.strategy][0][si.max_drawdown]}')
        print()
        trade_simulate.plot_date(data)


if __name__ == '__main__':
    run()





