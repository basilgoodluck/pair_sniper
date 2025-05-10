from telegram import Update
from telegram.ext import ContextTypes
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from keyboards import (
    get_interval_keyboard, get_period_keyboard, get_stocks_keyboard,
    get_crypto_keyboard, get_forex_keyboard, get_commodities_keyboard,
    get_indices_keyboard
)

async def interval_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    valid_intervals = ["1d", "1h", "30m", "15m", "5m", "1m"]
    period_options = {
        "1m": ["7d", "14d", "30d"],
        "5m": ["7d", "14d", "30d"],
        "15m": ["7d", "14d", "30d"],
        "30m": ["7d", "14d", "30d"],
        "1h": ["14d", "30d", "6mo"],
        "1d": ["30d", "6mo", "1y"]
    }
    asset_type_map = {
        "commodities": get_commodities_keyboard,
        "crypto": get_crypto_keyboard,
        "forex": get_forex_keyboard,
        "indices": get_indices_keyboard,
        "stocks": get_stocks_keyboard
    }

    if query.data.startswith("interval_"):
        interval = query.data.replace("interval_", "")
        if interval in valid_intervals:
            context.user_data["state"] = "select_period"
            context.user_data["interval"] = interval
            valid_periods = period_options.get(interval, ["30d", "6mo", "1y"])
            await query.edit_message_text(
                f"🤖 Choose a period for interval {interval}:",
                reply_markup=get_period_keyboard(valid_periods)
            )
    elif query.data == "back_to_period":
        asset_type = context.user_data.get("asset_type")
        if asset_type in asset_type_map:
            context.user_data["state"] = "select_ticker"
            await query.edit_message_text(
                f"🤖 Choose a ticker for {asset_type}:",
                reply_markup=asset_type_map[asset_type]()
            )