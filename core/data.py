# import aiohttp
# import asyncio
# from .config import twelve_data_token
from indicators import OBVIndicator, YahooFinanceDataProvider, RSIIndicator, MACDIndicator, RSIMACDSignalGenerator

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

if __name__ == "__main__":
    provider = YahooFinanceDataProvider()
    symbol = "EURUSD=X"
    market_data = provider.fetch_data(symbol=symbol, period="3d", interval="5m")
    indicators = [RSIIndicator(), MACDIndicator(), OBVIndicator()]
    signal_generator = RSIMACDSignalGenerator()
    result = signal_generator.generate_signals(market_data, indicators, symbol)
    
    # print("\nMost recent signal:")
    print(result)