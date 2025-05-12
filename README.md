# Forex Passed Pairs Indicator

## Overview
A Python-based Telegram bot that analyzes and generates trading signals for various asset types (forex, crypto, stocks, commodities, and indices) using technical indicators like RSI, MACD, and OBV. Originally designed to identify forex pairs with significant price movements ("passed pairs") based on a percentage change threshold, it now supports dynamic signal generation and user interaction via a Telegram interface. Deployed on Render for scalability and accessibility.

## Features
- **Multi-Asset Analysis**: Supports forex pairs, cryptocurrencies, stocks, commodities, and indices.
- **Technical Indicators**: Utilizes RSI, MACD, and OBV to generate buy/sell signals with confidence levels.
- **Dynamic Signal Generation**: Employs a voting system to dynamically produce signals based on indicator agreement.
- **User Interaction**: Telegram bot with a menu-driven interface for selecting asset types, tickers, intervals, periods, and signal generation.
- **Real-Time Data**: Fetches data from Yahoo Finance (for non-crypto) and Binance (for crypto) APIs.
- **Deployment**: Hosted on Render with webhook support for continuous operation.
- **Security**: Includes basic webhook validation to prevent unauthorized access.
- **User Notification**: Sends the bot owner the username and ID of users who start the bot.

## Requirements
- Python 3.8+
- Libraries: `python-telegram-bot==20.8`, `yfinance`, `ccxt`, `pandas`, `numpy`
- Environment variables: `tg_bot_token` (Telegram bot token), `backend_url` (webhook URL)

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/basilgoodluck/pair_sniper.git
   cd pair_sniper