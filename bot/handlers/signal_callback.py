import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from telegram import Update
from telegram.ext import ContextTypes
from core.data import generate_rsi_signal, generate_macd_signal, generate_obv_signal, generate_combined_signal
from core.signal_engine import YahooFinanceDataProvider, BinanceDataProvider, RSIIndicator, MACDIndicator, OBVIndicator, DynamicSignalGenerator
from keyboards import get_back_keyboard, generate_keyboard 
from utils.helper import plot_signals

async def signal_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    ticker = context.user_data.get("ticker")
    asset_type = context.user_data.get("asset_type")
    period = context.user_data.get("period")
    interval = context.user_data.get("interval")
    signal_type = context.user_data.get("signal_type", "combined")

    ticker_map = {
        "commodities": {"GOLD": "GC=F", "SILVER": "SI=F", "OIL": "CL=F", "NATGAS": "NG=F"},
        "crypto": {"BTC/USDT": "BTC/USDT", "ETH/USDT": "ETH/USDT", "SOL/USDT": "SOL/USDT", "BNB/USDT": "BNB/USDT", "ADA/USDT": "ADA/USDT"},
        "forex": {"EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "USD/JPY": "USDJPY=X", "AUD/USD": "AUDUSD=X", "USD/CHF": "USDCHF=X"},
        "indices": {"SP500": "^GSPC", "NASDAQ": "^IXIC", "DOWJ": "^DJI", "FTSE": "^FTSE", "NIKKEI": "^N225"},
        "stocks": {"AAPL": "AAPL", "TSLA": "TSLA", "GOOG": "GOOG", "MSFT": "MSFT", "AMZN": "AMZN"}
    }

    if query.data in ticker_map.get(asset_type, {}):
        context.user_data["state"] = "generate_signal"
        context.user_data["ticker"] = query.data
        symbol = ticker_map[asset_type][query.data]
        try:
            if signal_type == "rsi":
                signal_data = generate_rsi_signal(symbol, asset_type, period, interval)
            elif signal_type == "macd":
                signal_data = generate_macd_signal(symbol, asset_type, period, interval)
            elif signal_type == "obv":
                signal_data = generate_obv_signal(symbol, asset_type, period, interval)
            else:
                signal_data = generate_combined_signal(symbol, asset_type, period, interval)

            if 'error' in signal_data:
                await query.edit_message_text(
                    f"❌ Error generating signal: {signal_data['error']}",
                    reply_markup=get_back_keyboard()
                )
                return

            provider = BinanceDataProvider() if asset_type == 'crypto' else YahooFinanceDataProvider()
            market_data = provider.fetch_data(symbol, period, interval, asset_type)
            df = market_data.df.copy()

            config = {
                asset_type: {'rsi_buy': 30 if asset_type in ['crypto', 'forex'] else 40 if asset_type in ['stocks', 'indices'] else 35,
                             'rsi_sell': 70 if asset_type in ['crypto', 'forex'] else 60 if asset_type in ['stocks', 'indices'] else 65}
            }
            indicators = []
            if signal_type == "rsi" or signal_type == "combined":
                indicators.append(RSIIndicator(period=14, buy_threshold=config[asset_type]['rsi_buy'], sell_threshold=config[asset_type]['rsi_sell']))
            if signal_type == "macd" or signal_type == "combined":
                indicators.append(MACDIndicator(fast=12, slow=26, signal=9))
            if signal_type == "obv" or signal_type == "combined":
                indicators.append(OBVIndicator())
            signal_generator = DynamicSignalGenerator(config)
            df = signal_generator.generate_signals(market_data, indicators, symbol, asset_type)

            plot_buf = plot_signals(df.tail(50))
            await query.message.reply_photo(
                photo=plot_buf,
                caption=f"📈 Latest Signal for {query.data} ({asset_type}, {period}, {interval}):\n{signal_data['signal']}",
                reply_markup=get_back_keyboard()
            )
            await query.delete_message()
            plot_buf.close()
        except Exception as e:
            await query.edit_message_text(
                f"❌ Error generating signal: {str(e)}",
                reply_markup=get_back_keyboard()
            )
    elif query.data == "back_button":
        context.user_data["state"] = "select_period"
        valid_periods = ["7d", "14d", "30d", "6mo", "1y"]
        await query.edit_message_text(
            "🤖 Choose a period:", reply_markup=generate_keyboard(valid_periods + ["🔙 Go back"])
        )