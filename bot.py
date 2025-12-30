import asyncio
import logging
from aiogram import Bot, Dispatcher
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from handlers import start, upload
from config import BOT_TOKEN, LOG_LEVEL




async def main():
    """Main function to start the bot."""
    logger.info("Starting Arkhe AI bot...")

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(upload.router)

    logger.info("Bot is ready. Starting polling...")

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot stopped due to error: {e}")