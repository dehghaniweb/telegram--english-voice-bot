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
        "⏳ متن دریافت شد.\n"
        "در حال ساخت فایل صوتی... 🎙️"
    )

    audio_file = Path("/tmp/voice.mp3")

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

            # وارد کردن متن
            textarea = page.locator(
                "textarea[placeholder='Enter text up to 5000 characters...']"
            )

            await textarea.fill(text)

            # ساخت صدا
            await page.get_by_role(
                "button",
                name="Generate Voice"
            ).click()

            # صبر برای تولید
            await page.wait_for_timeout(5000)

            # دانلود MP3
            download_button = page.get_by_role(
                "button",
                name="⬇ Download MP3"
            )

            await download_button.wait_for(
                state="visible",
                timeout=60000
            )

            async with page.expect_download(
                timeout=60000
            ) as download_info:

                await download_button.click()

            download = await download_info.value

            await download.save_as(str(audio_file))

            await browser.close()

        # ارسال فایل صوتی به تلگرام
        with open(audio_file, "rb") as audio:

            await update.message.reply_audio(
                audio=audio,
                title="English Voice 🎧",
                caption="🎙️ ساخته‌شده با VoiceLime"
            )

        # حذف فایل موقت
        if audio_file.exists():
            audio_file.unlink()

    except Exception as e:

        await update.message.reply_text(
            "❌ هنگام ساخت فایل صوتی مشکلی پیش آمد.\n\n"
            f"جزئیات: {str(e)[:1000]}"
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
