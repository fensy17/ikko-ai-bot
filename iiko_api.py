import os
import requests


class IikoClient:

    def __init__(self):
        self.base_url = "https://api-ru.iiko.services"

        self.api_key = os.getenv("IIKO_API_KEY")
        self.org_id = os.getenv("IIKO_ORG_ID")

        self.token = None

    def get_token(self):
        if self.token:
            return self.token

        response = requests.post(
            f"{self.base_url}/api/1/access_token",
            json={
                "apiLogin": self.api_key
            },
            timeout=30
        )

        if response.status_code != 200:
            raise Exception(
                f"Ошибка получения токена: {response.status_code}\n{response.text}"
            )

        self.token = response.json()["token"]
        return self.token

    def headers(self):
        return {
            "Authorization": f"Bearer {self.get_token()}",
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
            raise Exception(
                f"Ошибка iiko: {response.status_code}\n{response.text}"
            )

        return response.json()

    # Организации
    def get_organizations(self):
        return self.post("/api/1/organizations")

    # Номенклатура
    def get_nomenclature(self):
        if not self.org_id:
            raise Exception(
                "Не задан IIKO_ORG_ID в Railway Variables"
            )

        return self.post(
            "/api/1/nomenclature",
            {
                "organizationId": self.org_id,
                "startRevision": 0
            }
        )

    # Стоп-лист
    def get_stoplist(self):
        if not self.org_id:
            raise Exception(
                "Не задан IIKO_ORG_ID в Railway Variables"
            )

        return self.post(
            "/api/1/stop_lists",
            {
                "organizationIds": [self.org_id]
            }
        )

    # Типы оплат
    def get_payment_types(self):
        if not self.org_id:
            raise Exception(
                "Не задан IIKO_ORG_ID в Railway Variables"
            )

        return self.post(
            "/api/1/payment_types",
            {
                "organizationIds": [self.org_id]
            }
        )

    # Склады
    def get_storages(self):
        if not self.org_id:
            raise Exception(
                "Не задан IIKO_ORG_ID в Railway Variables"
            )

        return self.post(
            "/api/1/warehouses",
            {
                "organizationId": self.org_id
            }
        )
