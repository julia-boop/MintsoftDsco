import os
import sys
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, List

from flask import json
from loggers.order_logger import get_logger
from clients.dsco_order_client import DscoOrderClient
from clients.mintsoft_order_client import MintsoftOrderClient
from mappers.order_mapper import map_dsco_order

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


class OrderSyncService:
    def __init__(self):
        with open('./state/state.json', 'r') as file:
            states = json.load(file)
        self.logger = get_logger("order_service", "orders.log")
        self.dsco_client = DscoOrderClient()
        self.mintsoft_client = MintsoftOrderClient()
        self.last_order_sync = states.get("last_order_sync", None)
        self.last_product_sync = states.get("last_product_sync", None)

    def sync_all_orders(
        self
    ):
        mintsoft_orders = MintsoftOrderClient()._get_orders()

        until = datetime.now(timezone.utc).isoformat()
        dsco_orders = self.dsco_client.get_orders(
            orders_created_since=self.last_order_sync,
            until=until,
        )

        skipped = []
        updated = []
        created = []

        for dsco_order in dsco_orders:
            mintsoft_order = next((order for order in mintsoft_orders if order["OrderNumber"] == dsco_order["poNumber"]), None)
            if not mintsoft_order:
                created.append(dsco_order)
            elif datetime.fromisoformat(dsco_order["dscoLastUpdate"]) > datetime.fromisoformat(mintsoft_order["ConnectAction"]["ExtraDate1"]):
                updated.append({"order":dsco_order, "mintsoft_id": mintsoft_order["Id"]})
            else:
                skipped.append(dsco_order)

        self.logger.info(f"Orders to be created: {len(created)}")
        self.logger.info(f"Orders to be updated: {len(updated)}")
        self.logger.info(f"Orders to be skipped: {len(skipped)}")

        for order in created:
            mapped_order = map_dsco_order(order)
            self.mintsoft_client.create_order(mapped_order)

        for order in updated:
            mapped_order = map_dsco_order(order.get("order"))
            order_items = mapped_order.pop("OrderItems")
            self.mintsoft_client.update_order(mapped_order, order.get("mintsoft_id"))

        with open('./state/state.json', 'r') as file:
            states = json.load(file)
        states["last_order_sync"] = until
        with open('./state/state.json', 'w') as file:
            json.dump(states, file)