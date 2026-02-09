from dotenv import load_dotenv
import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from clients.dsco_order_client import DscoOrderClient
from loggers.product_logger import get_product_logger

def main():
    load_dotenv()

    logger = get_product_logger()
    logger.info("===== DSCO ORDER TEST START =====")

    order_client = DscoOrderClient()

    updated_since = "2024-01-01T00:00:00+00:00"  
    updated_until = "2026-01-02T18:58:05+00:00"

    try:
        orders_page = order_client.get_orders(
            orders_created_since=updated_since,
            until=updated_until,
        )

    except Exception as e:
        logger.error(f"Error fetching orders: {e}")

    logger.info("===== DSCO ORDER TEST END =====")

if __name__ == "__main__":
    main()
