from telegram import Update
from telegram.ext import ContextTypes
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from keyboards import get_period_keyboard, get_asset_type_keyboard
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

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
    if query.data.startswith("period_"):
        period = query.data.replace("period_", "")
        if period in valid_periods:
            context.user_data["state"] = "generate_signal"
            context.user_data["period"] = period
            await query.edit_message_text(
                f"🤖 Selected period: {period} for interval {interval}\nGenerate signal now?",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Generate Signal", callback_data="generate_signal")],
                    [InlineKeyboardButton("🔙 Go back", callback_data="back_to_period")]
                ])
            )
    elif query.data == "back_to_asset_type":
        context.user_data["state"] = "select_asset_type"
        await query.edit_message_text(
            "🤖 Choose an asset type:", reply_markup=get_asset_type_keyboard()
        )