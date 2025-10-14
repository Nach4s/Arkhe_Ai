import asyncio
import logging
from aiogram import Bot, Dispatcher
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from handlers import start, upload
from config import BOT_TOKEN, LOG_LEVEL

# ---------- Fake HTTP server (for Render port scan) ----------
class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

def run_server():
    server = HTTPServer(('0.0.0.0', 10000), HealthCheck)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()
# --------------------------------------------------------------

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


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