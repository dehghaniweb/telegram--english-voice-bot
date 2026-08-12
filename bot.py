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
        "یک جمله انگلیسی بفرست تا Voiceهای VoiceLime را پیدا کنم 🎙️"
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
        "🔎 در حال شناسایی Voiceهای واقعی VoiceLime..."
    )

    try:

        async with async_playwright() as p:

            browser = await p.chromium.launch(headless=True)

            page = await browser.new_page()

            await page.goto(
                VOICE_URL,
                wait_until="networkidle",
                timeout=60000
            )

            # Cookie
            accept = page.get_by_role(
                "button",
                name="Accept All"
            )

            if await accept.count() > 0:

                try:
                    await accept.click(timeout=3000)
                except Exception:
                    pass

            # صبر برای اجرای JavaScript
            await page.wait_for_timeout(3000)

            # همه عناصر قابل انتخاب
            elements = await page.locator(
                "select, option, [role='option'], "
                "[role='combobox'], input"
            ).evaluate_all(
                """
                els => els.map((e, i) => ({
                    index: i,
                    tag: e.tagName,
                    text: (e.innerText || e.textContent || '').trim(),
                    value: e.value || '',
                    placeholder: e.placeholder || '',
                    aria: e.getAttribute('aria-label') || '',
                    role: e.getAttribute('role') || '',
                    name: e.getAttribute('name') || '',
                    id: e.id || '',
                    type: e.type || ''
                }))
                """
            )

            # ساخت گزارش
            message = "🎙 عناصر پیدا شده:\n\n"

            for item in elements:

                message += (
                    f"#{item['index']} "
                    f"{item['tag']}\n"
                    f"Text: {item['text'][:150]}\n"
                    f"Value: {item['value']}\n"
                    f"Placeholder: {item['placeholder']}\n"
                    f"ARIA: {item['aria']}\n"
                    f"Role: {item['role']}\n"
                    f"Name: {item['name']}\n"
                    f"ID: {item['id']}\n"
                    f"Type: {item['type']}\n\n"
                )

            if len(message) > 3900:
                message = message[:3900] + "\n..."

            await update.message.reply_text(message)

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
