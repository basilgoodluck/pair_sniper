# import aiohttp
# import asyncio
# from .config import twelve_data_token
from .indicators import OBVIndicator, YahooFinanceDataProvider, RSIIndicator, MACDIndicator, RSIMACDSignalGenerator
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from bot.utils import plot_signals

# async def get_forex_data(interval, symbol): 
#     async with aiohttp.ClientSession() as session:
#         async with session.get(f"https://api.twelvedata.com/time_series?apikey={twelve_data_token}={interval}&symbol={symbol}") as response:
#             data = await response.json() 
#             return data
        
# async def get_crypto_data(interval, symbol):
#     async with aiohttp.ClientSession() as session:
#         async with session.get(f"https://api.twelvedata.com/time_series?apikey={twelve_data_token}={interval}&symbol={symbol}") as response:
#             data = await response.json()
#             return data

def generate_signal(period: str, interval: str):
    provider = YahooFinanceDataProvider()
    symbol = "EURUSD=X"
    market_data = provider.fetch_data(symbol=symbol, period=period, interval=interval)
    indicators = [RSIIndicator(), MACDIndicator(), OBVIndicator()]
    signal_generator = RSIMACDSignalGenerator()
    result = signal_generator.generate_signals(market_data, indicators, symbol)
    
    return result
