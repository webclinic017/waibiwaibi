import numpy as np
import copy
from typing import List, Optional

import turtle

from mak_neat_genome import gene_node, gene_connection, chromosome


def is_connection_from_ins(chrom: chromosome, gene_con: gene_connection):
    if gene_con.id < chrom.ins:
        return True
    else:
        return False


def is_connection_to_outs(chrom: chromosome, gene_con: gene_connection):
    if chrom.ins <= gene_con.id < chrom.ins + chrom.outs:
        return True
    else:
        return False


#
#
# def amount_connect_to(chrom: chromosome, id: int):
#     return len([x for x in chrom.gen_cons if x.node_to == id])
#
#
# def amount_connect_from(chrom: chromosome, id: int):
#     return len([x for x in chrom.gen_cons if x.node_from == id])

def nodes_connect_to(chrom: chromosome, id: int) -> List[gene_connection]:
    return [x for x in chrom.gen_cons if x.node_to == id]


def nodes_connect_from(chrom: chromosome, id: int) -> List[gene_connection]:
    return [x for x in chrom.gen_cons if x.node_from == id]


def ids_connect_to(chrom: chromosome, id: int) -> List[int]:
    return [x.node_from for x in chrom.gen_cons if x.node_to == id]


def ids_connect_from(chrom: chromosome, id: int) -> List[int]:
    return [x.node_to for x in chrom.gen_cons if x.node_from == id]


def gene_node_id(gen_list: List[gene_node], id: int) -> gene_node:
    for gen in gen_list:
        if gen.id == id:
            return gen
    return None


def gene_connect_id(gen_list: List[gene_connection], id: int) -> Optional[gene_connection]:
    for gen in gen_list:
        if gen.id == id:
            return gen
    return None


class neat_net:
    def __init__(self, chrom: chromosome):
        self.chrom = chrom
        self.net, self.matrixs, self.masks = self.neat_net_generate(self.chrom)

    @staticmethod
    def neat_net_generate(chrom: chromosome):
        rest_node = [x.id for x in chrom.gen_nodes]
        net = [list(range(0, chrom.ins)), list(range(chrom.ins, chrom.ins + chrom.outs))]
        level = 0

        while rest_node:
            level += 1
            net.insert(level, [])
            for node in rest_node:
                # -- if the node is only connected from the former nodes
                if set(sum(net[0:level], [])) >= set(ids_connect_to(chrom, node)):
                    rest_node.remove(node)
                    net[level].append(node)

        # -- delete the unused nodes to save place and time
        id_to_out = sum([ids_connect_to(chrom, x) for x in net[-1]], [])
        # id_to_out = [a for x in net[-1] for a in ids_connect_to(chrom, x)]
        for i in range(level, 0, -1):
            id_from_level = net[i]
            if set(id_to_out).isdisjoint(set(id_from_level)):
                del net[i]

        # -- matrixs should be 4-d, every node(2-d) need a 2-d matrix to compute
        # -- so a level need a 3-d matrix to compute, so the matrixs need to be 4-d for all dimension
        length = len(net)
        width = max([len(x) for x in net])
        matrixs = []
        masks = []

        for layer in range(1, len(net)):
            matrixs.append([])
            masks.append([])
            for node_id in net[layer]:
                matrixs[-1].append([])
                masks[-1].append([])
                # -- every node need a 2-d matrix
                nodes_to_curr = nodes_connect_to(chrom, node_id)
                for former_layer in net[:layer]:
                    matrixs[-1][-1].append([])
                    masks[-1][-1].append([])
                    for former_node_id in former_layer:
                        # -- get every value of the 2-d matrix
                        if former_node_id in ids_connect_to(chrom, node_id):
                            masks[-1][-1][-1].append(1)
                            for node_to_curr in nodes_to_curr:
                                if former_node_id == node_to_curr.node_from:
                                    matrixs[-1][-1][-1].append(node_to_curr.weight)
                                    break
                        else:
                            masks[-1][-1][-1].append(0)
                            matrixs[-1][-1][-1].append(0)

        return net, matrixs, masks

    def forward(self, x: List[float]):
        outputs = [x]
        for i in range(0, len(self.matrixs)):
            outputs.append([])
            for j in range(0, len(self.matrixs[i])):
                node_input = 0
                for fi in range(0, len(self.matrixs[i][j])):
                    for fj in range(0, len(self.matrixs[i][j][fi])):

                        node_input += self.matrixs[i][j][fi][fj] * outputs[fi][fj]

                node_id = self.net[i+1][j]
                node = gene_node_id(self.chrom.gen_nodes, node_id)
                node.update(node_input)
                outputs[-1].append(node.output)

        return outputs

    def __call__(self, x):
        self.outputs = self.forward(x)
        return self.outputs[-1]

    def __str__(self):
        res = ''
        for i in range(0, len(self.net)):
            if i == 0:
                res += 'ins:\t'
            elif i == len(self.net) - 1:
                res += '\nouts:\t'
            else:
                res += '\n\t\t'
            for node in self.net[i]:
                res += str(node) + '\t'
        return res


def test():
    # chrom1 = chromosome([gene_node(0, 1, 0), gene_node(1, 1, 0), gene_node(2, 1, 0)],
    #                     [gene_connection(0, 1, 2, 1), gene_connection(1, 0, 2, 1)],
    #                     1, 2)
    # a = ids_connect_to(chrom1, 2)
    # print(a)
    # id_to_out = sum([ids_connect_to(chrom1, x) for x in [1, 2]], [])
    # print(id_to_out)
    #
    # t = [ids_connect_to(chrom1, x) for x in [1, 2]]
    # print(t)
    # print([b for a in t for b in a])
    # print([b for a in [ids_connect_to(chrom1, x) for x in [1, 2]] for b in a])
    # print([a for x in [1, 2] for a in ids_connect_to(chrom1, x)])
    #
    # if set([0, 1]).isdisjoint(set([0, 2])):
    #     print(1)
    # else:
    #     print(0)
    #
    # la = [[1, 2], [1, 2], [1, 0]]
    # lb = [[1, 0], [2, 0, 1], [3, 2]]
    # aaa = np.array([np.array(x) for x in la])
    # print(la)
    # print(np.array(la))
    # # print(np.array(la) + np.array(lb))
    # print(aaa)

    from mak_neat_genome import generate_chromesome_basic

    net = neat_net(generate_chromesome_basic(4, 2))
    print(net)
    print(net.net)
    print(net.matrixs)
    print(net([1, 1, 1, 1]))





if __name__ == '__main__':
    test()
