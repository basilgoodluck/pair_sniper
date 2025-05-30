import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from telegram import Update
from telegram.ext import ContextTypes
from core.data import generate_rsi_signal, generate_macd_signal, generate_obv_signal, generate_combined_signal
from core.signal_engine import YahooFinanceDataProvider, BinanceDataProvider, RSIIndicator, MACDIndicator, OBVIndicator, DynamicSignalGenerator
from keyboards import get_back_keyboard, get_period_keyboard
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

async def signal_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    ticker = context.user_data.get("ticker")  
    asset_type = context.user_data.get("asset_type")
    period = context.user_data.get("period")
    interval = context.user_data.get("interval")
    signal_type = context.user_data.get("signal_type", "combined")

    ticker_map = {
        "commodities": {"commodity_gold": "GC=F", "commodity_silver": "SI=F", "commodity_oil": "CL=F", "commodity_natgas": "NG=F"},
        "crypto": {"crypto_btc_usd": "BTC/USDT", "crypto_eth_usd": "ETH/USDT", "crypto_sol_usd": "SOL/USDT", "crypto_bnb_usd": "BNB/USDT", "crypto_ada_usd": "ADA/USDT"},
        "forex": {"forex_eur_usd": "EURUSD=X", "forex_gbp_usd": "GBPUSD=X", "forex_usd_jpy": "USDJPY=X", "forex_aud_usd": "AUDUSD=X", "forex_usd_chf": "USDCHF=X"},
        "indices": {"index_sp500": "^GSPC", "index_nasdaq": "^IXIC", "index_dowj": "^DJI", "index_ftse": "^FTSE", "index_nikkei": "^N225"},
        "stocks": {"stock_aapl": "AAPL", "stock_tsla": "TSLA", "stock_goog": "GOOG", "stock_msft": "MSFT", "stock_amzn": "AMZN"}
    }

    if query.data == "generate_signal":
        if not all([ticker, asset_type, period, interval]):
            await query.edit_message_text(
                "❌ Missing required data to generate signal.",
                reply_markup=get_back_keyboard()
            )
            return

        symbol = ticker_map.get(asset_type, {}).get(ticker)
        if not symbol:
            await query.edit_message_text(
                "❌ Invalid ticker or asset type.",
                reply_markup=get_back_keyboard()
            )
            return

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

            latest_signal = df.iloc[-1]
            direction = "Buy" if latest_signal['Signal'] == 1 else "Sell" if latest_signal['Signal'] == -1 else "Hold"
            entry_point = latest_signal['Close'] if latest_signal['Signal'] != 0 else None
            exit_point = latest_signal['Exit_Price'] if latest_signal['Signal'] != 0 else None
            confidence = min(latest_signal['Confidence'] * 100, 100) 

            img = Image.new('RGB', (400, 200), color=(0, 0, 0))
            d = ImageDraw.Draw(img)
            try:
                font = ImageFont.load_default()
            except:
                font = ImageFont.load_default()
            entry_text = f"${entry_point:.2f}" if entry_point is not None else "N/A"
            exit_text = f"${exit_point:.2f}" if exit_point is not None else "N/A"
            text = (
                f"Signal Report\n"
                f"Ticker: {ticker}\n"
                f"Asset Type: {asset_type}\n"
                f"Period: {period}\n"
                f"Interval: {interval}\n"
                f"Direction: {direction}\n"
                f"Entry Point: {entry_text}\n"
                f"Exit Point: {exit_text}\n"
                f"Confidence: {confidence:.1f}%"
            )
            d.multiline_text((10, 10), text, fill=(255, 255, 255), font=font)
            buf = BytesIO()
            img.save(buf, format='PNG')
            buf.seek(0)

            await query.message.reply_photo(
                photo=buf,
                caption="📊 Signal Generated",
            )
            await query.delete_message()
            buf.close()
        except Exception as e:
            await query.edit_message_text(
                f"❌ Error generating signal: {str(e)}",
                reply_markup=get_back_keyboard()
            )
    elif query.data == "back_button":
        context.user_data["state"] = "select_period"
        valid_periods = ["7d", "14d", "30d", "6mo", "1y"]
        await query.edit_message_text(
            "🤖 Choose a period:", reply_markup=get_period_keyboard(valid_periods)
        )