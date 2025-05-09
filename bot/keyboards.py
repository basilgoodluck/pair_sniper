from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def generate_keyboard(options):
    return InlineKeyboardMarkup([[InlineKeyboardButton(option, callback_data=option)] for option in options])

def get_main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Bulk Analysis", callback_data="bulk_button")],
        [InlineKeyboardButton("📈 Single Analysis", callback_data="single_button")]
    ])

def get_back_keyboard():
    return generate_keyboard(["🔙 Go back"])

def get_asset_type_keyboard():
    options = ["🛢️ Commodities", "₿ Crypto", "💱 Forex", "📉 Indices", "🏦 Stocks", "🔙 Go back"]
    callback_data = ['commodities', 'crypto', 'forex', 'indices', 'stocks', 'back_button']
    return InlineKeyboardMarkup([[InlineKeyboardButton(text, callback_data=cb)] for text, cb in zip(options, callback_data)])

def get_period_keyboard():
    return generate_keyboard(["1y", "6mo", "30d", "14d", "7d", "🔙 Go back"])

def get_interval_keyboard():
    return generate_keyboard(["1d", "1h", "30m", "15m", "5m", "1m", "🔙 Go back"])

def get_stocks_keyboard():
    return generate_keyboard(["AAPL", "TSLA", "GOOG", "MSFT", "AMZN", "🔙 Go back"])

def get_crypto_keyboard():
    return generate_keyboard(["BTC/USD", "ETH/USD", "SOL/USD", "BNB/USD", "ADA/USD", "🔙 Go back"])

def get_forex_keyboard():
    return generate_keyboard(["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CHF", "🔙 Go back"])

def get_commodities_keyboard():
    return generate_keyboard(["GOLD", "SILVER", "OIL", "NATGAS", "🔙 Go back"])

def get_indices_keyboard():
    return generate_keyboard(["SP500", "NASDAQ", "DOWJ", "FTSE", "NIKKEI", "🔙 Go back"])
