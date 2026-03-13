import os 
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from dotenv import load_dotenv
from services.order_service import OrderSyncService
#from loggers.order_logger import get_logger



def main():
    load_dotenv()

    # logger = get_logger("order_main", "orders.log")
    # logger.info("===== ORDER SYNC STARTED =====")

    try:
        service = OrderSyncService()
        service.sync_all_orders()
        #Cambiar nivel de stock en DSCO
        print("===== ORDER SYNC FINISHED SUCCESSFULLY =====")

    except Exception:
        print("===== ORDER SYNC FAILED =====")
       
if __name__ == "__main__":
    main()
