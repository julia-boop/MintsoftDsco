import os
import requests
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
import json

load_dotenv()


class MintsoftOrderClient:
    BASE_URL = "https://api.mintsoft.co.uk"

    def __init__(self):
        self.username = os.getenv("MINTSOFT_USERNAME")
        self.password = os.getenv("MINTSOFT_PASSWORD")
        self.client_id = os.getenv("MINTSOFT_CLIENT_ID")
        self.channel_id = os.getenv("CHANNEL_ID")

        if not all([self.username, self.password, self.client_id]):
            raise RuntimeError(
                "Missing Mintsoft credentials "
                "(MINTSOFT_USERNAME / MINTSOFT_PASSWORD / MINTSOFT_CLIENT_ID)"
            )

        self.api_key = self._authenticate()

    def _authenticate(self) -> str:
        url = f"{self.BASE_URL}/api/Auth"

        payload = {
            "Username": self.username,
            "Password": self.password,
        }

        r = requests.post(url, json=payload, timeout=30)
        r.raise_for_status()

        return r.json()

    def headers(self) -> Dict[str, str]:
        return {
            "ms-apikey": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def create_order(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/api/Order"

        r = requests.put(
            url,
            headers=self.headers,
            json=payload,
            timeout=30,
        )
        r.raise_for_status()

        return r.json() if r.text else {}

    def update_order_items(
        self,
        order_id: int,
        item_id: int,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:

        url = f"{self.BASE_URL}/api/Order/{order_id}/Items/{item_id}"
        r = requests.post(
            url,
            headers=self.headers,
            json=payload,
            timeout=30,
        )
        r.raise_for_status()

        return r.json() if r.text else {}
    
    def create_order_items(
        self,
        order_id: int,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:

        url = f"{self.BASE_URL}/api/Order/{order_id}/Items"
        r = requests.put(
            url,
            headers=self.headers,
            json=payload,
            timeout=30,
        )
        r.raise_for_status()

        return r.json() if r.text else {}
    
    def delete_order_items(
        self,
        order_id: int,
        item_id: int,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:

        url = f"{self.BASE_URL}/api/Order/{order_id}/Items/{item_id}"
        r = requests.delete(
            url,
            headers=self.headers,
            json=payload,
            timeout=30,
        )
        r.raise_for_status()

        return r.json() if r.text else {}
    
    def get_order_items(
        self,
        order_id: int,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:

        url = f"{self.BASE_URL}/api/Order/{order_id}/Items"
        r = requests.get(
            url,
            headers=self.headers,
            json=payload,
            timeout=30,
        )
        r.raise_for_status()

        return r.json() if r.text else {}
    
    
    def update_order(
        self,
        order_id: int,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:

        url = f"{self.BASE_URL}/api/Order/{order_id}"

        r = requests.post(
            url,
            headers=self.headers,
            json=payload,
            timeout=30,
        )
        r.raise_for_status()

        return r.json() if r.text else {}

    def _get_orders(
        self
    ) -> List[Dict[str, Any]]:
        url = f"{self.BASE_URL}/api/Order/List"

        params = {
            "ClientId": self.client_id,
            "ChannelId": self.channel_id,
        }

        r = requests.get(
            url,
            headers=self.headers(),
            params=params,
            timeout=30,
        )
        r.raise_for_status()
        return r.json()

    def get_countries(self):
        url = f"{self.BASE_URL}/api/RefData/Countries"

        r = requests.get(
            url,
            headers=self.headers(),
            timeout=30,
        )

        r.raise_for_status()
        data = r.json()
        with open('mintsoft_country_model.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return data

    def get_currencies(self):
        url = f"{self.BASE_URL}/api/RefData/Currencies"

        r = requests.get(
            url,
            headers=self.headers(),
            timeout=30,
        )

        r.raise_for_status()
        data = r.json()
        with open('mintsoft_currency_model.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return data