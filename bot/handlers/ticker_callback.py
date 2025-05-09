from telegram import Update
from telegram.ext import ContextTypes
from keyboards import (
    get_stocks_keyboard, get_crypto_keyboard, get_forex_keyboard,
    get_commodities_keyboard, get_indices_keyboard, get_back_keyboard
)

async def ticker_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    asset_type_map = {
        "commodities": get_commodities_keyboard,
        "crypto": get_crypto_keyboard,
        "forex": get_forex_keyboard,
        "indices": get_indices_keyboard,
        "stocks": get_stocks_keyboard
    }

    if query.data in asset_type_map:
        context.user_data["state"] = "select_ticker"
        context.user_data["asset_type"] = query.data
        await query.edit_message_text(
            f"🤖 Choose a ticker for {query.data}:",
            reply_markup=asset_type_map[query.data]()
        )
    elif query.data == "back_button":
        context.user_data["state"] = "select_asset_type"
        await query.edit_message_text(
            "🤖 Choose an asset type:", reply_markup=get_back_keyboard()
        )