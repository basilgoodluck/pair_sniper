import aiohttp
import asyncio
from .config import twelve_data_token

async def get_forex_data(interval, symbol): 
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.twelvedata.com/time_series?apikey={twelve_data_token}={interval}&symbol={symbol}") as response:
            data = await response.json() 
            return data