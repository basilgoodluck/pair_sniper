import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core.signal_engine import YahooFinanceDataProvider, BinanceDataProvider, RSIIndicator, MACDIndicator, OBVIndicator, DynamicSignalGenerator


from typing import Dict, Optional, List

def validate_period_interval(period: str, interval: str) -> bool:
    valid_combinations = {
        "1m": ["7d", "14d", "30d"],
        "5m": ["7d", "14d", "30d"],
        "15m": ["7d", "14d", "30d"],
        "30m": ["7d", "14d", "30d"],
        "1h": ["14d", "30d", "6mo"],
        "1d": ["30d", "6mo", "1y"]
    }
    return period in valid_combinations.get(interval, [])

def get_data_provider(asset_type: str, symbol: str) -> tuple:
    match asset_type:
        case 'crypto':
            provider = BinanceDataProvider()
            symbol = symbol.replace('-', '/')
        case 'stocks' | 'indices' | 'commodities' | 'forex':
            provider = YahooFinanceDataProvider()
        case _:
            raise ValueError(f"Unsupported asset type: {asset_type}")
    return provider, symbol

def get_default_config(asset_type: str) -> Dict:
    return {
        'stocks': {'rsi_buy': 40, 'rsi_sell': 60, 'period': '1y', 'interval': '1d'},
        'indices': {'rsi_buy': 40, 'rsi_sell': 60, 'period': '1y', 'interval': '1d'},
        'commodities': {'rsi_buy': 35, 'rsi_sell': 65, 'period': '6mo', 'interval': '1d'},
        'forex': {'rsi_buy': 30, 'rsi_sell': 70, 'period': '30d', 'interval': '1h'},
        'crypto': {'rsi_buy': 30, 'rsi_sell': 70, 'period': '30d', 'interval': '1h'}
    }

def generate_rsi_signal(
    symbol: str,
    asset_type: str,
    period: Optional[str] = None,
    interval: Optional[str] = None,
    rsi_period: int = 14,
    rsi_buy: Optional[float] = None,
    rsi_sell: Optional[float] = None
) -> Dict[str, any]:
    try:
        config = get_default_config(asset_type)
        if rsi_buy is not None:
            config[asset_type]['rsi_buy'] = rsi_buy
        if rsi_sell is not None:
            config[asset_type]['rsi_sell'] = rsi_sell
        selected_period = period if period is not None else config[asset_type]['period']
        selected_interval = interval if interval is not None else config[asset_type]['interval']

        if not validate_period_interval(selected_period, selected_interval):
            raise ValueError(f"Invalid period ({selected_period}) for interval ({selected_interval})")

        provider, symbol = get_data_provider(asset_type, symbol)
        market_data = provider.fetch_data(symbol, selected_period, selected_interval, asset_type)

        indicators = [RSIIndicator(period=rsi_period, buy_threshold=config[asset_type]['rsi_buy'], sell_threshold=config[asset_type]['rsi_sell'])]
        signal_generator = DynamicSignalGenerator(config)
        result = signal_generator.generate_signals(market_data, indicators, symbol, asset_type)

        return {'signal': result.to_dict(orient='records')[0]}
    except Exception as e:
        return {'error': f"Error generating RSI signal for {symbol} ({asset_type}): {str(e)}"}

def generate_macd_signal(
    symbol: str,
    asset_type: str,
    period: Optional[str] = None,
    interval: Optional[str] = None,
    macd_fast: int = 12,
    macd_slow: int = 26,
    macd_signal: int = 9
) -> Dict[str, any]:
    try:
        config = get_default_config(asset_type)
        selected_period = period if period is not None else config[asset_type]['period']
        selected_interval = interval if interval is not None else config[asset_type]['interval']

        if not validate_period_interval(selected_period, selected_interval):
            raise ValueError(f"Invalid period ({selected_period}) for interval ({selected_interval})")

        provider, symbol = get_data_provider(asset_type, symbol)
        market_data = provider.fetch_data(symbol, selected_period, selected_interval, asset_type)

        indicators = [MACDIndicator(fast=macd_fast, slow=macd_slow, signal=macd_signal)]
        signal_generator = DynamicSignalGenerator(config)
        result = signal_generator.generate_signals(market_data, indicators, symbol, asset_type)

        return {'signal': result.to_dict(orient='records')[0]}
    except Exception as e:
        return {'error': f"Error generating MACD signal for {symbol} ({asset_type}): {str(e)}"}

def generate_obv_signal(
    symbol: str,
    asset_type: str,
    period: Optional[str] = None,
    interval: Optional[str] = None
) -> Dict[str, any]:
    try:
        config = get_default_config(asset_type)
        selected_period = period if period is not None else config[asset_type]['period']
        selected_interval = interval if interval is not None else config[asset_type]['interval']

        if not validate_period_interval(selected_period, selected_interval):
            raise ValueError(f"Invalid period ({selected_period}) for interval ({selected_interval})")

        provider, symbol = get_data_provider(asset_type, symbol)
        market_data = provider.fetch_data(symbol, selected_period, selected_interval, asset_type)

        indicators = [OBVIndicator()]
        signal_generator = DynamicSignalGenerator(config)
        result = signal_generator.generate_signals(market_data, indicators, symbol, asset_type)

        return {'signal': result.to_dict(orient='records')[0]}
    except Exception as e:
        return {'error': f"Error generating OBV signal for {symbol} ({asset_type}): {str(e)}"}

def generate_combined_signal(
    symbol: str,
    asset_type: str,
    period: Optional[str] = None,
    interval: Optional[str] = None,
    rsi_period: int = 14,
    rsi_buy: Optional[float] = None,
    rsi_sell: Optional[float] = None,
    macd_fast: int = 12,
    macd_slow: int = 26,
    macd_signal: int = 9,
    indicators: Optional[List[str]] = None
) -> Dict[str, any]:
    try:
        config = get_default_config(asset_type)
        if rsi_buy is not None:
            config[asset_type]['rsi_buy'] = rsi_buy
        if rsi_sell is not None:
            config[asset_type]['rsi_sell'] = rsi_sell
        selected_period = period if period is not None else config[asset_type]['period']
        selected_interval = interval if interval is not None else config[asset_type]['interval']

        if not validate_period_interval(selected_period, selected_interval):
            raise ValueError(f"Invalid period ({selected_period}) for interval ({selected_interval})")

        provider, symbol = get_data_provider(asset_type, symbol)
        market_data = provider.fetch_data(symbol, selected_period, selected_interval, asset_type)

        if indicators is None:
            indicators = ['rsi', 'macd', 'obv']

        indicator_map = {
            'rsi': RSIIndicator(period=rsi_period, buy_threshold=config[asset_type]['rsi_buy'], sell_threshold=config[asset_type]['rsi_sell']),
            'macd': MACDIndicator(fast=macd_fast, slow=macd_slow, signal=macd_signal),
            'obv': OBVIndicator()
        }

        selected_indicators = [indicator_map[ind] for ind in indicators if ind in indicator_map]
        if not selected_indicators:
            raise ValueError("No valid indicators selected")

        signal_generator = DynamicSignalGenerator(config)
        result = signal_generator.generate_signals(market_data, selected_indicators, symbol, asset_type)

        return {'signal': result.to_dict(orient='records')[0]}
    except Exception as e:
        return {'error': f"Error generating combined signal for {symbol} ({asset_type}): {str(e)}"}