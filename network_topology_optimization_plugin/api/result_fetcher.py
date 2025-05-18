from .client import APIClient

class ResultFetcher:
    def __init__(self, client):
        self.client = client

    def get_result(self, query_id, save_path):
        return self.client.download_file("/get", params={'queryId': query_id}, dest_path=save_path)