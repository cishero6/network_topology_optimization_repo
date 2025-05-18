from .client import APIClient
import time

class StatusChecker:
    def __init__(self, client):
        self.client = client

    def wait_for_completion(self, query_id, interval=5):
        while True:
            response = self.client.get("/check", params={'queryId': query_id})
            if response.get('status') == 'completed':
                return True
            time.sleep(interval)