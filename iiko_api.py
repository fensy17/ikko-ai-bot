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

        if not self.api_key:
            raise ValueError("Не задан IIKO_API_KEY")
        if not self.app_id:
            raise ValueError("Не задан IIKO_APP_ID")
        if not self.client_secret:
            raise ValueError("Не задан IIKO_CLIENT_SECRET")
        if not self.org_id:
            raise ValueError("Не задан IIKO_ORG_ID")

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

        if response.status_code != 200:
            raise Exception(f"Ошибка iiko: {response.status_code} {response.text}")

        return response.json()

    # Организации
    def get_organizations(self):
        return self.post("/api/1/organizations")

    # Меню / номенклатура
    def get_nomenclature(self):
        if not self.org_id:
            raise Exception("Не задан IIKO_ORG_ID в Railway Variables")

    return self.post(
        "/api/1/nomenclature",
        {
            "organizationId": self.org_id,
            "startRevision": 0
        }
    )
    
    # Стоп-лист
    def get_stoplist(self):
        return self.post("/api/1/stop_lists", {
            "organizationIds": [self.org_id]
        })

    # Внешние меню
    def get_external_menus(self):
        return self.post("/api/2/menu", {
            "organizationIds": [self.org_id]
        })

    # Типы оплат
    def get_payment_types(self):
        return self.post("/api/1/payment_types", {
            "organizationIds": [self.org_id]
        })

    # Скидки и надбавки
    def get_discounts(self):
        return self.post("/api/1/discounts", {
            "organizationIds": [self.org_id]
        })

    # Типы заказов
    def get_order_types(self):
        return self.post("/api/1/deliveries/order_types", {
            "organizationIds": [self.org_id]
        })

    # Причины удаления
    def get_removal_types(self):
        return self.post("/api/1/removal_types", {
            "organizationIds": [self.org_id]
        })

    # Причины отмены
    def get_cancel_causes(self):
        return self.post("/api/1/cancel_causes", {
            "organizationIds": [self.org_id]
        })

    # Маркетинговые источники
    def get_marketing_sources(self):
        return self.post("/api/1/marketing_sources", {
            "organizationIds": [self.org_id]
        })

    # Терминальные группы
    def get_terminal_groups(self):
        return self.post("/api/1/terminal_groups", {
            "organizationIds": [self.org_id]
        })

    # Доставочные ограничения
    def get_delivery_restrictions(self):
        return self.post("/api/1/delivery_restrictions", {
            "organizationIds": [self.org_id]
        })

    # Поиск товара локально по номенклатуре
    def search_products(self, query):
        data = self.get_nomenclature()
        products = data.get("products", [])

        query = query.lower()

        return [
            product for product in products
            if query in product.get("name", "").lower()
        ]

    # Получить только товары
    def get_products_only(self):
        data = self.get_nomenclature()
        products = data.get("products", [])

        return [
            product for product in products
            if product.get("type") == "Product"
        ]
