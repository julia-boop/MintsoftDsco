from dotenv import load_dotenv
from datetime import datetime, timezone
import os
import json
load_dotenv()


def dsco_to_mintsoft(dsco_ts: str) -> str:
    dt = datetime.fromisoformat(dsco_ts)          
    dt_utc = dt.astimezone(timezone.utc)          
    return dt_utc.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z" 

def map_dsco_order(dsco_order):

    with open('./models/mintsoft_country_model.json', 'r') as file:
        countries = json.load(file)
        name_list = []
        country_id = None
        for c in countries:
            name_list.append(c.get("Name"))
            name_list.append(c.get("Code"))
            name_list.append(c.get("Code3"))
            if dsco_order.get("shipping", {}).get("country") in name_list:
                country_id = c.get("ID")
        print(country_id)

    with open('./models/mintsoft_currency_model.json', 'r') as file:
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
    for i in range(1, 3):
        addr_arr = dsco_order.get("shipping", {}).get("address", [])
        if addr_arr[i]:
            address_lines.append(addr_arr[i])
        else:
            address_lines.append("")

    order_items = []
    order_value = 0 
    for li in dsco_order.get("lineItems", []):
        item = {
            "SKU": li.get("sku"),
            "Quantity": li.get("quantity"),
            "Price": li.get("consumerPrice"),
            "Details": li.get("title"),
        }
        order_value += li.get("consumerPrice", 0) * li.get("quantity", 0)
        order_items.append(item)
    

    mintsoft_order = {
        "OrderItems": order_items,
        "OrderNumber": dsco_order.get("poNumber"),
        "ExternalOrderReference": dsco_order.get("dscoOrderId"),
        "Title": dsco_order.get("name"),
        "FirstName": dsco_order.get("shipping", {}).get("firstName"),
        "LastName": dsco_order.get("shipping", {}).get("lastName"),
        "Address1": address_lines[0],
        "Address2": address_lines[1],
        "Address3": address_lines[2],
        "Town": dsco_order.get("shipping", {}).get("city"),
        "County": dsco_order.get("shipping", {}).get("state"),
        "PostCode": dsco_order.get("shipping", {}).get("postal"),
        "Country": dsco_order.get("shipping", {}).get("country"),
        "CountryId": country_id, 
        "Email": dsco_order.get("billTo", {}).get("email"),
        "Phone": dsco_order.get("billTo", {}).get("phone"),
        "CourierService": dsco_order.get("shipCarrier") + " " + dsco_order.get("shipMethod"),
        "CourierServiceId": dsco_order.get("requestedShippingServiceLevelCodeUnmapped"),
        "Channel": "DSCO",
        "ChannelId": int(os.getenv("CHANNEL_ID", "50")),
        "Warehouse": "Warehouse",
        "WarehouseId": int(os.getenv("MINTSOFT_WAREHOUSE_ID", "0")),
        "Currency": dsco_order.get("currencyCode"),
        "CurrencyId": currency_id,
        "RequiredDespatchDate": dsco_to_mintsoft(dsco_order.get("shipByDate")), 
        "OrderValue": order_value,
        "ClientId": int(os.getenv("MINTSOFT_CLIENT_ID", "0")),
        "ConnectAction": {
            "ExtraDate1": datetime.now(timezone.utc).isoformat()
        }
    }
    return mintsoft_order