import numpy as np
import random
from typing import List


class gene_node:
    def __init__(self, id: int, activation_func: str, bias: float):
        self.id = id
        self.activation_func = activation_func
        self.bias = bias
        self.output = 0

    def update(self, x):
        self.output = activation_func_list[self.activation_func](x + self.bias)


activation_func_list = {'null': lambda x: x,
                        'relu': lambda x: x if x > 0 else 0,
                        'sigmoid': lambda x: 1 / (1 + np.exp(-x))}


class gene_connection:
    def __init__(self, id: int, node_from: int, node_to: int, weight: float):
        self.id = id
        self.node_from = node_from
        self.node_to = node_to
        self.weight = weight


# -- maybe use a matrix as the mask of connections between nodes, can be useful for muting
class chromosome:
    def __init__(self, gen_nodes: List[gene_node], gen_cons: List[gene_connection], ins: int, outs: int):
        self.gen_nodes = gen_nodes
        self.gen_cons = gen_cons
        self.ins = ins
        self.outs = outs

    def add_nodes(self, g: gene_node):
        self.gen_nodes.append(g)

    def del_nodes(self, id: int):
        for i in range(0, len(self.gen_nodes)):
            if self.gen_nodes[i].id == id:
                self.gen_nodes.remove(self.gen_nodes[i])

    def add_cons(self, g: gene_node):
        self.gen_cons.append(g)

    def del_cons(self, id: int):
        for i in range(0, len(self.gen_cons)):
            if self.gen_cons[i].id == id:
                self.gen_cons.remove(self.gen_cons[i])

    def is_id_in(self, id):
        if 0 <= id < self.ins:
            return True
        else:
            return False

    def is_id_out(self, id):
        if self.ins <= id < self.ins + self.outs:
            return True
        else:
            return False

    # def forward(self):


def generate_chromesome_basic(ins: int, outs: int) -> chromosome:
    gene_nodes = []
    for i in range(0, outs):
        gene_nodes.append(gene_node(ins + i, 'relu', random.uniform(-1, 1)))
    gene_nodes.append(gene_node(ins + outs, 'relu', random.uniform(-1, 1)))
    gene_cons = []
    for i in range(0, ins):
        gene_cons.append(gene_connection(i, i, ins + outs, random.uniform(-1, 1)))
    for i in range(0, outs):
        gene_cons.append(gene_connection(ins + i, ins + outs, ins + i, random.uniform(-1, 1)))

    return chromosome(gene_nodes, gene_cons, ins, outs)


class genome:
    def __init__(self, chromosomes: List[chromosome]):
        self.chromosomes = chromosomes
        self.fitness = None
        self.species = None
        self.probability = None



    # def reproduce(self, other):







