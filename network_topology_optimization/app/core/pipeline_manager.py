import logging
from typing import Callable
from app.core.interfaces import IProcessManager, IStorageManager
from app.models import Query
from app.modules.demand_estimation.demand_estimation_module import DemandEstimationModule
from app.modules.demand_processing.demand_processing_module import DemandProcessingModule
from app.modules.graph_processing.graph_processing_module import GraphProcessingModule
from app.modules.topology_optimization.topology_optimization_module import TopologyOptimizationModule
from app.modules.utils.parse_utils import ParseUtils

logger = logging.getLogger(__name__)

class PipelineManager:
    def __init__(
            self,
            graph_processing: GraphProcessingModule,
            demand_processing: DemandProcessingModule,
            demand_estimation: DemandEstimationModule,
            topology_optimization: TopologyOptimizationModule,
            storage: IStorageManager
        ):
            self.graph_processing = graph_processing
            self.demand_processing = demand_processing
            self.demand_estimation = demand_estimation
            self.topology_optimization = topology_optimization
            self.storage = storage

    def optimize_topology_with_demand(self, query_id: str, file1_path: str, file2_path: str, set_status_callback: Callable[[str, str], bool]):
        """Основной метод обработки пайплайна"""
        try:
            # Обновляем статус перед началом обработки
            Query.objects.filter(query_id=query_id).update(status='PROCESSING')

            graph = ParseUtils.get_graph_xml(file1_path)
            raw_demand_coordinates, raw_demand_matrix = ParseUtils.get_demand_npz(file2_path)

            simplified_graph, crossroads_graph = self._process_stage(
                processor=self.graph_processing,
                input= [graph],
                stage_name='graph_processing'
            )
            
            demand_coordinates, demand_matrix = self._process_stage(
                processor = self.demand_processing,
                input = [raw_demand_coordinates, raw_demand_matrix, crossroads_graph],
                stage_name = 'demand_processing'
            )

            optimal_topology = self._process_stage(
                 processor = self.topology_optimization,
                 input = [crossroads_graph, demand_coordinates, demand_matrix],
                 stage_name = 'topology_optimization'
            )
            
            self.storage.save_final_result(content = optimal_topology,query_id = query_id)
            self.storage.cleanup_query_files(query_id = query_id)
            set_status_callback(query_id, 'COMPLETED')
            
        except Exception as e:
            logger.error(f"Pipeline processing failed: {str(e)}")
            set_status_callback(query_id, 'FAILED')
            raise

    def _process_stage(self, processor : IProcessManager, input: list, stage_name: str) -> str:
        """Обработка одного этапа"""
        try:
            output = processor.process(input)
            return output
            
        except Exception as e:
            logger.error(f"Stage {stage_name} failed: {str(e)}")
            raise