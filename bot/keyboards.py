from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Bulk Analysis", callback_data="bulk_button")],
        [InlineKeyboardButton("📈 Single Analysis", callback_data="single_button")]
    ])

def get_back_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Go back", callback_data="back_button")]
    ])

def get_asset_type_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛢️ Commodities", callback_data="commodities")],
        [InlineKeyboardButton("₿ Crypto", callback_data="crypto")],
        [InlineKeyboardButton("💱 Forex", callback_data="forex")],
        [InlineKeyboardButton("📉 Indices", callback_data="indices")],
        [InlineKeyboardButton("🏦 Stocks", callback_data="stocks")],
        [InlineKeyboardButton("🔙 Go back", callback_data="back_button")]
    ])

def get_period_keyboard(valid_periods=None):
    if valid_periods is None:
        valid_periods = ["1y", "6mo", "30d", "14d", "7d"]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(period, callback_data=f"period_{period}")] for period in valid_periods
    ] + [[InlineKeyboardButton("🔙 Go back", callback_data="back_to_asset_type")]])

def get_interval_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("1d", callback_data="interval_1d")],
        [InlineKeyboardButton("1h", callback_data="interval_1h")],
        [InlineKeyboardButton("30m", callback_data="interval_30m")],
        [InlineKeyboardButton("15m", callback_data="interval_15m")],
        [InlineKeyboardButton("5m", callback_data="interval_5m")],
        [InlineKeyboardButton("1m", callback_data="interval_1m")],
        [InlineKeyboardButton("🔙 Go back", callback_data="back_to_period")]
    ])

def get_stocks_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("AAPL", callback_data="stock_aapl")],
        [InlineKeyboardButton("TSLA", callback_data="stock_tsla")],
        [InlineKeyboardButton("GOOG", callback_data="stock_goog")],
        [InlineKeyboardButton("MSFT", callback_data="stock_msft")],
        [InlineKeyboardButton("AMZN", callback_data="stock_amzn")],
        [InlineKeyboardButton("🔙 Go back", callback_data="back_to_asset_type")]
    ])

def get_crypto_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("BTC/USD", callback_data="crypto_btc_usd")],
        [InlineKeyboardButton("ETH/USD", callback_data="crypto_eth_usd")],
        [InlineKeyboardButton("SOL/USD", callback_data="crypto_sol_usd")],
        [InlineKeyboardButton("BNB/USD", callback_data="crypto_bnb_usd")],
        [InlineKeyboardButton("ADA/USD", callback_data="crypto_ada_usd")],
        [InlineKeyboardButton("🔙 Go back", callback_data="back_to_asset_type")]
    ])

def get_forex_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("EUR/USD", callback_data="forex_eur_usd")],
        [InlineKeyboardButton("GBP/USD", callback_data="forex_gbp_usd")],
        [InlineKeyboardButton("USD/JPY", callback_data="forex_usd_jpy")],
        [InlineKeyboardButton("AUD/USD", callback_data="forex_aud_usd")],
        [InlineKeyboardButton("USD/CHF", callback_data="forex_usd_chf")],
        [InlineKeyboardButton("🔙 Go back", callback_data="back_to_asset_type")]
    ])

def get_commodities_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("GOLD", callback_data="commodity_gold")],
        [InlineKeyboardButton("SILVER", callback_data="commodity_silver")],
        [InlineKeyboardButton("OIL", callback_data="commodity_oil")],
        [InlineKeyboardButton("NATGAS", callback_data="commodity_natgas")],
        [InlineKeyboardButton("🔙 Go back", callback_data="back_to_asset_type")]
    ])

def get_indices_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("SP500", callback_data="index_sp500")],
        [InlineKeyboardButton("NASDAQ", callback_data="index_nasdaq")],
        [InlineKeyboardButton("DOWJ", callback_data="index_dowj")],
        [InlineKeyboardButton("FTSE", callback_data="index_ftse")],
        [InlineKeyboardButton("NIKKEI", callback_data="index_nikkei")],
        [InlineKeyboardButton("🔙 Go back", callback_data="back_to_asset_type")]
    ])