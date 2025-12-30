"""
Скрипт для проверки webhook бота через Telegram API.

Использование:
    python check_webhook.py

Или с указанием токена:
    BOT_TOKEN=your_token python check_webhook.py
"""
import os
import sys
import asyncio
from aiogram import Bot

async def check_webhook():
    """Проверка информации о webhook."""
    bot_token = os.getenv("BOT_TOKEN")
    
    if not bot_token:
        print("❌ BOT_TOKEN не установлен!")
        print("Установите переменную окружения BOT_TOKEN или добавьте её в .env файл")
        sys.exit(1)
    
    bot = Bot(token=bot_token)
    
    try:
        print("🔍 Проверка webhook информации...")
        webhook_info = await bot.get_webhook_info()
        
        print("\n📊 Информация о webhook:")
        print(f"  URL: {webhook_info.url or 'Не установлен (используется polling)'}")
        print(f"  Pending updates: {webhook_info.pending_update_count}")
        print(f"  Last error date: {webhook_info.last_error_date or 'Нет ошибок'}")
        print(f"  Last error message: {webhook_info.last_error_message or 'Нет ошибок'}")
        print(f"  Max connections: {webhook_info.max_connections or 'Не установлено'}")
        print(f"  Allowed updates: {webhook_info.allowed_updates or 'Все'}")
        
        if webhook_info.url:
            print(f"\n✅ Webhook установлен: {webhook_info.url}")
            if webhook_info.pending_update_count > 0:
                print(f"⚠️  Внимание: {webhook_info.pending_update_count} обновлений в очереди")
            if webhook_info.last_error_date:
                print(f"❌ Последняя ошибка: {webhook_info.last_error_message}")
        else:
            print("\nℹ️  Webhook не установлен. Бот работает в режиме polling.")
        
    except Exception as e:
        print(f"❌ Ошибка при проверке webhook: {e}")
        sys.exit(1)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(check_webhook())

