import os

import pytz
from dotenv import load_dotenv

load_dotenv()


BOT_TOKEN = os.getenv("BOT_TOKEN")
TIMEZONE = pytz.timezone("Europe/Moscow")
