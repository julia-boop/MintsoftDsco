from dotenv import load_dotenv
from datetime import datetime, timezone
import os
import json
import traceback
from clients.mintsoft_order_client import MintsoftOrderClient
load_dotenv()


def dsco_to_mintsoft(dsco_ts: str) -> str:
    dt = datetime.fromisoformat(dsco_ts)          
    dt_utc = dt.astimezone(timezone.utc)          
    return dt_utc.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z" 

def map_dsco_order(dsco_order):
    try:
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_model_countries = os.path.join(directorio_actual, '..','models', 'mintsoft_country_model.json')
        with open(ruta_model_countries, 'r') as file:
            countries = json.load(file)
            #name_list = []
            country = None
            for c in countries:
                if c.get("Code") == dsco_order.get("shipping", {}).get("country"):
                    country = c.get("Name")
                    break
            print("country")

        ruta_model_currency = os.path.join(directorio_actual, '..','models', 'mintsoft_currency_model.json')
        with open(ruta_model_currency, 'r') as file:
            currencies = json.load(file)
            name_list = []
            currency_id = None
            for c in currencies:
                name_list.append(c.get("Name"))
                name_list.append(c.get("Code"))
                if dsco_order.get("currencyCode") in name_list:
                    currency_id = c.get("ID")
            print(currency_id)

        address_lines = []
        # for i in range(0):  #Chequear sacar range 
        #     addr_arr = dsco_order.get("shipping", {}).get("address", [])
        #     print("address", addr_arr)
        #     if addr_arr[i]:
        #         address_lines.append(addr_arr)
        #     else:
        #         address_lines.append("")
        addr_1 = dsco_order.get("shipping", {}).get("address1")

        

       # print("addr", addr_arr)
        address_lines.append(addr_1)
        #if address 2
       #address_lines.append("")
        #address_lines.append("")
        #Agregar otros address
        
        order_items = []
        order_value = 0 
        client = MintsoftOrderClient() #segmentar lógica por clie¡nte
        for li in dsco_order.get("lineItems", []):
            #sku = client.search_barcode(li.get("sku"))
            item = {
                "SKU": li.get("sku"),
                #Chequear como traer product id o si basta con SKU
                "Quantity": li.get("quantity"),
                "UnitPrice": li.get("expectedCost"),
                #"Details": li.get("dscoItemId"),
            }
            order_value += li.get("expectedCost", 0) * li.get("quantity", 0)
            order_items.append(item)
        
        #Order a model:
        #Entender consumerOrderNumber ("return invoices tied to the consumer order number")
        
        print("esto", dsco_order.get("shipping", {}).get("region"), dsco_order.get("shipping", {}).get("state") )
        mintsoft_order = {
            "OrderItems": order_items, #UnitPrice,UnitPriceVat,Discount,OrderItemNameValues, WarehouseId hardcodeado?, RequestedSerialNo,RequestedBatchNo, RequestedBBEDate
            #     "OrderItemNameValues": [ #parte de OrderItems
            #     {
            #       "Name": "string",
            #       "Value": "string"
            #     }
            #   ],
                #OrderNameValues [
            #     {
            #       "Name": "string",
            #       "Value": "string"
            #     }
            #   ]

            #Tags
            "ConnectAction": { #Ver si agregar más datos 
                "ExtraDate1": datetime.now(timezone.utc).isoformat()
            },
            "OrderNumber": dsco_order.get("poNumber"), 
            "ExternalOrderReference": dsco_order.get("dscoOrderId"),
            "Title": dsco_order.get("name"),
            #CompanyName
            "FirstName": dsco_order.get("shipping", {}).get("firstName"),
            "LastName": dsco_order.get("shipping", {}).get("lastName"),
            "Address1": address_lines[0],
            "Town": dsco_order.get("shipping", {}).get("city"),
            "County": dsco_order.get("shipping", {}).get("region"),
            "PostCode": dsco_order.get("shipping", {}).get("postal"),
            "Country": country,
            "Email": dsco_order.get("billTo", {}).get("email"),
            "Phone": dsco_order.get("billTo", {}).get("phone"),
            #Mobile
            #"CourierService": dsco_order.get("shipCarrier") + " " + dsco_order.get("shipMethod") + " - " + "Ecommerce", #Agregar ecommerce
            "CourierServiceId": 2555,  #chequear cual es el de shirty
            "Channel": "TEST_DSCO", #Cambiar a DSCO
            "ChannelId": 50,  #Cambiar a 5
            "Warehouse": "Warehouse", #Chequear
            "WarehouseId": int(os.getenv("MINTSOFT_WAREHOUSE_ID", "0")),
            "Currency": dsco_order.get("currencyCode"),
            "CurrencyId": currency_id,
            "RequiredDespatchDate": dsco_to_mintsoft(dsco_order.get("shipByDate")), 
            "OrderValue": order_value, 
            "ClientId": 9,  #Porque esta hardcodeado 9
            #   "Comments": "string",
            #   "DeliveryNotes": "string",
            #   "GiftMessages": "string",
            #   "VATNumber": "string",
            #   "EORINumber": "string",
            #   "PIDNumber": "string",
            #   "UKIMSNumber": "string",
            #   "RFCNumber": "string",
            #   "IOSSNumber": "string",
            #   "OrderValue": 0,
            #   "ShippingTotalExVat": 0,
            #   "ShippingTotalVat": 0,
            #   "DiscountTotalExVat": 0,
            #   "DiscountTotalVat": 0,
            #   "TotalVat": 0,
            #   "ClientId": 0,
            #   "NumberOfParcels": 0,
            #   "CashOnDelivery": {
            #     "Amount": 0,
            #     "CurrencyCode": "string"
            #   },
            #   "RecipientType": "string",
            #   "NationalAddressField": "string"
            # }
        }
        if dsco_order.get("shipping", {}).get("address2"):
            mintsoft_order["Address2"] = dsco_order.get("shipping", {}).get("address2")
        else:
            mintsoft_order["Address2"] = ""
        #mintsoft_order_json = json.dumps(mintsoft_order)
    except Exception as e:
        print(e)
        traceback.print_exec()
    return mintsoft_order, order_items


