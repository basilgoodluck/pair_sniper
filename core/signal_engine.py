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
            print(f"Fetching data for {symbol}, period: {period}, interval: {interval}, asset_type: {asset_type}")
            df = yf.download(symbol, period=period, interval=interval, auto_adjust=False)
            if df is None or df.empty or not isinstance(df, pd.DataFrame):
                print(f"No data fetched for {symbol}. Raw download result: {df}")
                raise ValueError(f"No data fetched for {symbol}. Period: {period}, Interval: {interval}")
            print(f"Raw data columns: {df.columns}, shape: {df.shape}")
            required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0) 
            if not all(col in df.columns for col in required_cols):
                print(f"Missing columns: {set(required_cols) - set(df.columns)}")
                raise ValueError(f"Missing required columns for {symbol}. Columns: {df.columns}")
            print(f"Data after fetch: {df.head()}")
            return MarketData(df)
        except Exception as e:
            print(f"Exception in fetch_data: {str(e)}")
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
        if len(df) < 10: 
            raise ValueError(f"Insufficient data after dropping NaNs for {symbol}. Only {len(df)} rows available.")

        df['Signal'] = 0
        df['Confidence'] = 0.0

        rsi_buy = self.config[asset_type]['rsi_buy']
        rsi_sell = self.config[asset_type]['rsi_sell']

        df['MACD_Cross'] = ((df['MACD'] > df['MACD_Signal']) & 
                           (df['MACD'].shift(1) <= df['MACD_Signal'].shift(1)))
        df['MACD_Cross_Sell'] = ((df['MACD'] < df['MACD_Signal']) & 
                                (df['MACD'].shift(1) >= df['MACD_Signal'].shift(1)))
        df['OBV_Trend'] = df['OBV'].diff() > 0
        df['RSI_Buy'] = df['RSI'].lt(rsi_buy)  
        df['RSI_Sell'] = df['RSI'].gt(rsi_sell)

        for col in ['MACD_Cross', 'MACD_Cross_Sell', 'OBV_Trend', 'RSI_Buy', 'RSI_Sell']:
            if df[col].isna().any():
                raise ValueError(f"NaN values found in {col} after computation for {symbol}")

        df['Buy_Score'] = (df['RSI_Buy'].astype(int) + 
                          df['MACD_Cross'].astype(int) + 
                          df['OBV_Trend'].astype(int))
        df['Sell_Score'] = (df['RSI_Sell'].astype(int) + 
                           df['MACD_Cross_Sell'].astype(int) + 
                           (~df['OBV_Trend']).astype(int))

        buy_mask = df['Buy_Score'] >= 2
        sell_mask = df['Sell_Score'] >= 2

        no_signal_mask = (~buy_mask) & (~sell_mask)
        df.loc[no_signal_mask & df['RSI_Buy'], 'Buy_Score'] = 1
        df.loc[no_signal_mask & df['RSI_Sell'], 'Sell_Score'] = 1
        buy_mask = df['Buy_Score'] >= 1
        sell_mask = df['Sell_Score'] >= 1

        df.loc[buy_mask, 'Signal'] = 1
        df.loc[sell_mask, 'Signal'] = -1

        epsilon = 1e-10
        df.loc[buy_mask, 'Confidence'] = (
            (df['Buy_Score'] / 3) *  
            (0.5 + 0.5 * ((rsi_buy - df['RSI']).clip(lower=0) / rsi_buy)) 
        )
        df.loc[sell_mask, 'Confidence'] = (
            (df['Sell_Score'] / 3) *  
            (0.5 + 0.5 * ((df['RSI'] - rsi_sell).clip(lower=0) / (100 - rsi_sell)))  
        )

        df['Confidence'] = df['Confidence'].clip(0, 1)
        df['Ticker'] = symbol

        df['Exit_Price'] = None
        for idx in df.index:
            if df.loc[idx, 'Signal'] == 1: 
                future_rows = df.loc[idx:].index
                exit_idx = future_rows[df.loc[future_rows, 'RSI'] > rsi_sell][:1]
                if not exit_idx.empty:
                    df.loc[idx, 'Exit_Price'] = df.loc[exit_idx[0], 'Close']
            elif df.loc[idx, 'Signal'] == -1: 
                future_rows = df.loc[idx:].index
                exit_idx = future_rows[df.loc[future_rows, 'RSI'] < rsi_buy][:1]
                if not exit_idx.empty:
                    df.loc[idx, 'Exit_Price'] = df.loc[exit_idx[0], 'Close']

        return df[['Signal', 'Confidence', 'Ticker', 'RSI', 'MACD', 'MACD_Signal', 'OBV', 'Close', 'Exit_Price']].iloc[-10:]