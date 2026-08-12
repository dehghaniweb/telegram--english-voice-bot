import os
from playwright.async_api import async_playwright
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام علی 👋\n\n"
        "یک جمله انگلیسی بفرست تا VoiceLime را تست کنیم."
    )


async def generate_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if len(text) > 5000:
        await update.message.reply_text(
            f"⚠️ متن شما {len(text)} کاراکتر است.\n"
            "لطفاً متن را کوتاه‌تر کن."
        )
        return

    await update.message.reply_text("⏳ در حال اتصال به VoiceLime...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        page = await browser.new_page()

        await page.goto(
            "https://voicelime.com/voice-generator",
            wait_until="domcontentloaded",
            timeout=60000
        )

        await update.message.reply_text(
            f"✅ VoiceLime باز شد.\n\n"
            f"متن شما:\n{text}"
        )

        await browser.close()


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, generate_voice)
    )

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
