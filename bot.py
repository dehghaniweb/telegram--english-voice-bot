import os
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
        "یک جمله انگلیسی بفرست تا Voiceهای انگلیسی را پیدا کنم 🎙️"
    )


async def generate_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text.strip()

    if len(text) > 5000:
        await update.message.reply_text(
            f"⚠️ متن شما {len(text)} کاراکتر است.\n\n"
            "حداکثر ۵۰۰۰ کاراکتر مجاز است."
        )
        return

    await update.message.reply_text(
        "🇺🇸 در حال بررسی Voiceهای English (United States)..."
    )

    try:

        async with async_playwright() as p:

            browser = await p.chromium.launch(headless=True)

            page = await browser.new_page(
                accept_downloads=True
            )

            await page.goto(
                VOICE_URL,
                wait_until="networkidle",
                timeout=60000
            )

            # قبول کوکی‌ها
            accept = page.get_by_role(
                "button",
                name="Accept All"
            )

            if await accept.count() > 0:
                try:
                    await accept.click(timeout=3000)
                except Exception:
                    pass

            await page.wait_for_timeout(2000)

            # انتخاب English United States
            language = page.locator(
                "#languageSelect"
            )

            await language.select_option(
                "en-US"
            )

            # صبر برای تغییر Voiceها
            await page.wait_for_timeout(2000)

            # پیدا کردن تمام select ها
            selects = await page.locator(
                "select"
            ).count()

            result = []

            for i in range(selects):

                select = page.locator(
                    "select"
                ).nth(i)

                info = await select.evaluate(
                    """e => ({
                        id: e.id,
                        name: e.name,
                        value: e.value
                    })"""
                )

                options = await select.locator(
                    "option"
                ).evaluate_all(
                    """
                    els => els.map(e => ({
                        text: e.textContent.trim(),
                        value: e.value
                    }))
                    """
                )

                result.append(
                    {
                        "index": i,
                        "info": info,
                        "options": options
                    }
                )

            message = "🎙 Voiceهای English (United States):\n\n"

            found = False

            for item in result:

                options = item["options"]

                if len(options) > 1:

                    found = True

                    message += (
                        f"SELECT #{item['index']}\n"
                        f"ID: {item['info']['id']}\n\n"
                    )

                    for option in options:

                        message += (
                            f"• {option['text']}\n"
                            f"  value: {option['value']}\n\n"
                        )

            if not found:

                message += (
                    "⚠️ Voice بعد از انتخاب زبان "
                    "به صورت SELECT پیدا نشد.\n\n"
                    "باید روش دیگری برای شناسایی Voiceها استفاده کنیم."
                )

            await update.message.reply_text(
                message[:4000]
            )

            await browser.close()

    except Exception as e:

        await update.message.reply_text(
            "❌ خطا:\n\n"
            f"{str(e)[:1500]}"
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
