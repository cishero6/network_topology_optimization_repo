import numpy as np
import networkx as nx
import osmnx as ox

class ParseUtils:
    @staticmethod
    def get_graph_xml(xml:str) -> nx.MultiDiGraph:
        graph = ox.graph_from_xml(xml, simplify=False ,bidirectional=False)
        for node_id, node_data in graph.nodes(data=True):
            if ("lat" not in node_data) or ("lon" not in node_data):
                node_data["lat"] = node_data["y"]
                node_data["lon"] = node_data["x"]
        return graph

    @staticmethod
    def get_demand_npz(npz:str) -> np.ndarray:
        data = np.load(npz)
        return data['coordinates'],data['matrix']