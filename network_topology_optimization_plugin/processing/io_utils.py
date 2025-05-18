import os
import xml.etree.ElementTree as ET
from qgis.PyQt.QtCore import QStandardPaths

def read_matrix(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    coords = []
    matrix = []
    # Предполагаем структуру <data><coords><coord>...</coord></coords><matrix><row>...</row></matrix></data>
    for c in root.find('coords').findall('coord'):
        coords.append((float(c.get('x')), float(c.get('y'))))
    for r in root.find('matrix').findall('row'):
        row = [float(v) for v in r.text.strip().split()]
        matrix.append(row)
    return coords, matrix

def get_path(name:str):
    temp_dir = QStandardPaths.writableLocation(QStandardPaths.TempLocation)
    path = os.path.join(temp_dir, 'area.osm')
    return path