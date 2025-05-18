import requests

class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')

    def post(self, endpoint, files=None, data=None):
        url = f"{self.base_url}{endpoint}"
        response = requests.post(url, files=files, data=data)
        response.raise_for_status()
        return response.json()

    def get(self, endpoint, params=None):
        url = f"{self.base_url}{endpoint}"
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def download_file(self, endpoint, params=None, dest_path="result.graphml"):
        url = f"{self.base_url}{endpoint}"
        response = requests.get(url, params=params)
        response.raise_for_status()
        with open(dest_path, 'wb') as f:
            f.write(response.content)
        return dest_path