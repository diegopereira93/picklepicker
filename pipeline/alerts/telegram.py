import os
import logging
from telegram import Bot

logger = logging.getLogger(__name__)


async def send_telegram_alert(message: str) -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        logger.warning("Telegram credentials not set, logging alert instead: %s", message)
        return
    bot = Bot(token=token)
    await bot.send_message(chat_id=chat_id, text=f"[PickleIQ Alert] {message}")
