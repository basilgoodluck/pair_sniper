from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import os
import sys
# from .utils import plot_signals

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core.config import watch_list, tg_bot_token
from core.data import generate_signal

async def show_pairs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pairs_list = pairs() 
    await update.message.reply_text("Pairs:\n" + "\n".join(pairs_list))
    pairs = list(watch_list.split(","))
    return pairs

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["state"] = "start"
    keyboard = [
        [InlineKeyboardButton("Bulk Analysis", callback_data="bulk_button")],
        [InlineKeyboardButton("Single Analysis", callback_data="single_button")]
    ]
    await update.message.reply_text("Please choose an option you would like to go with.", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    state = context.user_data.get("state", "start")
    if query.data == "single_button" and state == "start":
        context.user_data["state"] = "single_info"
        keyboard = [
            [InlineKeyboardButton("Commodities", callback_data='bulk_crypto')],
            [InlineKeyboardButton("Crypto", callback_data='bulk_forex')],
            [InlineKeyboardButton("Forex", callback_data='bulk_forex')],
            [InlineKeyboardButton("Indices", callback_data='bulk_forex')],
            [InlineKeyboardButton("Stocks", callback_data='bulk_forex')],
            [InlineKeyboardButton("Go back", callback_data='back_button')]
        ]
        info = generate_signal("3d", "1m")
        await query.edit_message_text(str(info), reply_markup=InlineKeyboardMarkup(keyboard))  
    elif query.data == "bulk_button" and state == "start":
        context.user_data["state"] = "bulk_info"
        keyboard = [
            [InlineKeyboardButton("Go back", callback_data='back_button')]
        ]
        await query.edit_message_text("This feature is not available yet.", reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data == "back_button" and state in ["single_info", "bulk_info"] :
        context.user_data["state"] = "start"
        keyboard = [
            [InlineKeyboardButton("Bulk Analysis", callback_data="bulk_button")],
            [InlineKeyboardButton("Single Analysis", callback_data="single_button")]
        ]
        await query.edit_message_text("Please choose an option you would like to go with.", reply_markup=InlineKeyboardMarkup(keyboard)) 
if __name__ == "__main__":
    app = ApplicationBuilder().token(tg_bot_token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.run_polling()