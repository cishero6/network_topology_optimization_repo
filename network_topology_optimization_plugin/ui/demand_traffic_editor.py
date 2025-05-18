from qgis.core import QgsFeature, QgsGeometry, QgsVectorLayer, QgsProject
from qgis.gui import QgsMapToolEmitPoint
from qgis.PyQt import QtWidgets
import xml.etree.ElementTree as ET

class DemandTrafficEditor(QgsMapToolEmitPoint):
    def __init__(self, iface):
        super().__init__(iface.mapCanvas())
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.points = []  # две точки
        self.values = []  # пары (geom1, geom2, value)

    def run(self):
        self.canvas.setMapTool(self)
        return None, None

    def canvasReleaseEvent(self, e):
        point = self.toMapCoordinates(e.pos())
        self.points.append(point)
        if len(self.points) == 2:
            # Уточняем тип введенных данных
            choice, ok = QtWidgets.QInputDialog.getItem(
                self.iface.mainWindow(), 'Type', 'Select input type:', ['Demand', 'Traffic'], 0, False)
            if not ok:
                self.points = []
                self.canvas.unsetMapTool(self)
                return
            value, ok = QtWidgets.QInputDialog.getDouble(
                self.iface.mainWindow(), 'Value', f'Enter {choice} value:')
            if ok:
                self.values.append((self.points[0], self.points[1], choice.lower(), value))
                self.save_xml(choice.lower())
            self.points = []
            self.canvas.unsetMapTool(self)

    def save_xml(self, data_type):
        root = ET.Element('data')
        coords = [ET.SubElement(root, 'pair') for _ in self.values]
        for pair_elem, (p1, p2, dtype, val) in zip(coords, self.values):
            ET.SubElement(pair_elem, 'type').text = dtype
            ET.SubElement(pair_elem, 'x1').text = str(p1.x())
            ET.SubElement(pair_elem, 'y1').text = str(p1.y())
            ET.SubElement(pair_elem, 'x2').text = str(p2.x())
            ET.SubElement(pair_elem, 'y2').text = str(p2.y())
            ET.SubElement(pair_elem, 'value').text = str(val)
        path = f'manual_{data_type}.xml'
        tree = ET.ElementTree(root)
        tree.write(path, encoding='utf-8', xml_declaration=True)
        if data_type == 'demand':
            self.demand_path = path
            self.traffic_path = None
        else:
            self.traffic_path = path
            self.demand_path = None
        return self.demand_path, self.traffic_path