# @ last edit time 2022/1/30 16:38

from typing import List
from random import random
from copy import deepcopy

from mak_neat_genome import genome, chromosome


def reproduce(settings: dict, gen1: genome, gen2: genome):
    new_chrom_list = []
    for chrome_id in range(0, len(gen1.chromosomes)):
        ran = random()
        if ran < settings['reproduce_rate_select']:
            if ran < 0.5 * settings['reproduce_rate_select']:
                new_chrom_list.append(gen1.chromosomes[chrome_id])
            else:
                new_chrom_list.append(gen2.chromosomes[chrome_id])
        elif ran < settings['reproduce_rate_select'] + settings['reproduce_rate_combine']:
            new_chrom_list.append(chrome_combine(gen1.chromosomes[chrome_id], gen2.chromosomes[chrome_id]))

def chrome_combine(chrom1: chromosome, chrom2: chromosome):
    nodes =
    new_chrom = chromosome()
