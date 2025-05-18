from abc import abstractmethod
from app.core.interfaces import IProcessManager

class DemandEstimationModule(IProcessManager):
    def process(self, input):
        demand_estimation = self.get_demand(input)
        return demand_estimation
    
    @abstractmethod
    def get_demand(self, input): ...

    
