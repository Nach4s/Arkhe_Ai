import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")  # Значение по умолчанию
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Проверка обязательных переменных
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set")
