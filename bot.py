import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp import SimpleRequestHandler, setup_application
from aiohttp import web

from handlers import start, upload
from config import BOT_TOKEN, LOG_LEVEL

# Настройка логгера
logger = logging.getLogger("arkheai")
# Используем LOG_LEVEL из config, если доступен
log_level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
logger.setLevel(log_level)

# Настройка вывода в консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(log_level)

# Форматирование логов
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)

# Режим работы бота: webhook или polling
USE_WEBHOOK = os.getenv("USE_WEBHOOK", "false").lower() == "true"
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/webhook")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")


async def check_webhook_info(bot: Bot):
    """Проверка информации о webhook через Telegram API."""
    try:
        webhook_info = await bot.get_webhook_info()
        logger.info(f"Webhook info: URL={webhook_info.url}, Pending updates={webhook_info.pending_update_count}")
        if webhook_info.url:
            logger.info(f"Current webhook URL: {webhook_info.url}")
        else:
            logger.info("No webhook is set (using polling or not configured)")
        return webhook_info
    except Exception as e:
        logger.error(f"Error checking webhook info: {e}")
        return None


async def setup_webhook(bot: Bot):
    """Настройка webhook для бота."""
    if not WEBHOOK_URL:
        raise ValueError("WEBHOOK_URL environment variable is not set")
    
    full_webhook_url = f"{WEBHOOK_URL.rstrip('/')}{WEBHOOK_PATH}"
    logger.info(f"Setting webhook to: {full_webhook_url}")
    
    try:
        await bot.set_webhook(
            url=full_webhook_url,
            secret_token=WEBHOOK_SECRET if WEBHOOK_SECRET else None,
            drop_pending_updates=True
        )
        logger.info("Webhook set successfully")
        await check_webhook_info(bot)
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")
        raise


async def remove_webhook(bot: Bot):
    """Удаление webhook (для переключения на polling)."""
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Webhook removed successfully")
    except Exception as e:
        logger.error(f"Error removing webhook: {e}")


async def start_polling_mode(bot: Bot, dp: Dispatcher):
    """Запуск бота в режиме polling."""
    logger.info("Starting bot in POLLING mode...")
    
    # Убеждаемся, что webhook не установлен
    await remove_webhook(bot)
    
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


async def start_webhook_mode(bot: Bot, dp: Dispatcher):
    """Запуск бота в режиме webhook."""
    logger.info("Starting bot in WEBHOOK mode...")
    
    # Настраиваем webhook
    await setup_webhook(bot)
    
    # Создаем aiohttp приложение
    app = web.Application()
    
    # Настраиваем обработчик webhook
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET if WEBHOOK_SECRET else None,
    )
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    
    setup_application(app, dp, bot=bot)
    
    # Получаем порт из окружения или используем 8080 по умолчанию
    port = int(os.getenv("PORT", "8080"))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"Webhook server starting on {host}:{port}, path: {WEBHOOK_PATH}")
    
    # Запускаем сервер
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host=host, port=port)
    await site.start()
    
    # Держим сервер запущенным
    try:
        await asyncio.Event().wait()  # Бесконечное ожидание
    finally:
        await runner.cleanup()


async def main():
    """Main function to start the bot."""
    logger.info("Starting Arkhe AI bot...")
    logger.info(f"BOT_TOKEN is set: {bool(BOT_TOKEN)}")
    logger.info(f"USE_WEBHOOK: {USE_WEBHOOK}")
    
    if USE_WEBHOOK:
        logger.info(f"WEBHOOK_URL: {WEBHOOK_URL}")
        logger.info(f"WEBHOOK_PATH: {WEBHOOK_PATH}")

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(upload.router)

    try:
        if USE_WEBHOOK:
            await start_webhook_mode(bot, dp)
        else:
            await start_polling_mode(bot, dp)
    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
    finally:
        if not USE_WEBHOOK:
            await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot stopped due to error: {e}", exc_info=True)