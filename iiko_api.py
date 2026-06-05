import os
import requests

class IikoClient:
    def __init__(self):
        self.api_key = os.getenv("IIKO_API_KEY")
        self.app_id = os.getenv("IIKO_APP_ID")
        self.client_secret = os.getenv("IIKO_CLIENT_SECRET")
        self.org_id = os.getenv("IIKO_ORG_ID")
        self.base_url = os.getenv("IIKO_BASE_URL", "https://api-ru.iiko.services")
        self.token = None

    def get_token(self):
        url = f"{self.base_url}/api/v2/access_token"

        response = requests.post(
            url,
            json={
                "apiKey": self.api_key,
                "appId": self.app_id,
                "clientSecret": self.client_secret
            },
            timeout=30
        )

        if response.status_code != 200:
            raise Exception(f"Ошибка получения токена: {response.status_code} {response.text}")

        self.token = response.json().get("token")
        return self.token

    def headers(self):
        if not self.token:
            self.get_token()

        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def post(self, endpoint, payload=None):
        url = f"{self.base_url}{endpoint}"

        response = requests.post(
            url,
            headers=self.headers(),
            json=payload or {},
            timeout=30
        )

        if response.status_code == 401:
            self.token = None
            response = requests.post(
                url,
                headers=self.headers(),
                json=payload or {},
                timeout=30
            )

        if response.status_code != 200:
            raise Exception(f"Ошибка iiko: {response.status_code} {response.text}")

        return response.json()

    def get_organizations(self):
        return self.post("/api/1/organizations")

    def get_nomenclature(self):
        return self.post("/api/1/nomenclature", {
            "organizationId": self.org_id
        })

    def get_stoplist(self):
        return self.post("/api/1/stop_lists", {
            "organizationIds": [self.org_id]
        })




