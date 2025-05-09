from telegram import Update
from telegram.ext import ContextTypes
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from keyboards import get_interval_keyboard, get_back_keyboard

async def interval_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    valid_intervals = ["1d", "1h", "30m", "15m", "5m", "1m"]
    if query.data in valid_intervals:
        context.user_data["state"] = "select_interval"
        context.user_data["interval"] = query.data
        await query.edit_message_text(
            "🤖 Choose an interval:", reply_markup=get_interval_keyboard()
        )
    elif query.data == "back_button":
        context.user_data["state"] = "select_ticker"
        await query.edit_message_text(
            "🤖 Choose a ticker:", reply_markup=get_back_keyboard()
        )