import os
import requests
from typing import Dict, Optional, List
from dotenv import load_dotenv
from urllib.parse import quote
import time
import json
import datetime

load_dotenv()


class DscoOrderClient:

    AUTH_URL = "https://api.dsco.io/api/v3/oauth2/token"
    BASE_URL = "https://api.dsco.io/api/v3"

    def __init__(self):
        self.client_id = os.getenv("DSCO_CLIENT_ID")
        self.client_secret = os.getenv("DSCO_CLIENT_SECRET")

        if not self.client_id or not self.client_secret:
            raise RuntimeError("Missing DSCO_CLIENT_ID or DSCO_CLIENT_SECRET")

        self._access_token: Optional[str] = None


    def _get_access_token(self) -> str:
        response = requests.post(
            self.AUTH_URL,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
            },
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
            timeout=30,
        )

        if not response.ok:
            raise RuntimeError(
                f"OAuth failed {response.status_code}: {response.text}"
            )

        data = response.json()
        self._access_token = data["access_token"]

        return self._access_token

    def _headers(self) -> Dict[str, str]:
        token = self._get_access_token()
        print(f"Access token: {token}") 
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def get_orders(
        self,
        *,
        orders_created_since: str,
        until: str,
    ) -> Dict:

        encoded_orders_created_since = quote(orders_created_since, safe=":")
        encoded_until = quote(until, safe=":")

        url = (
            f"{self.BASE_URL}/order/page"
            f"?ordersCreatedSince={encoded_orders_created_since}"
            f"&until={encoded_until}"
        )

        r = requests.get(
            url=url,
            headers=self._headers(),
            timeout=30,
        )

        r.raise_for_status()
        # data = r.json()
        # with open('dsco_order_model.json', 'w', encoding='utf-8') as f:
        #     json.dump(data, f, ensure_ascii=False, indent=4)
            
        return r.json()





    def formateo_ack(self, payload):
        url = (
            f"{self.BASE_URL}/order/acknowledge"
              )
         
        ack_payload = [
            {
                "id": payload["ExternalOrderReference"],
                "type": "DSCO_ORDER_ID",
                "supplierOrderNumber": payload["OrderNumber"],
                "poAcknowledgement": {
                    "messageControlNumber": payload["OrderNumber"], # O un UUID único
                    "originatingSystemTrxId": {
                        "trxDate": datetime.datetime.utcnow().isoformat() + "Z",
                        "text": "Mintsoft Order Created",
                        "systemOwner": "Mintsoft"
                    },
                    "scheduledShipDate": payload.get("RequiredDespatchDate"),
                    "lineItemAck": [
                        {
                            "poLineNumber": str(item.get("LineNumber", index + 1)),
                            "quantityOpen": str(item["Quantity"]),
                            "action": [
                                {
                                    "quantity": str(item["Quantity"]),
                                    "accept": "true", # Confirmamos que aceptamos el item
                                    "vendorSKU": item["SKU"]
                                }
                            ]
                        } for index, item in enumerate(payload["OrderItems"])
                    ],
                    "ackType": "entire_po" # Indica que estamos respondiendo por toda la orden
                }
            }
        ]
        r = requests.post(url, headers=self._headers(), json=ack_payload)
        print(r.json())
        return #r.json()