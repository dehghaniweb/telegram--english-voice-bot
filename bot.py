import os
import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    logger.info("START command received")

    await update.message.reply_text(
        "🇮🇷 سلام علی 👋\n\n"
        "✅ ربات فارسی فعال است.\n\n"
        "یک متن فارسی بفرست."
    )


async def message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    logger.info("Message received: %s", text)

    await update.message.reply_text(
        "✅ پیام دریافت شد!\n\n"
        f"متن شما:\n{text}"
    )


async def error_handler(update, context):

    logger.error(
        "Exception while handling update:",
        exc_info=context.error
    )


def main():

    if not TOKEN:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN is missing!"
        )

    logger.info("================================")
    logger.info("🇮🇷 PERSIAN VOICE BOT STARTED")
    logger.info("================================")

    app = (
        Application.builder()
        .token(TOKEN)
        .build()
    )

    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            message
        )
    )

    app.add_error_handler(
        error_handler
    )

    logger.info(
        "🤖 Waiting for Telegram messages..."
    )

    app.run_polling(
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()
