import os
import time
from pathlib import Path

from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    ContextTypes,
    filters,
)

from playwright.async_api import async_playwright


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

VOICE_LIME_URL = "https://voicelime.com/voice-generator"

DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)


async def generate_voice(text: str) -> Path:

    output_file = DOWNLOAD_DIR / f"voice_{int(time.time())}.mp3"

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
            ],
        )

        page = await browser.new_page(
            accept_downloads=True
        )

        try:

            print("Opening VoiceLime...")

            await page.goto(
                VOICE_LIME_URL,
                wait_until="domcontentloaded",
                timeout=60000,
            )

            await page.wait_for_timeout(3000)

            print("VoiceLime opened.")

            text_area = page.locator("textarea").first

            await text_area.wait_for(
                state="visible",
                timeout=30000
            )

            await text_area.fill(text)

            print("Text entered.")

            generate_button = page.get_by_role(
                "button",
                name="Generate Voice"
            )

            await generate_button.wait_for(
                state="visible",
                timeout=30000
            )

            print("Clicking Generate Voice...")

            await generate_button.click()

            await page.wait_for_timeout(5000)

            download_button = page.get_by_role(
                "button",
                name="Download MP3"
            )

            await download_button.wait_for(
                state="visible",
                timeout=60000
            )

            print("Voice generated.")

            async with page.expect_download(
                timeout=60000
            ) as download_info:

                await download_button.click()

            download = await download_info.value

            await download.save_as(
                str(output_file)
            )

            print(
                f"MP3 saved: {output_file}"
            )

            return output_file

        finally:

            await browser.close()


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    text = update.message.text

    if not text:
        return

    text = text.strip()

    if not text:
        return

    print(f"Received: {text}")

    await update.message.reply_text(
        "🎙 Generating English voice..."
    )

    try:

        audio_file = await generate_voice(text)

        with open(
            audio_file,
            "rb"
        ) as audio:

            await update.message.reply_audio(
                audio=audio,
                filename="english_voice.mp3",
                title="English Voice"
            )

        try:
            audio_file.unlink()
        except Exception:
            pass

    except Exception as e:

        print(f"ERROR: {repr(e)}")

        await update.message.reply_text(
            "❌ Voice generation failed.\n\n"
            f"{str(e)}"
        )


def main():

    if not TELEGRAM_BOT_TOKEN:

        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN is not set."
        )

    app = (
        Application
        .builder()
        .token(TELEGRAM_BOT_TOKEN)
        .build()
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )

    print(
        "Telegram Voice Bot is running..."
    )

    app.run_polling()


if __name__ == "__main__":
    main()
