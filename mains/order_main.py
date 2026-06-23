import os 
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from dotenv import load_dotenv
from services.order_service import OrderSyncService



def main():
    load_dotenv()


    try:
        service = OrderSyncService()
        service.sync_all_orders()


    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()
