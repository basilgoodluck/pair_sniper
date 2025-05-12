from telegram import Update
from telegram.ext import ContextTypes
from keyboards import (
    get_stocks_keyboard, get_crypto_keyboard, get_forex_keyboard,
    get_commodities_keyboard, get_indices_keyboard, get_asset_type_keyboard,
    get_interval_keyboard
)

async def asset_type_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    ticker_def = {
        "commodities": get_commodities_keyboard,
        "forex": get_forex_keyboard,
        "indices": get_indices_keyboard,
        "stocks": get_stocks_keyboard
    }

    if query.data in ticker_def:
        context.user_data["state"] = "select_ticker"
        context.user_data["asset_type"] = query.data
        await query.edit_message_text(
            f"🤖 Choose a ticker for {query.data}:",
            reply_markup=ticker_def[query.data]()
        )

    elif any(query.data.startswith(f"{key}_") for key in ticker_def):
        asset_type = query.data.split('_')[0]  
        context.user_data["state"] = "select_ticker"
        context.user_data["asset_type"] = query.data
        await query.edit_message_text(
            f"🤖 Choose a ticker for {query.data.split('_')[-1]}:", 
            reply_markup=ticker_def[asset_type]() 
        )

    elif query.data == "back_to_asset_type":
        context.user_data["state"] = "select_asset_type"
        await query.edit_message_text(
            "🤖 Choose an asset type:", 
            reply_markup=get_asset_type_keyboard()
        )
