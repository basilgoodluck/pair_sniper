import os
from dotenv import load_dotenv

load_dotenv()

tg_bot_token= os.getenv("TG_BOT_TOKEN")
backend_url = os.getenv("BACKEND_URL") 