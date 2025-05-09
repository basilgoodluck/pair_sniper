from telegram import Update
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from bot.keyboards import get_main_keyboard
from bot.handlers.asset_type import asset_type_callback
from bot.handlers.ticker_callback import ticker_callback
from bot.handlers.interval_callback import interval_callback
from bot.handlers.period_callback import period_callback
from bot.handlers.signal_callback import signal_callback

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["state"] = "start"
    await update.message.reply_text(
        "🤖 Please choose an option you would like to go with.",
        reply_markup=get_main_keyboard()
    )

def register_handlers(app):
    """Register command and callback handlers with the application."""
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(asset_type_callback, pattern="^(single_button|back_button)$"))
    app.add_handler(CallbackQueryHandler(ticker_callback, pattern="^(commodities|crypto|forex|indices|stocks|back_button)$"))
    app.add_handler(CallbackQueryHandler(interval_callback, pattern="^(1d|1h|30m|15m|5m|1m|back_button)$"))
    app.add_handler(CallbackQueryHandler(period_callback, pattern="^(7d|14d|30d|6mo|1y|back_button)$"))
    app.add_handler(CallbackQueryHandler(signal_callback, pattern="^(AAPL|TSLA|GOOG|MSFT|AMZN|BTC/USD|ETH/USD|SOL/USD|BNB/USD|ADA/USD|EUR/USD|GBP/USD|USD/JPY|AUD/USD|USD/CHF|GOLD|SILVER|OIL|NATGAS|SP500|NASDAQ|DOWJ|FTSE|NIKKEI|back_button)$"))