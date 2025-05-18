import networkx as nx
import osmnx as ox
import numpy as np
from scipy.spatial import KDTree

from app.modules.graph_processing.graph_processing_module import GraphProcessingModule
from app.modules.utils.capacity_utils import CapacityUtils

class DefaultGraphProcessingModuleImpl(GraphProcessingModule):

    def preprocess_graph(self, G):
        """Дозаполняем атрибуты 'lanes' и 'maxspeed'."""
        for u, v, key in G.edges(keys=True):
            edge_data = G[u][v][key]
            
            # Устанавливаем lanes по умолчанию
            if 'lanes' not in edge_data:
                edge_data['lanes'] = 1
                
            # Устанавливаем maxspeed по умолчанию
            maxspeed = edge_data.get('maxspeed', 60)
            if not isinstance(maxspeed, (int, float)):
                edge_data['maxspeed'] = 60
                
            # Убедимся, что length присутствует
            if 'length' not in edge_data:
                edge_data['length'] = 0.0  # Или рассчитать по координатам
                
        return G

    def simplify_graph(self, G, is_junction_simplification):
        """Упрощение графа с учётом двунаправленных рёбер и суммирования length."""
        G = G.copy()
        
        while True:
            changed = False
            nodes_to_remove = []
            edges_to_add = []
            edges_to_remove = []
            
            for node in list(G.nodes()):
                # Удаляем тупиковые узлы
                if G.out_degree(node) == 0:
                    nodes_to_remove.append(node)
                    changed = True
                    continue
                    
                in_edges = list(G.in_edges(node, data=True, keys=True))
                out_edges = list(G.out_edges(node, data=True, keys=True))
                
                # Пропускаем узлы без входящих или исходящих рёбер
                if not in_edges or not out_edges:
                    continue
                    
                # Проверяем возможность полного объединения всех рёбер
                if len(in_edges) != len(out_edges):
                    continue
                    
                # Поиск совместимых пар рёбер
                used_out = [False] * len(out_edges)
                pairs = []
                
                for i, (u, _, k_in, d_in) in enumerate(in_edges):
                    found = False
                    for j, (_, v, k_out, d_out) in enumerate(out_edges):
                        if not used_out[j] and self._are_edges_compatible(d_in, d_out, is_junction_simplification):
                            pairs.append((i, j))
                            used_out[j] = True
                            found = True
                            break
                    if not found:
                        break
                        
                if len(pairs) != len(in_edges):
                    continue
                    
                # Формируем новые рёбра
                for i, j in pairs:
                    u, _, k_in, d_in = in_edges[i]
                    _, v, k_out, d_out = out_edges[j]
                    
                    # Суммируем длины
                    new_data = d_in.copy()
                    new_data['length'] = d_in.get('length', 0) + d_out.get('length', 0)
                    
                    edges_to_add.append((u, v, new_data))
                    edges_to_remove.extend([(u, node, k_in), (node, v, k_out)])
                    
                nodes_to_remove.append(node)
                changed = True
                
            # Применяем изменения
            for u, v, k in edges_to_remove:
                if G.has_edge(u, v, k):
                    G.remove_edge(u, v, k)
                    
            G.remove_nodes_from(nodes_to_remove)
            
            for u, v, data in edges_to_add:
                G.add_edge(u, v, **data)
                
            if not changed:
                break
                
        return G

    def reindex_graphs(self, *graphs):
        """Унифицированная переиндексация узлов по координатам."""
        coord_map = {}
        
        # Собираем все координаты
        for G in graphs:
            for node in G.nodes():
                pos = tuple(G.nodes[node]['pos'])
                if pos not in coord_map:
                    coord_map[pos] = len(coord_map)
                    
        # Переиндексируем графы
        results = []
        for G in graphs:
            mapping = {node: coord_map[tuple(G.nodes[node]['pos'])] for node in G.nodes()}
            new_G = nx.relabel_nodes(G, mapping, copy=True)
            results.append(new_G)
            
        return 
    
    def postprocess_graph(self, *graphs):
        for graph in graphs:
            CapacityUtils.assign_capacity(graph) 
        return 
    
    def _map_demand_to_graph(self, demand_coordinates, reindexed_graph):
        """Сопоставляет исходные координаты с узлами переиндексированного графа."""
        # Получаем координаты узлов графа
        graph_nodes = list(reindexed_graph.nodes(data='pos'))
        graph_coords = [pos for _, pos in graph_nodes]
        node_ids = [node for node, _ in graph_nodes]
        
        # Построение KDTree для быстрого поиска
        tree = KDTree(graph_coords)
        
        # Находим ближайшие узлы
        _, indices = tree.query(demand_coordinates)
        
        # Создаем отображение: исходный индекс -> ID узла в графе
        index_map = {i: node_ids[idx] for i, idx in enumerate(indices)}
        
        return index_map

    def _aggregate_demand_matrix(self,  original_matrix, index_map):
        """Агрегирует матрицу спроса по новым индексам."""
        unique_nodes = sorted(set(index_map.values()))
        node_to_idx = {node: idx for idx, node in enumerate(unique_nodes)}
        size = len(unique_nodes)
        
        new_matrix = np.zeros((size, size))
        
        for i in range(original_matrix.shape[0]):
            for j in range(original_matrix.shape[1]):
                src = node_to_idx[index_map[i]]
                dst = node_to_idx[index_map[j]]
                new_matrix[src, dst] += original_matrix[i, j]
        
        return new_matrix, [unique_nodes]
    
    def _are_edges_compatible(self, d1, d2, is_junction):
        """Проверяем совместимость рёбер для объединения."""
        if is_junction:
            # Для перекрестков: все атрибуты, кроме length, должны совпадать
            keys = set(d1.keys()) | set(d2.keys())
            return all(d1.get(k) == d2.get(k) for k in keys if k != 'length')
        else:
            # Для дорожного упрощения: совпадают lanes
            return d1.get('lanes', 1) == d2.get('lanes', 1)
