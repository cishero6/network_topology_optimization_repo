from app.modules.demand_processing.demand_processing_module import DemandProcessingModule
import networkx as nx


class DefaultDemandProcessingModuleImpl(DemandProcessingModule):
    def process_demand(self, demand_coordinates, demand_matrix, graph: nx.MultiDiGraph):
        """Основной метод обработки данных спроса."""
        # Шаг 1: Сопоставление координат с узлами графа
        index_map = self._map_demand_to_graph(demand_coordinates, graph)
        
        # Шаг 2: Агрегация матрицы спроса
        new_matrix, node_ids = self._aggregate_demand_matrix(demand_matrix, index_map)
        
        # Шаг 3: Получение новых координат
        new_coordinates = [graph.nodes[node]['pos'] for node in node_ids]
        
        return new_coordinates, new_matrix