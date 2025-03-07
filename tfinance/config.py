import os

import pytz
from dotenv import load_dotenv

load_dotenv()


BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_NAME = os.getenv("DATABASE_NAME")

TIMEZONE = pytz.timezone("Europe/Moscow")
