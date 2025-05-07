import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("TWELVE_DATA_TOKEN")

response = requests.get(f"https://api.twelvedata.com/time_series?symbol=EUR/USD&interval=1day&apikey={API_TOKEN}")

bulk = requests.get(f"https://api.exchangerate.host/latest?base=USD")

print(response.json())