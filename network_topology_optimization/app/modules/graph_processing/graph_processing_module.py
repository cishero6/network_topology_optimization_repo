from abc import ABC, abstractmethod
import networkx as nx

from app.core.interfaces import IProcessManager

class GraphProcessingModule(IProcessManager):
    def process(self, input):
        graph = input[0]

        preprocessed_graph = self.preprocess_graph(G = graph)

        simplified_graph = self.simplify_graph(G = preprocessed_graph, is_crossroad_simplification = False)
        crossroads_graph = self.simplify_graph(G = preprocessed_graph, is_crossroad_simplification = True)

        indexed_simplified_graph, indexed_crossroads_graph = self.reindex_graphs(simplified_graph, crossroads_graph)

        self.postprocess_graph(indexed_simplified_graph, indexed_crossroads_graph)

        return indexed_simplified_graph, indexed_crossroads_graph

    @abstractmethod
    def preprocess_graph(self, G) -> nx.MultiDiGraph: ...
    
    @abstractmethod
    def simplify_graph(self, G, is_crossroad_simplification) -> nx.MultiDiGraph: ...

    @abstractmethod
    def reindex_graphs(self, *graphs) -> nx.MultiDiGraph: ...

    @abstractmethod
    def postprocess_graph(self, *graphs) -> nx.MultiDiGraph: ...

    