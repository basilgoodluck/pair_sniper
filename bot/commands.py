from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
import sys
import os
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from .utils import pairs

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core.config import watch_list

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
    query= update.callback_query
    await query.answer()
    state = context.user_data.get("state", "start")
    if query.data == "bulk_button" and state == "start":
        context.user_data["state"] = "bulk_info"
        keyboard = [
            [InlineKeyboardButton("Crypto", callback_data='bulk_crypto')],
            [InlineKeyboardButton("Forex", callback_data='bulk_forex')]
            [InlineKeyboardButton("<< Go back", callback_data='back_start')]
        ]
        