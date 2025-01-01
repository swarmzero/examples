import logging
import os
from enum import Enum

from dotenv import load_dotenv

from bitquery_service import BitQueryService
from dex_agent import DexAgent
from dex_rabbit_bot import DexRabbitBot


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


def setup_logging():
    """Configure logging based on environment variable"""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    if log_level not in LogLevel.__members__:
        print(f"Invalid LOG_LEVEL: {log_level}. Defaulting to INFO")
        log_level = "INFO"

    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def main():
    # Load environment variables
    load_dotenv()

    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # Get required tokens
        telegram_token = os.getenv("BOTFATHER_API_TOKEN")
        bitquery_token = os.getenv("BITQUERY_OAUTH_TOKEN")

        if not telegram_token or not bitquery_token:
            raise ValueError("Missing required environment variables. Check .env file.")

        # Initialize services
        logger.info("Initializing services...")
        bitquery_service = BitQueryService(bitquery_token)
        agent = DexAgent(bitquery_service)

        # Create and run bot
        logger.info("Starting DexRabbit Bot...")
        bot = DexRabbitBot(telegram_token, agent)
        bot.run()

    except Exception as e:
        logger.error(f"Failed to start bot: {str(e)}")
        raise


if __name__ == "__main__":
    main()
