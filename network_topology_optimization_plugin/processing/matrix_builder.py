from .io_utils import read_matrix

class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Edge:
    def __init__(self, a, b, weight):
        self.a = a
        self.b = b
        self.weight = weight


def build_from_xml(xml_path):
    coords, matrix = read_matrix(xml_path)
    nodes = [Node(x, y) for x, y in coords]
    edges = []
    n = len(nodes)
    for i in range(n):
        for j in range(n):
            w = matrix[i][j]
            if w > 0:
                edges.append(Edge(nodes[i], nodes[j], w))
    return nodes, edges