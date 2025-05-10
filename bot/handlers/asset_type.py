from telegram import Update
from telegram.ext import ContextTypes
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from keyboards import get_asset_type_keyboard, get_back_keyboard, get_main_keyboard

async def asset_type_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "bulk_button":
        # context.user_data["state"] = "select_asset_type"
        await query.edit_message_text(
            "🤖 This feature is not available", reply_markup=get_back_keyboard()
        )
    elif query.data == "single_button":
        context.user_data["state"] = "select_asset_type"
        await query.edit_message_text(
            "🤖 Choose an asset type:", reply_markup=get_asset_type_keyboard()
        )
    elif query.data == "back_button":
        context.user_data["state"] = "start"
        print("works also")
        await query.edit_message_text(
            "🤖 Please choose an option you would like to go with.",
            reply_markup=get_main_keyboard()
        )