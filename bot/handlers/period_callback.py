from telegram import Update
from telegram.ext import ContextTypes
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from keyboards import generate_keyboard, get_back_keyboard, get_interval_keyboard

async def period_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    interval = context.user_data.get("interval")
    period_options = {
        "1m": ["7d", "14d", "30d"],
        "5m": ["7d", "14d", "30d"],
        "15m": ["7d", "14d", "30d"],
        "30m": ["7d", "14d", "30d"],
        "1h": ["14d", "30d", "6mo"],
        "1d": ["30d", "6mo", "1y"]
    }

    valid_periods = period_options.get(interval, ["30d", "6mo", "1y"])
    if query.data in valid_periods:
        context.user_data["state"] = "select_period"
        context.user_data["period"] = query.data
        await query.edit_message_text(
            f"🤖 Choose a period for {interval}:",
            reply_markup=generate_keyboard(valid_periods + ["🔙 Go back"])
        )
    elif query.data == "back_button":
        context.user_data["state"] = "select_interval"
        await query.edit_message_text(
            "🤖 Choose an interval:", reply_markup=get_interval_keyboard()
        )