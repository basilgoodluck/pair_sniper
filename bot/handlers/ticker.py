from telegram import Update
from telegram.ext import ContextTypes
from keyboards import (
    get_commodities_keyboard, get_crypto_keyboard, get_forex_keyboard,
    get_indices_keyboard, get_stocks_keyboard, get_interval_keyboard
)

async def ticker_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    asset_type = {
        "commodity": get_commodities_keyboard,
        "crypto": get_crypto_keyboard,
        "forex": get_forex_keyboard,
        "index": get_indices_keyboard,
        "stock": get_stocks_keyboard
    }

    for asset in asset_type:
        if query.data.startswith(f"{asset}_"):
            context.user_data["state"] = asset  
            context.user_data["ticker"] = query.data
            await query.edit_message_text(
                "Choose a period",
                reply_markup=get_interval_keyboard() 
            )
            break

    if query.data == "back_to_period":
        asset_type = context.user_data.get("asset_type")
        if asset_type in asset_type:
            context.user_data["state"] = "select_ticker"
            await query.edit_message_text(
                f"🤖 Choose a ticker for {asset_type}:",
                reply_markup=asset_type[asset_type]() 
            )
