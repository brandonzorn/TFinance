import os
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

load_dotenv()


BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_NAME = os.getenv("DATABASE_NAME")

TIMEZONE = ZoneInfo("Europe/Moscow")
