from abc import ABC, abstractmethod
import networkx as nx

from app.core.interfaces import IProcessManager

class DemandProcessingModule(IProcessManager):
    def process(self, input):
        graph = input[0]
        demand_coordinates = input[1]
        demand_matrix = input[2]

        processed_demand_coordinates, processed_demand_matrix = self.process_demand(demand_coordinates = demand_coordinates, demand_matrix = demand_matrix, graph = graph)

        return processed_demand_coordinates, processed_demand_matrix

    @abstractmethod
    def process_demand(self, demand_coordinates, demand_matrix, graph): ...

    