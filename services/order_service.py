import os
import sys
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, List
import traceback
from flask import json
#from loggers.order_logger import get_logger
from clients.dsco_order_client import DscoOrderClient
from clients.mintsoft_order_client import MintsoftOrderClient
from mappers.order_mapper import map_dsco_order

#map_dsco_order_update

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


class OrderSyncService:
    def __init__(self):
        print(sys.path)
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_json = os.path.join(directorio_actual, '..', 'state', 'state.json')
        with open(ruta_json, 'r') as file:   
            states = json.load(file)
        #self.logger = get_logger("order_service", "orders.log")
        self.dsco_client = DscoOrderClient()
        self.mintsoft_client = MintsoftOrderClient()
        self.last_order_sync = states.get("last_order_sync", None)
        self.last_product_sync = states.get("last_product_sync", None)

    def sync_all_orders(
        self
    ):
        #mintsoft_orders = MintsoftOrderClient()._get_orders()
        #Para que trae ordenes?
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_order = os.path.join(directorio_actual, '..', 'dsco_order_model.json')
        print("chequeo")
        try: 
            until = datetime.now(timezone.utc).isoformat() 
            dsco_orders_1 = self.dsco_client.get_orders(
                orders_created_since=self.last_order_sync,
                until=until,
            )
            #print(dsco_orders_1)
            # with open(ruta_order, 'w', encoding='utf-8') as f:   
            #     json.dump(dsco_orders_1, f, ensure_ascii=False, indent=2)
                
            print("inicio", dsco_orders_1,"fin")
        except Exception as e:
            print(e)
        #sys.exit()
        with open(ruta_order, 'r') as file:   
            dsco_orders = json.load(file)["orders"]
        #traer las ordenes de las cajas ahora
        print("ordenes", len(dsco_orders))
        #skipped = []
        updated = []
        created = []
        client = MintsoftOrderClient()
        try: 
            for dsco_order in dsco_orders:
                #mintsoft_order = next((order for order in mintsoft_orders if order["OrderNumber"] == dsco_order["poNumber"]), None)
                #chequear orden mintsoft con id 
                print(dsco_order["poNumber"])
                mintsoft_order = client.order_con_order_number(dsco_order["poNumber"])
                if not mintsoft_order:  #Cambiar logica, chequear directamente con order id, chequear si trae updated
                    print("cae acá", mintsoft_order)
                    created.append(dsco_order)
                #elif datetime.fromisoformat(dsco_order["dscoLastUpdate"]) > datetime.fromisoformat(mintsoft_order["ConnectAction"]["ExtraDate1"]):
                   # updated.append({"order":dsco_order, "mintsoft_id": mintsoft_order["Id"]})
                else:
                    updated.append({"order":dsco_order, "mintsoft_id": mintsoft_order[0]["ID"]})

            # self.logger.info(f"Orders to be created: {len(created)}")
            # self.logger.info(f"Orders to be updated: {len(updated)}")
            # self.logger.info(f"Orders to be skipped: {len(skipped)}")
            print("acaa")
            for order in created:
                mapped_order = map_dsco_order(order)
                print(mapped_order, "mapped")
                #Hasta acá, debugear funcion
                client.create_order(mapped_order)
                print("OK")
                self.dsco_client.formateo_ack(mapped_order)


            # for order in updated:  #Chequear diferencias para post api/Order/{id}
            #     mapped_order = map_dsco_order_update(order.get("order"))
            #     print("acaa") #Chequear update si necesito cambiar items
            #     #order_items = mapped_order.pop("OrderItems")
            #     self.mintsoft_client.update_order(mapped_order, order.get("mintsoft_id"))
            #     print("updated", order.get("mintsoft_id"))
            ruta_state = os.path.join(directorio_actual, '..', 'state','state.json')
            with open(ruta_state, 'r') as file:
                states = json.load(file)
            states["last_order_sync"] = until #ver funcionalidad de product
            with open(ruta_state, 'w') as file:
                json.dump(states, file)
        
        except Exception as e:
            print(e)
            traceback.print_exc()