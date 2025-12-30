import os
from dotenv import load_dotenv

# Load .env file if it exists (for local development)
# In production (e.g., Render), environment variables are set directly
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Validate required environment variables
# Check both .env file and system environment variables
if not BOT_TOKEN:
    raise ValueError(
        "BOT_TOKEN is not set. "
        "Please set it as an environment variable or in a .env file. "
        "On Render, set it in the Environment Variables section of your service settings."
    )
if not OPENAI_API_KEY:
    raise ValueError(
        "OPENAI_API_KEY is not set. "
        "Please set it as an environment variable or in a .env file. "
        "On Render, set it in the Environment Variables section of your service settings."
    )
