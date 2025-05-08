from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
import yfinance as yf
from dataclasses import dataclass
from typing import List

@dataclass
class MarketData:
    """Holds market data (OHLCV)."""
    df: pd.DataFrame

class DataProvider(ABC):
    """Interface for fetching market data."""
    @abstractmethod
    def fetch_data(self, symbol: str, period: str, interval: str) -> MarketData:
        pass

class Indicator(ABC):
    """Interface for technical indicators."""
    @abstractmethod
    def calculate(self, data: MarketData) -> pd.DataFrame:
        pass

class SignalGenerator(ABC):
    """Interface for generating trading signals."""
    @abstractmethod
    def generate_signals(self, data: MarketData, indicators: List[Indicator], symbol: str) -> pd.DataFrame:
        pass

class YahooFinanceDataProvider(DataProvider):
    """Fetches data from Yahoo Finance."""
    def fetch_data(self, symbol: str, period: str, interval: str) -> MarketData:
        try:
            df = yf.download(symbol, period=period, interval=interval, auto_adjust=False)
            if df.empty:
                raise ValueError(f"No data fetched for {symbol}")
            return MarketData(df)
        except Exception as e:
            raise RuntimeError(f"Failed to fetch data for {symbol}: {e}")

class RSIIndicator(Indicator):
    """Calculates 14-period RSI."""
    def calculate(self, data: MarketData) -> pd.DataFrame:
        df = data.df.copy()
        close = df['Close']
        delta = close.diff()
        
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        period = 14
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        rs = avg_gain / avg_loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        return df

class MACDIndicator(Indicator):
    """Calculates MACD (12, 26, 9)."""
    def calculate(self, data: MarketData) -> pd.DataFrame:
        df = data.df.copy()
        close = df['Close']
        
        ema_fast = close.ewm(span=12, adjust=False).mean()
        ema_slow = close.ewm(span=26, adjust=False).mean()
        
        df['MACD_12_26_9'] = ema_fast - ema_slow
        
        df['MACDs_12_26_9'] = df['MACD_12_26_9'].ewm(span=9, adjust=False).mean()
        
        return df

class OBVIndicator(Indicator):
    """Calculates On-Balance Volume (OBV)."""
    def calculate(self, data: MarketData) -> pd.DataFrame:
        df = data.df.copy()
        close = df['Close']
        volume = df['Volume']
        
        direction = np.sign(close.diff())
        df['OBV'] = (volume * direction).cumsum()
        
        return df

class RSIMACDSignalGenerator(SignalGenerator):
    """Generates signals based on RSI and MACD with confidence."""
    def generate_signals(self, data: MarketData, indicators: List[Indicator], symbol: str) -> pd.DataFrame:
        df = data.df.copy()
        
        for indicator in indicators:
            df = indicator.calculate(MarketData(df))
        
        df = df.dropna()
        
        df['Signal'] = 0
        df['Confidence'] = 0.0
        
        df['MACD_Cross'] = ((df['MACD_12_26_9'] > df['MACDs_12_26_9']) & 
                           (df['MACD_12_26_9'].shift(1) <= df['MACDs_12_26_9'].shift(1)))
        df['MACD_Cross_Sell'] = ((df['MACD_12_26_9'] < df['MACDs_12_26_9']) & 
                                (df['MACD_12_26_9'].shift(1) >= df['MACDs_12_26_9'].shift(1)))
        
        buy_mask = ((df['RSI'] < 40) & df['MACD_Cross'])
        sell_mask = ((df['RSI'] > 60) & df['MACD_Cross_Sell'])
        
        df.loc[buy_mask, 'Signal'] = 1
        df.loc[sell_mask, 'Signal'] = -1  
        
        epsilon = 1e-10 
        df.loc[buy_mask, 'Confidence'] = (
            ((40 - df['RSI']) / 40) + 
            ((df['MACD_12_26_9'] - df['MACDs_12_26_9']) / (df['MACD_12_26_9'].abs() + epsilon))
        ) / 2
        
        df.loc[sell_mask, 'Confidence'] = (
            ((df['RSI'] - 60) / 40) + 
            ((df['MACDs_12_26_9'] - df['MACD_12_26_9']) / (df['MACD_12_26_9'].abs() + epsilon))
        ) / 2
        
        df['Confidence'] = df['Confidence'].clip(0, 1)
        
        print("Debug Info:")
        print(f"RSI range: {df['RSI'].min():.2f} to {df['RSI'].max():.2f}")
        print(f"MACD Crossovers (Buy): {df['MACD_Cross'].sum()}")
        print(f"MACD Crossunders (Sell): {df['MACD_Cross_Sell'].sum()}")
        print(f"Buy Signals: {buy_mask.sum()}, Sell Signals: {sell_mask.sum()}")
        
        df['Ticker'] = symbol
        
        non_zero_signals = df[df['Signal'] != 0][['Signal', 'Confidence', 'Ticker']]
        if not non_zero_signals.empty:
            return non_zero_signals.iloc[-1:]
        return df[['Signal', 'Confidence', 'Ticker']].iloc[-1:]  

