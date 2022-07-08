# @ last edit time 2022/1/30 16:37

from typing import List

from mak_neat_genome import chromosome, genome


def difference_chromosome(chrom1: chromosome, chrom2: chromosome):

    pass


def difference_genome(genom1: genome, genom2: genome):
    return 1.0


class species:
    def __init__(self, species_state, settings):
        if species_state:
            self.load_state(species_state)
        else:
            self.amount = 0
            self.active_species = {}

        self.settings = settings

    def load_state(self, state):
        pass

    def new_species(self, genom: genome):
        self.amount += 1
        self.active_species.update({self.amount: {'fitness': 0, 'amount': 0, 'typical': genom, 'best_fitness': None,
                                    'best_fitness_average': None, 'stagnate_epoch': 0, 'fitness_adjust_rate': 1}})
        return self.amount

    def counting_fitness(self, id, fitness):
        for sp in self.active_species:
            if sp['id'] == id:
                sp['fitness'] = (sp['amount'] * sp['fitness'] + fitness) / (sp['amount'] + 1)
                sp['amount'] += 1
                break

    def classify(self, genomes: List[genome]):
        for genom in genomes:
            relations = {}
            for s_id in self.active_species:
                relations.update({s_id: difference_genome(genom, self.active_species[s_id]['typical'])})
            min_diff = min(list(relations.values()))
            if min_diff <= self.settings['minimum_species_difference']:
                sp_id = list(relations.keys())[list(relations.values()).index(min_diff)]
                genom.species = sp_id
            else:
                genom.species = self.new_species(genom)





