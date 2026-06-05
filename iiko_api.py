import os
import requests

class IikoClient:
    def init(self):
self.api_key = os.getenv("IIKO_API_KEY")
self.base_url = os.getenv(
"IIKO_BASE_URL",
"https://api-ru.iiko.services"
)
self.token = None

def get_token(self):
    url = f"{self.base_url}/api/v2/access_token"

    response = requests.post(
        url,
        json={"apiKey": self.api_key},
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    self.token = data.get("token")

    if not self.token:
        raise Exception(f"Не удалось получить токен: {data}")

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

    response.raise_for_status()

    return response.json()

def get_organizations(self):
    return self.post("/api/1/organizations")




