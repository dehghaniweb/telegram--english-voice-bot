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
        "یک جمله انگلیسی بفرست تا Voiceهای VoiceLime را بررسی کنم 🎙️"
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
        "🔎 در حال پیدا کردن منوی Voice..."
    )

    try:

        async with async_playwright() as p:

            browser = await p.chromium.launch(
                headless=True
            )

            page = await browser.new_page()

            await page.goto(
                VOICE_URL,
                wait_until="networkidle",
                timeout=60000
            )

            # قبول کوکی
            accept = page.get_by_role(
                "button",
                name="Accept All"
            )

            if await accept.count() > 0:
                try:
                    await accept.click(timeout=3000)
                except Exception:
                    pass

            # انتخاب زبان انگلیسی آمریکا
            language = page.locator(
                "#languageSelect"
            )

            await language.select_option(
                "en-US"
            )

            # صبر برای JavaScript
            await page.wait_for_timeout(5000)

            # پیدا کردن همه select ها
            select_count = await page.locator(
                "select"
            ).count()

            message = (
                f"🎙 بررسی Voiceها\n\n"
                f"تعداد SELECTها: {select_count}\n\n"
            )

            for i in range(select_count):

                select = page.locator(
                    "select"
                ).nth(i)

                info = await select.evaluate(
                    """
                    e => ({
                        id: e.id || '',
                        name: e.name || '',
                        value: e.value || '',
                        disabled: e.disabled,
                        hidden: e.hidden
                    })
                    """
                )

                options = await select.locator(
                    "option"
                ).evaluate_all(
                    """
                    els => els.map(e => ({
                        text: (e.textContent || '').trim(),
                        value: e.value || '',
                        disabled: e.disabled
                    }))
                    """
                )

                message += (
                    f"━━━━━━━━━━━━━━\n"
                    f"SELECT #{i}\n"
                    f"ID: {info['id']}\n"
                    f"Name: {info['name']}\n"
                    f"Value: {info['value']}\n"
                    f"Disabled: {info['disabled']}\n"
                    f"Hidden: {info['hidden']}\n"
                    f"Options: {len(options)}\n\n"
                )

                for option in options[:30]:

                    message += (
                        f"• {option['text']}\n"
                        f"  value={option['value']}\n"
                    )

                if len(options) > 30:
                    message += (
                        f"\n... و "
                        f"{len(options) - 30} گزینه دیگر\n"
                    )

                message += "\n"

            if len(message) > 3900:
                message = message[:3900] + (
                    "\n\n⚠️ ادامه اطلاعات زیاد بود."
                )

            await update.message.reply_text(
                message
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
        CommandHandler(
            "start",
            start
        )
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
