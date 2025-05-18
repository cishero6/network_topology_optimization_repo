from qgis.core import QgsRectangle, QgsProject, QgsVectorLayer, QgsFeature, QgsGeometry
from qgis.gui import QgsMapTool, QgisInterface
import requests

from ..processing.io_utils import get_path

class AreaSelector(QgsMapTool):
    def __init__(self, iface:QgisInterface, on_finished):
        """
        iface        – экземпляр QGIS Interface
        on_finished  – callback-функция, получает path к area.osm
        """
        super().__init__(iface.mapCanvas())
        self.iface = iface
        self.points = []
        self.on_finished = on_finished  # callback
        print('init')

    def start(self):
        # активируем наш инструмент
        self.iface.mapCanvas().setMapTool(self)
        print('start')


    def canvasReleaseEvent(self, e):
        print('releaseEvent')

        # собираем две точки
        self.points.append(self.toMapCoordinates(e.pos()))
        if len(self.points) == 2:
            # рисуем прямоугольник
            self._draw_rectangle()
            # скачиваем OSM
            path = self._fetch_osm()
            # вызываем callback из MainDialog
            self.on_finished(path)
            # сбрасываем инструмент
            self.iface.mapCanvas().unsetMapTool(self)

    def _draw_rectangle(self):
        rect = QgsRectangle(self.points[0], self.points[1])
        layer = QgsVectorLayer('Polygon?crs=EPSG:4326', 'Selection', 'memory')
        prov = layer.dataProvider()
        feat = QgsFeature()
        feat.setGeometry(QgsGeometry.fromRect(rect))
        prov.addFeatures([feat])
        layer.updateExtents()
        QgsProject.instance().addMapLayer(layer)
        self.bounds = rect

    def _fetch_osm(self):
        bbox = self.bounds
        overpass_url = "https://overpass-api.de/api/interpreter"

        query = f'''
            [out:xml];
            (
            way["highway"~"^(primary|secondary|tertiary|residential)$"]({bbox.yMinimum()},{bbox.xMinimum()},{bbox.yMaximum()},{bbox.xMaximum()});
            );
            (._;>;);
            out meta;
            '''
        response = requests.get(overpass_url, params={'data': query})

        path = get_path('area.osm')
        with open(path, 'w') as f:
            f.write(response.text)
        self.osm_path = path