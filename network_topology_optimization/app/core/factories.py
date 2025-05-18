from app.core.interfaces import IStorageManager
from app.core.pipeline_manager import PipelineManager
from app.core.storage_manager import StorageManager
from app.modules.demand_estimation.demand_estimation_module import DemandEstimationModule
from app.modules.demand_processing.impl.default_demand_processing_module_impl import DefaultDemandProcessingModuleImpl
from app.modules.graph_processing.impl.default_graph_processing_module_impl import DefaultGraphProcessingModuleImpl
from app.modules.topology_optimization.topology_optimization_module import TopologyOptimizationModule

class ProdFactory:
    @staticmethod
    def create_storage() -> IStorageManager:
        return StorageManager()
    
    @staticmethod
    def create_pipeline_manager() -> PipelineManager:
        return PipelineManager(
            graph_processing = DefaultGraphProcessingModuleImpl(),
            demand_processing = DefaultDemandProcessingModuleImpl(),
            demand_estimation = DemandEstimationModule(),
            topology_optimization = TopologyOptimizationModule(),
            storage=ProdFactory.create_storage()
        )