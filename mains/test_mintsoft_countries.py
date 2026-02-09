from dotenv import load_dotenv
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from clients.mintsoft_order_client import MintsoftOrderClient

def main():
    order_client = MintsoftOrderClient()
    try:
        countries = order_client.get_currencies()
        print(countries)

    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()