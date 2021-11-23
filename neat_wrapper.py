
import os
import numpy as np
import time
import gzip
import random
import pickle

from neat.population import Population
from neat.reporting import BaseReporter

import mak_tools


class neat_logger(BaseReporter):
    def __init__(self, name, dir_base, save_interval=10, backup_time_interval=0.1 * 60 * 60,  suffix=''):
        self.logger = mak_tools.mak_logger(1, 1, 1, save_interval, backup_time_interval, name, dir_base)
        self.suffix = suffix

        self.last_generation_checkpoint = -1
        self.last_time_checkpoint = time.time()

        self.dir_stock_config = os.path.join(self.logger.dir_logger_base, 'stock_config.npy')

    def start_generation(self, generation):
        self.logger.print(f'epoch_{generation} start: ')

    def end_generation(self, config, population, species_set):
        self.logger.step_update()

        dir_save = self.logger.checkpoint(self.suffix)
        if dir_save:
            self.save_checkpoint(dir_save, config, population, species_set)

    def save_checkpoint(self, filename, config, population, species_set):
        with gzip.open(filename, 'w', compresslevel=5) as f:
            data = (self.logger.epoch, config, population, species_set, random.getstate())
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

    def load_population(self):
        generation, config, population, species_set, rndstate = load_population_from(self.logger.dir_backup_model)
        random.setstate(rndstate)

        return Population(config, (population, species_set, generation))

    def save_stock_config(self, config: dict):
        np.save(self.dir_stock_config, config)

    def load_stock_config(self):
        return np.load(self.dir_stock_config, allow_pickle=True).item()


def load_population_from(filename):
    """Resumes the simulation from a previous saved point."""
    with gzip.open(filename) as f:
        generation, config, population, species_set, rndstate = pickle.load(f)
        return [generation, config, population, species_set, rndstate]















