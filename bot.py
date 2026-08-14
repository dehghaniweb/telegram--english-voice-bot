import os
import time
from pathlib import Path

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
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
# DEFAULT SETTINGS
# =========================================================

DEFAULT_SPEED = 0

# VoiceLime speed:
# -10 = slightly slower
#   0 = normal
# +10 = slightly faster


# =========================================================
# GET VOICES FROM VOICELIME
# =========================================================

async def get_voices():

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
            ],
        )

        page = await browser.new_page()

        try:

            print("Loading VoiceLime...")

            await page.goto(
                VOICE_LIME_URL,
                wait_until="domcontentloaded",
                timeout=60000,
            )

            await page.wait_for_timeout(3000)

            # Try to disable ad blocker warning if present
            try:

                disable_button = page.get_by_role(
                    "button",
                    name="Disable Ad Blocker & Reload"
                )

                if await disable_button.is_visible():

                    print("Ad blocker message detected.")

                    await disable_button.click()

                    await page.wait_for_timeout(5000)

            except Exception:
                pass

            selects = page.locator("select")

            count = await selects.count()

            print("Select count:", count)

            if count < 2:
                raise Exception(
                    "VoiceLime voice selector was not found."
                )

            voice_select = selects.nth(1)

            options = voice_select.locator("option")

            option_count = await options.count()

            voices = []

            for i in range(option_count):

                option = options.nth(i)

                value = await option.get_attribute("value")

                name = (await option.inner_text()).strip()

                if value and name:

                    voices.append({
                        "value": value,
                        "name": name,
                    })

            print(
                f"Found {len(voices)} voices."
            )

            return voices

        finally:

            await browser.close()


# =========================================================
# GENERATE VOICE
# =========================================================

async def generate_voice(
    text,
    voice_value,
    speed_value
):

    output_file = (
        DOWNLOAD_DIR /
        f"voice_{int(time.time())}.mp3"
    )

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

            # =================================================
            # AD BLOCKER
            # =================================================

            try:

                disable_button = page.get_by_role(
                    "button",
                    name="Disable Ad Blocker & Reload"
                )

                if await disable_button.is_visible():

                    print(
                        "Ad blocker warning found."
                    )

                    await disable_button.click()

                    await page.wait_for_timeout(5000)

            except Exception:
                pass

            # =================================================
            # TEXT
            # =================================================

            text_area = page.locator(
                "textarea"
            ).first

            await text_area.wait_for(
                state="visible",
                timeout=30000
            )

            await text_area.fill(text)

            print("Text entered.")

            # =================================================
            # LANGUAGE
            # =================================================

            selects = page.locator("select")

            select_count = await selects.count()

            if select_count < 2:

                raise Exception(
                    "Voice selector not found."
                )

            language_select = selects.nth(0)

            try:

                await language_select.select_option(
                    label="English"
                )

            except Exception:

                try:

                    await language_select.select_option(
                        value="en"
                    )

                except Exception:

                    print(
                        "Could not explicitly select English."
                    )

            # =================================================
            # VOICE
            # =================================================

            voice_select = selects.nth(1)

            await voice_select.select_option(
                value=voice_value
            )

            print(
                "Voice selected:",
                voice_value
            )

            # =================================================
            # SPEED
            # =================================================

            # VoiceLime has Pitch, Speed and Volume inputs.
            # We assume the three range inputs are:
            #
            # 0 = Pitch
            # 1 = Speed
            # 2 = Volume

            range_inputs = page.locator(
                'input[type="range"]'
            )

            range_count = await range_inputs.count()

            print(
                "Range inputs:",
                range_count
            )

            if range_count >= 2:

                speed_input = range_inputs.nth(1)

                await speed_input.evaluate(
                    """(el, value) => {
                        el.value = value;
                        el.dispatchEvent(
                            new Event('input', {bubbles: true})
                        );
                        el.dispatchEvent(
                            new Event('change', {bubbles: true})
                        );
                    }""",
                    str(speed_value)
                )

                print(
                    "Speed set:",
                    speed_value
                )

            # =================================================
            # GENERATE
            # =================================================

            generate_button = page.get_by_role(
                "button",
                name="Generate Voice"
            )

            await generate_button.wait_for(
                state="visible",
                timeout=30000
            )

            print(
                "Generating voice..."
            )

            await generate_button.click()

            # =================================================
            # WAIT
            # =================================================

            print(
                "Waiting for audio..."
            )

            await page.wait_for_timeout(5000)

            # =================================================
            # DOWNLOAD
            # =================================================

            download_button = page.get_by_role(
                "button",
                name="Download MP3"
            )

            await download_button.wait_for(
                state="visible",
                timeout=60000
            )

            print(
                "Download button found."
            )

            async with page.expect_download(
                timeout=60000
            ) as download_info:

                await download_button.click()

            download = await download_info.value

            await download.save_as(
                str(output_file)
            )

            print(
                "MP3 saved:",
                output_file
            )

            return output_file

        finally:

            await browser.close()


# =========================================================
# START COMMAND
# =========================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "🎙 English Voice Bot\n\n"
        "در حال دریافت لیست صداها..."
    )

    try:

        voices = await get_voices()

        context.user_data["voices"] = voices

        # Show first 12 voices
        buttons = []

        for i, voice in enumerate(
            voices[:12]
        ):

            buttons.append([
                InlineKeyboardButton(
                    voice["name"],
                    callback_data=f"voice:{i}"
                )
            ])

        if not buttons:

            raise Exception(
                "No voices found."
            )

        await update.message.reply_text(
            "🎤 صدای موردنظر را انتخاب کن:",
            reply_markup=InlineKeyboardMarkup(
                buttons
            )
        )

    except Exception as e:

        print(
            "VOICE LIST ERROR:",
            repr(e)
        )

        await update.message.reply_text(
            "❌ نتوانستم لیست صداهای VoiceLime را بگیرم.\n\n"
            f"{str(e)}"
        )


# =========================================================
# CALLBACKS
# =========================================================

async def callback_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    data = query.data

    # =====================================================
    # VOICE
    # =====================================================

    if data.startswith("voice:"):

        index = int(
            data.split(":")[1]
        )

        voices = context.user_data.get(
            "voices",
            []
        )

        if index >= len(voices):

            await query.edit_message_text(
                "❌ این Voice پیدا نشد."
            )

            return

        voice = voices[index]

        context.user_data["voice"] = voice

        speed_buttons = [

            [
                InlineKeyboardButton(
                    "🐢 کمی کم",
                    callback_data="speed:-10"
                )
            ],

            [
                InlineKeyboardButton(
                    "🎙 متوسط",
                    callback_data="speed:0"
                )
            ],

            [
                InlineKeyboardButton(
