from telegram.ext import ApplicationBuilder
from core.config import tg_bot_token
from bot.register_handlers import register_handlers

def main():
    app = ApplicationBuilder().token(tg_bot_token).build()
    register_handlers(app)
    app.run_polling()

if __name__ == "__main__":
    main()