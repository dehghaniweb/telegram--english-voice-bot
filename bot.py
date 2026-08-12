import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🇮🇷 سلام علی 👋\n\n"
        "ربات فارسی با موفقیت روشن است.\n"
        "یک متن فارسی بفرست."
    )


async def message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    await update.message.reply_text(
        "✅ پیام دریافت شد!\n\n"
        f"متن شما:\n{text}"
    )


def main():

    print("================================")
    print("🇮🇷 PERSIAN VOICE BOT STARTED")
    print("================================")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            message
        )
    )

    print("🤖 Waiting for Telegram messages...")

    app.run_polling(
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()
