from telegram import Update
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from bot.keyboards import get_main_keyboard
from bot.handlers.analysis_type import analysis_type_callback
from bot.handlers.ticker import ticker_callback
from bot.handlers.interval import interval_callback
from bot.handlers.period import period_callback
from bot.handlers.analysis import signal_callback
from bot.handlers.asset_type import asset_type_callback

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    username = user.username if user.username else "No username"
    user_id = user.id

    OWNER_ID = "1423681267" 

    try:
        await context.bot.send_message(
            chat_id=OWNER_ID,
            text=f"New user started the bot!\nUsername: @{username}\nUser ID: {user_id}"
        )
    except Exception as e:
        print(f"Failed to send message to owner: {str(e)}")

    context.user_data["state"] = "start"
    await update.message.reply_text(
        "🤖 Please choose an option you would like to go with.",
        reply_markup=get_main_keyboard()
    )

def register_handlers(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(analysis_type_callback, pattern="^(bulk_button|single_button|back_button)$"))
    app.add_handler(CallbackQueryHandler(asset_type_callback, pattern="^(commodities|crypto|forex|indices|stocks|back_to_asset_type)$"))
    app.add_handler(CallbackQueryHandler(ticker_callback, pattern="^(stock.*|crypto.*|forex.*|commodity.*|index.*|back_to_asset_type)$"))
    app.add_handler(CallbackQueryHandler(interval_callback, pattern="^interval_.*|back_to_period$"))
    app.add_handler(CallbackQueryHandler(period_callback, pattern="^period_.*|back_to_asset_type$"))
    app.add_handler(CallbackQueryHandler(signal_callback, pattern="^generate_signal$"))