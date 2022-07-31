import numpy as np
import random
from typing import List


# DONE: rewrite chromosome into net-like style, use levels in chromosome
# DONE: so mutation and reproduction code become easier
# TODO: then rewrite forward network generation in mak_neat_net


class gene_node:
    def __init__(self, id: int, activation_func: str, bias: float, level: int):
        self.id = id
        self.activation_func = activation_func
        self.bias = bias
        self.level = level

    def forward(self, x: float):
        return activation_func_list[self.activation_func](x + self.bias)


activation_func_list = {'null': lambda x: x,
                        'relu': lambda x: x if x > 0 else 0,
                        'leaky_relu': lambda x: x if x > 0 else 0.2 * x,
                        'sigmoid': lambda x: 1 / (1 + np.exp(-x)),
                        'tanh': lambda x: (1 - np.exp(-2 * x)) / (1 + np.exp(-2 * x))}


def random_activation_func_generate(settings: dict):
    return random.sample(settings['activation_options'], 1)[0]


def random_bias_generate(settings: dict):
    return min(max(random.normalvariate(settings['bias_init_mean'], settings['bias_init_std']), -10), 10)


def random_gene_node(settings: dict, id: int, level_max: int):
    return gene_node(id, random_activation_func_generate(settings), random_bias_generate(settings), random.randint(0, level_max))


class gene_conn:
    def __init__(self, id: int, node_from: int, node_to: int, weight: float, from_in: int = False, to_out: int = False):
        self.id = id
        self.node_from = node_from
        self.node_to = node_to
        self.weight = weight
        self.from_in = from_in
        self.to_out = to_out


def random_weight_generate(settings: dict):
    return


# -- maybe use a matrix as the mask of connections between nodes, can be useful for muting
# [[node [con...]]...]
class chromosome:
    def __init__(self, in_id_list, out_id_list):
        self.genes = [[x] for x in out_id_list]
        self.in_id_list = in_id_list
        self.out_id_list = out_id_list

    def level_amount(self):
        return len(self.genes)

    def node_amount(self):
        return sum([len(level) for level in self.genes[:-1]])

    def node_id_list(self):
        return [joint[0].id for level in self.genes[:-1] for joint in level]

    def conn_amount(self):
        return sum([len(joint[1]) for level in self.genes for joint in level])

    def conn_id_list(self):
        return [conn.id for level in self.genes for joint in level for conn in joint[1]]

    def add_node(self, node: gene_node, level):
        self.genes[level].append([node])

    def del_node(self, id: int):
        for level in self.genes[:-1]:
            for joint in level:
                if joint[0].id == id:
                    level.remove(joint)
                    return

    def add_cons(self, conn: gene_conn):
        if conn.to_out:
            for joint in self.genes[-1]:
                if joint[0] == conn.node_to:
                    joint.append(conn)
                    return
        else:
            for level in self.genes[:-1]:
                for joint in level:
                    if joint[0].id == conn.node_to:
                        joint.append(conn)
                        return

    def del_cons(self, id: int):
        for level in self.genes:
            for joint in level:
                for conn in joint[1:]:
                    if conn.id == id:
                        joint.remove(conn)
                        return

    # def forward(self):


def generate_chromesome_basic(ins: int, outs: int) -> chromosome:
    gene_nodes = []
    for i in range(0, outs):
        gene_nodes.append(gene_node(ins + i, 'relu', random.uniform(-1, 1)))
    gene_nodes.append(gene_node(ins + outs, 'relu', random.uniform(-1, 1)))
    gene_cons = []
    for i in range(0, ins):
        gene_cons.append(gene_conn(i, i, ins + outs, random.uniform(-1, 1)))
    for i in range(0, outs):
        gene_cons.append(gene_conn(ins + i, ins + outs, ins + i, random.uniform(-1, 1)))

    return chromosome(gene_nodes, gene_cons, ins, outs)


class genome:
    def __init__(self, chromosomes: List[chromosome], settings: dict):
        self.chromosomes = chromosomes
        self.fitness = None
        self.species = None
        self.probability = None
        self.gene_node_count = settings['gene_node_count']
        self.gene_conn_count = settings['gene_conn_count']

    def new_node_id(self):
        self.gene_node_count += 1
        return self.gene_node_count

    def new_conn_id(self):
        self.gene_conn_count += 1
        return self.gene_conn_count


    # def reproduce(self, other):







