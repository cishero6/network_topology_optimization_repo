from .client import APIClient

class TrafficRequester:
    def __init__(self, client):
        self.client = client

    def request_traffic(self, osm_file, demand_file):
        files = {
            'osm': open(osm_file, 'rb'),
            'demand': open(demand_file, 'rb')
        }
        return self.client.post("/request_traffic", files=files)