import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
CALORIES_TOKEN = os.getenv("CALORIES_BURNED_TOKEN")

if not TOKEN:
    raise ValueError("Переменная окружения BOT_TOKEN не установлена!")
if not CALORIES_TOKEN:
    raise ValueError("Переменная окружения CALORIES_TOKEN не установлена!")