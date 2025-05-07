import os
from dotenv import load_dotenv

load_dotenv()

watch_list= os.getenv("WATCH_LIST")
tg_bot_token= os.getenv("TG_BOT_TOKEN")
twelve_data_token= os.getenv("TWELVE_DATA_TOKEN")