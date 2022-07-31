# @ last edit time 2022/1/30 19:56

from typing import List

from mak_neat_genome import genome
from mak_neat_reproduce import reproduce


settings_default = {'population': 100,
                    'activation_options': ['relu', 'sigmoid'],
                    'bias_init_mean': 0,
                    'bias_init_std': 1,
                    'bias_max': 10,
                    'bias_min': -10,
                    'weight_init_mean': 0,
                    'weight_init_std': 1,
                    'weight_max': 10,
                    'weight_min': -10,

                    'mutate_rate_node_add': 0.01,
                    'mutate_rate_node_del': 0.01,
                    'mutate_rate_activation': 0.01,
                    'mutate_rate_connection_add': 0.02,
                    'mutate_rate_connection_del': 0.02,
                    'mutate_rate_bias_add': 0.05,
                    'mutate_rate_bias_mul': 0.05,
                    'mutate_rate_weight_add': 0.05,
                    'mutate_rate_weight_mul': 0.05,

                    'bias_mutate_add_mean': 0,
                    'bias_mutate_add_std': 1,
                    'bias_mutate_mul_mean': 1,
                    'bias_mutate_mul_std': 0.1,
                    'weight_mutate_add_mean': 0,
                    'weight_mutate_add_std': 1,
                    'weight_mutate_mul_mean': 1,
                    'weight_mutate_mul_std': 0.1,

                    'reproduce_rate_select': 0.5,
                    'reproduce_rate_combine': 0.5,
                    }


class neat:
    def __init__(self, settings: dict):
        self.settings = settings_default

        for name in settings:
            self.settings[name] = settings[name]

        self.state

    def step(self, genomes: List[genome], fitness_function):
        new_generation = []
        for genom in genomes:
            genom.fitness = (fitness_function(genom))

        genomes.sort(key=lambda g: g.fitness, reverse=True)

        # selection
        # reproduce
        # mutate

