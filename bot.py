import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from playwright.async_api import async_playwright

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

VOICE_URL = "https://airvoz.com/text-to-speech/persian"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🇮🇷 سلام علی 👋\n\n"
        "یک متن فارسی بفرست تا Voiceهای فارسی Airvoz را بررسی کنم."
    )


async def receive_text(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text.strip()

    context.user_data["text"] = text

    await update.message.reply_text(
        "🔎 در حال بررسی Airvoz..."
    )

    try:

        async with async_playwright() as p:

            browser = await p.chromium.launch(
                headless=True
            )

            page = await browser.new_page()

            await page.goto(
                VOICE_URL,
                wait_until="domcontentloaded",
                timeout=60000
            )

            await page.wait_for_timeout(5000)

            # پیدا کردن SELECTها
            selects = page.locator("select")

            select_count = await selects.count()

            message = (
                "🇮🇷 بررسی Airvoz\n\n"
                f"تعداد SELECTها: {select_count}\n\n"
            )

            for i in range(select_count):

                select = selects.nth(i)

                try:
                    element_id = await select.get_attribute("id")
                except:
                    element_id = ""

                try:
                    value = await select.input_value()
                except:
                    value = ""

                options = await select.locator(
                    "option"
                ).evaluate_all(
                    """
                    els => els.map(e => ({
                        text: (e.textContent || '').trim(),
                        value: e.value || ''
                    }))
                    """
                )

                message += (
                    f"━━━━━━━━━━━━━━\n"
                    f"SELECT #{i}\n"
                    f"ID: {element_id}\n"
                    f"Value: {value}\n"
                    f"Options: {len(options)}\n\n"
                )

                for option in options[:50]:

                    message += (
                        f"• {option['text']}\n"
                        f"  value={option['value']}\n"
                    )

                if len(options) > 50:
                    message += "\n... و گزینه‌های دیگر\n"

                message += "\n"

            # پیدا کردن دکمه‌ها
            buttons = page.locator("button")

            button_count = await buttons.count()

            message += (
                "━━━━━━━━━━━━━━\n"
                f"🔘 تعداد BUTTONها: {button_count}\n\n"
            )

            for i in range(button_count):

                button = buttons.nth(i)

                try:
                    text_value = (
                        await button.inner_text()
                    ).strip()
                except:
                    text_value = ""

                try:
                    button_id = (
                        await button.get_attribute("id")
                    )
                except:
                    button_id = ""

                try:
                    title = (
                        await button.get_attribute("title")
                    )
                except:
                    title = ""

                message += (
                    f"#{i} "
                    f"text={text_value[:100]} "
                    f"id={button_id} "
                    f"title={title}\n"
                )

            if len(message) > 3900:
                message = (
                    message[:3900]
                    + "\n\n⚠️ خروجی طولانی بود."
                )

            await update.message.reply_text(
                message
            )

            await browser.close()

    except Exception as e:

        await update.message.reply_text(
            "❌ خطا:\n\n"
            + str(e)[:1500]
        )


def main():

    app = Application.builder().token(
        TOKEN
    ).build()

    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            receive_text
        )
    )

    print(
        "🇮🇷 Persian Voice Bot is running..."
    )

    app.run_polling()


if __name__ == "__main__":
    main()
