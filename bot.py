import os
from pathlib import Path

from playwright.async_api import async_playwright
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

VOICE_URL = "https://voicelime.com/voice-generator"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام علی 👋\n\n"
        "متن انگلیسی خودت را بفرست تا برایت صوتی کنم 🎧"
    )


async def generate_voice(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    text = update.message.text.strip()

    if len(text) > 5000:
        await update.message.reply_text(
            f"⚠️ متن شما {len(text)} کاراکتر است.\n\n"
            "VoiceLime حداکثر ۵۰۰۰ کاراکتر قبول می‌کند.\n"
            "لطفاً متن را کوتاه‌تر کن."
        )
        return

    await update.message.reply_text(
        "🔎 در حال بررسی Voiceهای VoiceLime..."
    )

    try:
        async with async_playwright() as p:

            browser = await p.chromium.launch(headless=True)

            page = await browser.new_page(
                accept_downloads=True
            )

            await page.goto(
                VOICE_URL,
                wait_until="domcontentloaded",
                timeout=60000,
            )

            # قبول کوکی‌ها در صورت وجود
            accept_button = page.get_by_role(
                "button",
                name="Accept All"
            )

            if await accept_button.count() > 0:
                try:
                    await accept_button.click(timeout=3000)
                except Exception:
                    pass

            # پیدا کردن Select ها
            selects = await page.locator("select").count()

            voice_info = []

            for i in range(selects):

                options = await (
                    page.locator("select")
                    .nth(i)
                    .locator("option")
                    .all()
                )

                values = []

                for option in options:

                    text_option = (
                        await option.inner_text()
                    ).strip()

                    value_option = (
                        await option.get_attribute("value")
                    )

                    values.append(
                        f"{text_option} | value={value_option}"
                    )

                if values:
                    voice_info.append(
                        f"SELECT #{i}:\n"
                        + "\n".join(values)
                    )

            if voice_info:

                message = (
                    "🎙 Voiceهای پیدا شده در VoiceLime:\n\n"
                    + "\n\n".join(voice_info)
                )

                await update.message.reply_text(
                    message[:4000]
                )

            else:

                await update.message.reply_text(
                    "⚠️ Voice به صورت SELECT پیدا نشد."
                )

            await browser.close()

    except Exception as e:

        await update.message.reply_text(
            "❌ خطا هنگام بررسی Voiceها:\n\n"
            f"{str(e)[:1000]}"
        )


def main():

    app = Application.builder().token(TOKEN).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            generate_voice
        )
    )

    print("Bot is running...")

    app.run_polling()


if __name__ == "__main__":
    main()
