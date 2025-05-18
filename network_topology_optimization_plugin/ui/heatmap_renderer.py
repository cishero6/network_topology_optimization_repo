from qgis.core import QgsVectorLayer, QgsGraduatedSymbolRenderer, QgsRendererRange, QgsSymbol, QgsProject
import xml.etree.ElementTree as ET

class HeatmapRenderer:
    @staticmethod
    def render(graphml_path):
        layer = QgsVectorLayer(graphml_path, 'Heatmap', 'ogr')
        if not layer.isValid():
            return
        # Парсим значения свойства 'value'
        values = [feat['value'] for feat in layer.getFeatures()]
        if not values:
            return
        min_v, max_v = min(values), max(values)
        ranges = []
        step = (max_v - min_v) / 5
        for i in range(5):
            lower = min_v + i*step
            upper = lower + step
            symbol = QgsSymbol.defaultSymbol(layer.geometryType())
            rng = QgsRendererRange(lower, upper, symbol, f"{lower:.2f} - {upper:.2f}")
            ranges.append(rng)
        renderer = QgsGraduatedSymbolRenderer('value', ranges)
        layer.setRenderer(renderer)
        QgsProject.instance().addMapLayer(layer)