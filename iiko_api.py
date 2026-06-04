import os
import requests

IIKO_API_KEY = os.getenv("IIKO_API_KEY")
IIKO_BASE_URL = os.getenv("IIKO_BASE_URL", "https://api-ru.iiko.services")

class IikoClient:
    def __init__(self):
        self.token = None

    def get_token(self):
        url = f"{IIKO_BASE_URL}/api/1/access_token"
        response = requests.post(url, json={"apiLogin": IIKO_API_KEY}, timeout=30)
        response.raise_for_status()
        self.token = response.json()["token"]
        return self.token

    def headers(self):
        if not self.token:
            self.get_token()
        return {"Authorization": f"Bearer {self.token}"}

    def get_organizations(self):
        url = f"{IIKO_BASE_URL}/api/v2/organizations"
        response = requests.post(url, headers=self.headers(), json={}, timeout=30)

        if response.status_code == 401:
            self.get_token()
            response = requests.post(url, headers=self.headers(), json={}, timeout=30)

        response.raise_for_status()
        return response.json()
