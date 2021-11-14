

class gene_node:
    def __init__(self, id: int, activation_func):
        self.id = id
        self.activation_func = activation_func


class gene_connection:
    def __init__(self, id: int, node_from: int, node_to: int, weight: float):
        self.id = id
        self.node_from = node_from
        self.node_to = node_to
        self.weight = weight


class chromosome:
    def __init__(self, gen_nodes: list, gen_cons: list, ins: int, outs: int):
        self.gen_nodes = gen_nodes
        self.gen_cons = gen_cons
        self.ins: ins
        self.outs: outs

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

    # def forward(self):

    # def crossover(self, other):


class genome:
    def __init__(self, chromosomes: list):
        self.chromosomes = chromosomes

    # def reproduce(self, other):


class neat:
    def __init__(self, dict):
        self.dict = {'mute_rate': 0.1}

        for name in dict:
            self.dict[name] = dict['name']







