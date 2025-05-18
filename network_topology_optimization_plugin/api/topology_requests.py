from .client import APIClient

class TopologyRequester:
    def __init__(self, client):
        self.client = client

    def request_with_demand(self, osm_file, demand_file, bounds):
        files = {
            'osm': open(osm_file, 'rb'),
            'demand': open(demand_file, 'rb')
        }
        data = {
            'lower_bound': bounds[0],
            'upper_bound': bounds[1]
        }
        return self.client.post("/request_topology_with_demand", files=files, data=data)

    def request_with_traffic(self, osm_file, traffic_file):
        files = {
            'osm': open(osm_file, 'rb'),
            'traffic': open(traffic_file, 'rb')
        }
        return self.client.post("/request_topology_with_traffic", files=files)