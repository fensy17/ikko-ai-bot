import os
import requests

class IikoClient:
    def __init__(self):
        self.api_key = os.getenv("IIKO_API_KEY")
        self.app_id = os.getenv("IIKO_APP_ID")
        self.client_secret = os.getenv("IIKO_CLIENT_SECRET")
        self.base_url = os.getenv("IIKO_BASE_URL", "https://api-ru.iiko.services")
        self.token = None

        if not self.api_key:
            raise ValueError("Не задан IIKO_API_KEY")
        if not self.app_id:
            raise ValueError("Не задан IIKO_APP_ID")
        if not self.client_secret:
            raise ValueError("Не задан IIKO_CLIENT_SECRET")

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
            raise Exception(
                f"Ошибка получения токена: {response.status_code} {response.text}"
            )

        data = response.json()
        self.token = data.get("token")

        if not self.token:
            raise Exception(f"Токен не найден в ответе: {data}")

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

        response.raise_for_status()
        return response.json()

    def get_organizations(self):
        return self.post("/api/1/organizations")
