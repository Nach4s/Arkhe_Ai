import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")  # Значение по умолчанию
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
