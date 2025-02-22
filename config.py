import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
NUTRIONIX_APP_ID = os.getenv("NUTRIONIX_APP_ID")
NUTRIONIX_API_KEY = os.getenv("NUTRIONIX_API_KEY")
OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")

if not TOKEN:
    raise ValueError("Переменная окружения BOT_TOKEN не установлена!")
if not NUTRIONIX_APP_ID:
    raise ValueError("Переменная окружения NUTRIONIX_APP_ID не установлена!")
if not NUTRIONIX_API_KEY:
    raise ValueError("Переменная окружения NUTRIONIX_API_KEY не установлена!")
if not OPENWEATHERMAP_API_KEY:
    raise ValueError("Переменная окружения OPENWEATHERMAP_API_KEY не установлена!")