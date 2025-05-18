from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtCore import Qt
from qgis.core import QgsProject, QgsRectangle, QgsVectorLayer, QgsFeature, QgsGeometry
from qgis.gui import QgsMapToolEmitPoint
import os
import xml.etree.ElementTree as ET
import requests
import time

from ..api.client import APIClient
from ..api.status_checker import StatusChecker
from .area_selector import AreaSelector
from .bounds_dialog import BoundsDialog
from .demand_traffic_editor import DemandTrafficEditor
from .heatmap_renderer import HeatmapRenderer
from .server_config_dialog import ServerConfigDialog


# Диалог основного окна
FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ui_main_dialog.ui'))
class MainDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, iface):
        super(MainDialog, self).__init__(iface.mainWindow())
        self.iface = iface
        self.setupUi(self)
        # init vars
        self.osm_path = None
        self.demand_path = None
        self.traffic_path = None
        self.bounds = (0.9, 1.1)
        self.server_url = 'http://localhost:8000'
        self.api_client = APIClient(self.server_url)
        # Configure UI
        self.le_server_ip.setText(self.server_url)
        self.le_server_ip.editingFinished.connect(self.configure_server)
        # buttons
        self.btn_select_area.clicked.connect(self.select_area)
        self.btn_select_demand_file.clicked.connect(self.select_demand_file)
        self.btn_select_traffic_file.clicked.connect(self.select_traffic_file)
        self.btn_manual.clicked.connect(self.manual_input)
        self.btn_bounds.clicked.connect(self.set_bounds)
        self.btn_req_topo_d.clicked.connect(self.request_topology_demand)
        self.btn_req_topo_t.clicked.connect(self.request_topology_traffic)
        self.btn_req_traffic.clicked.connect(self.request_traffic)
        self.update_request_buttons()

    def configure_server(self):
        dlg = ServerConfigDialog(self.server_url)
        if dlg.exec_():
            self.server_url = dlg.get_url()
            self.api_client = APIClient(self.server_url)
        self.update_request_buttons()

    def update_request_buttons(self):
        self.btn_req_topo_d.setEnabled(bool(self.osm_path and self.demand_path))
        self.btn_req_topo_t.setEnabled(bool(self.osm_path and self.traffic_path))
        self.btn_req_traffic.setEnabled(bool(self.osm_path and self.demand_path))

    def select_area(self):
        # Создаем инструмент и передаём callback, чтобы получить путь после скачивания
        selector = AreaSelector(self.iface, on_finished=self.on_area_selected)
        selector.start()
        print('returned')
        tool = self.iface.mapCanvas().mapTool()
        print("After selector.start(), current tool is", tool.__class__.__name__)
    
    def on_area_selected(self, path):
        # Вызывается после того, как area.osm сохранён
        self.osm_path = path
        self.update_request_buttons()

    def select_demand_file(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Select Demand XML', filter='XML Files (*.xml)')
        if path:
            self.demand_path = path
        self.update_request_buttons()

    def select_traffic_file(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Select Traffic XML', filter='XML Files (*.xml)')
        if path:
            self.traffic_path = path
        self.update_request_buttons()

    def manual_input(self):
        editor = DemandTrafficEditor(self.iface)
        demand, traffic = editor.run()
        if demand:
            self.demand_path = demand
        if traffic:
            self.traffic_path = traffic
        self.update_request_buttons()

    def set_bounds(self):
        dlg = BoundsDialog(self)
        if dlg.exec_():
            self.bounds = (dlg.lower.value(), dlg.upper.value())
        self.update_request_buttons()

    def request_topology_demand(self):
        resp = self.api_client.post(
            '/request_topology_with_demand',
            files={'osm': open(self.osm_path, 'rb'), 'demand': open(self.demand_path, 'rb')},
            data={'lower_bound': self.bounds[0], 'upper_bound': self.bounds[1]}
        )
        qid = resp['queryId']
        StatusChecker(self.api_client).wait_for_completion(qid)
        path = self.api_client.download_file('/get', {'queryId': qid}, 'topo_demand.graphml')
        HeatmapRenderer.render(path)

    def request_topology_traffic(self):
        resp = self.api_client.post(
            '/request_topology_with_traffic',
            files={'osm': open(self.osm_path, 'rb'), 'traffic': open(self.traffic_path, 'rb')}
        )
        qid = resp['queryId']
        StatusChecker(self.api_client).wait_for_completion(qid)
        path = self.api_client.download_file('/get', {'queryId': qid}, 'topo_traffic.graphml')
        HeatmapRenderer.render(path)

    def request_traffic(self):
        resp = self.api_client.post(
            '/request_traffic',
            files={'osm': open(self.osm_path, 'rb'), 'demand': open(self.demand_path, 'rb')}
        )
        qid = resp['queryId']
        StatusChecker(self.api_client).wait_for_completion(qid)
        path = self.api_client.download_file('/get', {'queryId': qid}, 'traffic.graphml')
        HeatmapRenderer.render(path)
