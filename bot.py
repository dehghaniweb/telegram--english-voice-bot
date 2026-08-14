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


# =========================================================
# SETTINGS
# =========================================================

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

VOICE_LIME_URL = "https://voicelime.com/voice-generator"

DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)


# =========================================================
# VOICELIME
# =========================================================

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

            # Check page
            page_text = await page.locator("body").inner_text()

            if "Ad Blocker Detected" in page_text:
                raise Exception(
                    "VoiceLime detected an ad blocker."
                )

            # =================================================
            # TEXT BOX
            # =================================================

            text_area = page.locator("textarea").first

            await text_area.wait_for(
                state="visible",
                timeout=30000
            )

            await text_area.fill(text)

            print("Text entered.")

            # =================================================
            # SELECT LANGUAGE
            # =================================================

            selects = page.locator("select")

            select_count = await selects.count()

            print(
                "Select elements:",
                select_count
            )

            if select_count > 0:

                try:
                    await selects.nth(0).select_option(
                        label="English"
                    )

                except Exception:

                    try:
                        await selects.nth(0).select_option(
                            value="en"
                        )

                    except Exception:
                        pass

            # =================================================
            # SELECT VOICE
            # =================================================

            if select_count > 1:

                try:

                    options = await selects.nth(1).locator(
                        "option"
                    ).all()

                    for option in options:

                        value = await option.get_attribute(
                            "value"
                        )

                        label = await option.inner_text()

                        if value and value.strip():

                            try:

                                await selects.nth(1).select_option(
                                    value=value
                                )

                                print(
                                    "Selected voice:",
                                    label
                                )

                                break

                            except Exception:
                                continue

                except Exception as e:

                    print(
                        "Voice selection warning:",
                        e
                    )

            # =================================================
            # GENERATE VOICE
            # =================================================

            generate_button = page.get_by_role(
                "button",
                name="Generate Voice"
            )

            await generate_button.wait_for(
                state="visible",
                timeout=30000
            )

            print("Generating voice...")

            await generate_button.click()

            # Wait for generation
            await page.wait_for_timeout(5000)

            # =================================================
            # DOWNLOAD MP3
            # =================================================

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
                "Downloaded:",
                output_file
            )

            return output_file

        finally:

            await browser.close()


# =========================================================
# TELEGRAM MESSAGE HANDLER
# =========================================================

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

    print(
        "Received:",
        text
    )

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

        # Delete temporary MP3
        try:
            audio_file.unlink()
        except Exception:
            pass

    except Exception as e:

        print(
            "ERROR:",
            repr(e)
        )

        await update.message.reply_text(
            "❌ Voice generation failed.\n\n"
            f"Error: {str(e)}"
        )


# =========================================================
# MAIN
# =========================================================

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


# =========================================================
# START
# =========================================================

if __
