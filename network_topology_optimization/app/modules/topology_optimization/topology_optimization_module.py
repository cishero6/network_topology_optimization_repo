from abc import abstractmethod
from app.core.interfaces import IProcessManager

class TopologyOptimizationModule(IProcessManager):
    def process(self, input):
        optimal_topology = self.get_topology(input)
        return optimal_topology
    
    @abstractmethod
    def get_topology(self, input): ...

    
