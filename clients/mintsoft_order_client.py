import os
import requests
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
import json
import time 


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

    def create_order(self, payload):
        try:    
            url = f"{self.BASE_URL}/api/Order"
            headers = self.headers()
            headers["Content-Type"] = "application/json"
            print(payload, "Ok")
            print(type(payload))
            r = requests.put(
                url,
                headers=headers,
                
                data=json.dumps({"Order": payload,
                                 "ClientId": payload["ClientId"],
                                 "OrderNumber": payload["OrderNumber"],
                                 "OrderItems": payload["OrderItems"],
                                 "WarehouseId": payload["WarehouseId"],
                                 "Warehouse": payload["Warehouse"],
                                 "CurrencyId": payload["CurrencyId"],
                                 "CourierServiceId": payload["CourierServiceId"],
                                 "ChannelId": payload["ChannelId"],
                                 "Currency": payload["Currency"],
                                 "RequiredDespatchDate": payload["RequiredDespatchDate"],
                                 "FirstName": payload["FirstName"],
                                 "LastName": payload["LastName"],
                                 "Country": payload["Country"],
                                  "PostCode": payload["PostCode"],
                                  "ConnectAction": payload["ConnectAction"],
                                "Address1": payload["Address1"],
                                 "Town": payload["Town"],
                                  "Email": payload["Email"],
                                   "Phone": payload["Phone"],
                                     "ExternalOrderReference": payload["ExternalOrderReference"],
                                      #"CourierService": payload["CourierService"],
                                       "Channel": payload["Channel"],
                                         "OrderValue": payload["OrderValue"],
                                         "Address2": payload["Address2"],
                                    



                                 }),  # data= con dumps explícito, no json=
                timeout=30,
            )
            print("STATUS:", r.status_code)
            print("RESPONSE:", r.text)
        except Exception as e:
            print(e)
        return r.json()
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
    
    def order_con_order_number(self, orderNumber):
        url = f"{self.BASE_URL}/api/Order/Search"

        r = requests.get(
            url=url,
            headers=self.headers(),
            params= {
                "OrderNumber": orderNumber,
            },
            timeout=30
        )
        print(r.json())
        return r.json()
    


    def search_barcode(self, barcode):
        url = f"{self.BASE_URL}/api/Product/SearchBarcode"

        r = requests.get(
            url=url,
            headers=self.headers(),
            params= {
                "Barcode": barcode,
            },
            timeout=30
        )
        print(r.json())
        print(r.json().get("SKU"))
        return r.json().get("SKU")
    
    def map_order_item(self, order_vieja, cantidad_nueva):

        return {
            "SKU": order_vieja.get("SKU"),
            "ProductId": order_vieja.get("ProductId"),
            "Quantity": order_vieja.get("Quantity") - cantidad_nueva,
            "Details": order_vieja.get("Details"),
            "UnitPrice": order_vieja.get("Price", 0),
            "UnitPriceVat": order_vieja.get("Vat", 0),
            "Discount": order_vieja.get("Discount", 0),
            "OrderItemNameValues": [
                {
                    "Name": item.get("Name"),
                    "Value": item.get("Value")
                }
                for item in order_vieja.get("OrderItemNameValues", [])
            ],
            "WarehouseId": 3,      
            "RequestedSerialNo": "",
            "RequestedBatchNo": "",
            "RequestedBBEDate": ""
        }

    def liberar_items(self, order_items):
        info_stock = []
        id = 2395
        url_items = f"{self.BASE_URL}/api/Order/{id}/Items"
        time.sleep(6)
        items_dsco = requests.get(
            url=url_items,
            headers=self.headers(),
            params= {
                "id": id,
               
            },
            timeout=30
        )
        
        print(items_dsco)
        #id = 4078 #id se mantiene estatico, chequar acá si cambian 2395
        # search para buscar Id con SKU
        for item in order_items:
            hay_item = False
            cantidad_nueva = item.get("Quantity")
            sku = item.get("SKU")
            for item_dsco in items_dsco.json():
                #print("dsco item", item_dsco)
                if item_dsco.get("SKU") == sku:
                    ItemId = item_dsco.get("ID")
                    #print("itemId", ItemId) #esperar 74
                    if item_dsco.get("Quantity") - cantidad_nueva > 0:
                        hay_item = True
                        item_updated = self.map_order_item(item_dsco, cantidad_nueva)
                        #print("item", item )
                        # url_item = f"{self.BASE_URL}/api/Product/Search"
                        # r_item = requests.get(
                        #     url=url_item,
                        #     headers=self.headers(),
                        #     params= {
                        #         "Search": sku,
                        #     },
                        #     timeout=30
                        # )
                        #print("iditem", r_item.json())
                        
                        url = f"{self.BASE_URL}/api/Order/{id}/Items/{ItemId}"
                        #print(json.dumps(item_updated))
                        time.sleep(8)
                        r = requests.post(
                            url=url,
                            headers=self.headers(),
                            params= {
                                "id": id,
                                "ItemId": ItemId
                            },
                            data=json.dumps(item_updated),
                            timeout=30
                        )
                        print(r.json())
                        
                        break

                    if item_dsco.get("Quantity") - cantidad_nueva == 0:
                        
                        print("itemid", ItemId)
                        url = f"{self.BASE_URL}/api/Order/{id}/Items/{ItemId}"
                        time.sleep(8)
                        r = requests.delete(
                            url=url,
                            headers=self.headers(),
                            params= {
                                "id": id,
                                "ItemId": ItemId
                            },
                            timeout=30
                        )
                        
                        print(r.json())
                        if r.json().get("Message") !=  'Cannot remove the last item. Please cancel the order instead.':
                            hay_item = True
                        break
                        #eliminar item 
                    #else:
            info_stock.append((sku, hay_item))
        return info_stock