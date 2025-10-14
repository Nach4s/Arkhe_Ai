import asyncio
import logging
from aiogram import Bot, Dispatcher

from handlers import start, upload
from config import BOT_TOKEN, LOG_LEVEL

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main function to start the bot."""
    logger.info("Starting Arkhe AI bot...")
    
    # Initialize bot
    bot = Bot(token=BOT_TOKEN)
    
    # Initialize dispatcher
    dp = Dispatcher()
    
    # Include routers
    dp.include_router(start.router)
    dp.include_router(upload.router)
    
    logger.info("Bot is ready. Starting polling...")
    
    try:
        # Start polling
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
