import asyncio
import os
from datetime import datetime
import structlog


logger = structlog.get_logger()


class TelegramAlerter:
    """Send alerts to Telegram on errors (gracefully disabled if no token)."""

    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.bot = None
        if self.bot_token:
            try:
                from telegram import Bot
                self.bot = Bot(token=self.bot_token)
            except ImportError:
                logger.warning("telegram.not_installed")
        self.min_alert_interval = 60  # Rate limit: don't spam same error twice in 60s
        self.last_alerts = {}

    async def send_alert(self, severity: str, title: str, details: str, context: dict = None):
        """Send alert to Telegram asynchronously without blocking request."""
        if not self.bot or not self.chat_id:
            logger.warning("telegram.disabled", title=title)
            return

        # Rate limit: same error type not more than once per 60s
        alert_key = f"{severity}:{title}"
        now = datetime.now().timestamp()
        if alert_key in self.last_alerts and (now - self.last_alerts[alert_key]) < self.min_alert_interval:
            return

        self.last_alerts[alert_key] = now

        # Format message
        emoji_map = {"ERROR": "🚨", "WARNING": "⚠️", "INFO": "ℹ️"}
        emoji = emoji_map.get(severity, "📌")

        message = f"{emoji} *{severity}: {title}*\n{details}"
        if context:
            context_str = str(context)[:200]
            message += f"\n```{context_str}```"

        try:
            from telegram.error import TelegramError
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode="Markdown",
                read_timeout=5
            )
            logger.info("telegram.alert.sent", severity=severity, title=title)
        except Exception as e:
            logger.error("telegram.alert.failed", error=str(e), title=title)


alerter = TelegramAlerter()


async def send_scraper_alert(error: str, url: str):
    """Alert ops when scraper fails."""
    await alerter.send_alert(
        severity="ERROR",
        title="Scraper failure",
        details=f"Failed to scrape {url[:50]}...: {error[:100]}",
        context={"url": url, "error_type": type(error).__name__}
    )
