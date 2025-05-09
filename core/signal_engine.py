from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
import yfinance as yf
from dataclasses import dataclass
from typing import List, Dict
import ccxt

@dataclass
class MarketData:
    df: pd.DataFrame

class DataProvider(ABC):
    @abstractmethod
    def fetch_data(self, symbol: str, period: str, interval: str, asset_type: str) -> MarketData:
        pass

class Indicator(ABC):
    @abstractmethod
    def calculate(self, data: MarketData) -> pd.DataFrame:
        pass

class SignalGenerator(ABC):
    @abstractmethod
    def generate_signals(self, data: MarketData, indicators: List[Indicator], symbol: str, asset_type: str) -> pd.DataFrame:
        pass

class YahooFinanceDataProvider(DataProvider):
    def fetch_data(self, symbol: str, period: str, interval: str, asset_type: str) -> MarketData:
        try:
            df = yf.download(symbol, period=period, interval=interval, auto_adjust=False)
            if df is None or df.empty or not isinstance(df, pd.DataFrame):
                raise ValueError(f"No data fetched for {symbol}")
            required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
            if not all(col in df.columns for col in required_cols):
                raise ValueError(f"Missing required columns for {symbol}")
            return MarketData(df)
        except Exception as e:
            raise RuntimeError(f"Failed to fetch data for {symbol}: {str(e)}")

class BinanceDataProvider(DataProvider):
    def fetch_data(self, symbol: str, period: str, interval: str, asset_type: str) -> MarketData:
        try:
            exchange = ccxt.binance()
            timeframe = interval
            period_map = {
                '1mo': 30 * 24 * 60 * 60 * 1000,
                '1y': 365 * 24 * 60 * 60 * 1000,
                '6mo': 180 * 24 * 60 * 60 * 1000,
                '30d': 30 * 24 * 60 * 60 * 1000,
                '14d': 14 * 24 * 60 * 60 * 1000,
                '7d': 7 * 24 * 60 * 60 * 1000
            }
            since = exchange.milliseconds() - period_map.get(period, 30 * 24 * 60 * 60 * 1000)
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since)
            if ohlcv is None or not ohlcv:
                raise ValueError(f"No data fetched for {symbol}")
            df = pd.DataFrame(ohlcv, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
            df.set_index('Timestamp', inplace=True)
            if df.empty:
                raise ValueError(f"No data fetched for {symbol}")
            return MarketData(df)
        except Exception as e:
            raise RuntimeError(f"Failed to fetch data for {symbol}: {str(e)}")

class RSIIndicator(Indicator):
    def __init__(self, period: int, buy_threshold: float, sell_threshold: float):
        self.period = period
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold

    def calculate(self, data: MarketData) -> pd.DataFrame:
        df = data.df.copy()
        close = df['Close']
        delta = close.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=self.period).mean()
        avg_loss = loss.rolling(window=self.period).mean()
        rs = avg_gain / avg_loss
        df['RSI'] = 100 - (100 / (1 + rs))
        return df

class MACDIndicator(Indicator):
    def __init__(self, fast: int, slow: int, signal: int):
        self.fast = fast
        self.slow = slow
        self.signal = signal

    def calculate(self, data: MarketData) -> pd.DataFrame:
        df = data.df.copy()
        close = df['Close']
        ema_fast = close.ewm(span=self.fast, adjust=False).mean()
        ema_slow = close.ewm(span=self.slow, adjust=False).mean()
        df['MACD'] = ema_fast - ema_slow
        df['MACD_Signal'] = df['MACD'].ewm(span=self.signal, adjust=False).mean()
        return df

class OBVIndicator(Indicator):
    def calculate(self, data: MarketData) -> pd.DataFrame:
        df = data.df.copy()
        close = df['Close']
        volume = df['Volume']
        direction = np.sign(close.diff())
        df['OBV'] = (volume * direction).cumsum()
        return df

class DynamicSignalGenerator(SignalGenerator):
    def __init__(self, config: Dict):
        self.config = config

    def generate_signals(self, data: MarketData, indicators: List[Indicator], symbol: str, asset_type: str) -> pd.DataFrame:
        df = data.df.copy()
        for indicator in indicators:
            df = indicator.calculate(MarketData(df))
        df = df.dropna()

        df['Signal'] = 0
        df['Confidence'] = 0.0

        rsi_buy = self.config[asset_type]['rsi_buy']
        rsi_sell = self.config[asset_type]['rsi_sell']

        df['MACD_Cross'] = ((df['MACD'] > df['MACD_Signal']) & 
                           (df['MACD'].shift(1) <= df['MACD_Signal'].shift(1)))
        df['MACD_Cross_Sell'] = ((df['MACD'] < df['MACD_Signal']) & 
                                (df['MACD'].shift(1) >= df['MACD_Signal'].shift(1)))
        df['OBV_Trend'] = df['OBV'].diff() > 0

        buy_mask = ((df['RSI'] < rsi_buy) & df['MACD_Cross'] & df['OBV_Trend'])
        sell_mask = ((df['RSI'] > rsi_sell) & df['MACD_Cross_Sell'] & (~df['OBV_Trend']))

        df.loc[buy_mask, 'Signal'] = 1
        df.loc[sell_mask, 'Signal'] = -1

        epsilon = 1e-10
        df.loc[buy_mask, 'Confidence'] = (
            ((rsi_buy - df['RSI']) / rsi_buy) + 
            ((df['MACD'] - df['MACD_Signal']) / (df['MACD'].abs() + epsilon)) + 
            (df['OBV_Trend'].astype(float))
        ) / 3

        df.loc[sell_mask, 'Confidence'] = (
            ((df['RSI'] - rsi_sell) / (100 - rsi_sell)) + 
            ((df['MACD_Signal'] - df['MACD']) / (df['MACD'].abs() + epsilon)) + 
            ((~df['OBV_Trend']).astype(float))
        ) / 3

        df['Confidence'] = df['Confidence'].clip(0, 1)
        df['Ticker'] = symbol
        return df[['Signal', 'Confidence', 'Ticker', 'RSI', 'MACD', 'MACD_Signal', 'OBV', 'Close']].iloc[-1:]