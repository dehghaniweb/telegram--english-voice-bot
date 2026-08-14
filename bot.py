import os
import time
from pathlib import Path

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from playwright.async_api import async_playwright


TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
URL = "https://voicelime.com/voice-generator"

DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)


async def open_browser():
    playwright = await async_playwright().start()

    browser = await playwright.chromium.launch(
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

    return playwright, browser, page


async def get_voices():

    playwright, browser, page = await open_browser()

    try:

        await page.goto(
            URL,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        await page.wait_for_timeout(3000)

        selects = page.locator("select")
        count = await selects.count()

        print("Select count:", count)

        if count < 2:
            raise Exception(
                "Voice selector was not found."
            )

        voice_select = selects.nth(1)
        options = voice_select.locator("option")

        number = await options.count()

        voices = []

        for i in range(number):

            option = options.nth(i)

            value = await option.get_attribute("value")
            name = (await option.inner_text()).strip()

            if value and name:

                voices.append({
                    "value": value,
                    "name": name,
                })

        print("Voices found:", len(voices))

        return voices

    finally:

        await browser.close()
        await playwright.stop()


async def generate_voice(
    text,
    voice_value,
    speed_value
):

    filename = (
        DOWNLOAD_DIR /
        f"voice_{int(time.time())}.mp3"
    )

    playwright, browser, page = await open_browser()

    try:

        print("Opening VoiceLime...")

        await page.goto(
            URL,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        await page.wait_for_timeout(3000)

        print("Page loaded.")

        # -----------------------------
        # TEXT
        # -----------------------------

        textarea = page.locator("textarea").first

        await textarea.wait_for(
            state="visible",
            timeout=30000
        )

        await textarea.fill(text)

        print("Text entered.")

        # -----------------------------
        # SELECTS
        # -----------------------------

        selects = page.locator("select")
        count = await selects.count()

        print("Select count:", count)

        if count < 2:
            raise Exception(
                "Voice selector not found."
            )

        # Language
        language = selects.nth(0)

        try:
            await language.select_option(
                label="English"
            )
        except Exception:
            pass

        # Voice
        voice = selects.nth(1)

        await voice.select_option(
            value=voice_value
        )

        print(
            "Voice selected:",
            voice_value
        )

        # -----------------------------
        # SPEED
        # -----------------------------

        ranges = page.locator(
            'input[type="range"]'
        )

        range_count = await ranges.count()

        print(
            "Range inputs:",
            range_count
        )

        if range_count >= 2:

            speed = ranges.nth(1)

            await speed.evaluate(
                """
                (element, value) => {
                    element.value = value;
                    element.dispatchEvent(
                        new Event(
                            'input',
                            {bubbles: true}
                        )
                    );
                    element.dispatchEvent(
                        new Event(
                            'change',
                            {bubbles: true}
                        )
                    );
                }
                """,
                str(speed_value)
            )

            print(
                "Speed:",
                speed_value
            )

        # -----------------------------
        # GENERATE
        # -----------------------------

        generate = page.get_by_role(
            "button",
            name="Generate Voice"
        )

        await generate.wait_for(
            state="visible",
            timeout=30000
        )

        print("Generating...")

        await generate.click()

        # -----------------------------
        # WAIT
        # -----------------------------

        await page.wait_for_timeout(8000)

        # -----------------------------
        # DOWNLOAD
        # -----------------------------

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
        ) as info:

            await download_button.click()

        download = await info.value

        await download.save_as(
            str(filename)
        )

        print(
            "Saved:",
            filename
        )

        return filename

    finally:

        await browser.close()
        await playwright.stop()


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "🎙 VoiceLime\n\n"
        "در حال دریافت صداها..."
    )

    try:

        voices = await get_voices()

        context.user_data["voices"] = voices

        buttons = []

        for i, voice in enumerate(
            voices[:15]
        ):

            button = InlineKeyboardButton(
                voice["name"],
                callback_data=f"voice_{i}"
            )

            buttons.append([button])

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
            "VOICE ERROR:",
            repr(e)
        )

        await update.message.reply_text(
            "❌ دریافت Voiceها ناموفق بود.\n\n"
            + str(e)
        )


async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    data = query.data

    # -----------------------------
    # VOICE
    # -----------------------------

    if data.startswith("voice_"):

        index = int(
            data.split("_")[1]
        )

        voices = context.user_data.get(
            "voices",
            []
        )

        if index >= len(voices):

            await query.edit_message_text(
                "❌ Voice پیدا نشد."
            )

            return

        selected = voices[index]

        context.user_data["voice"] = selected

        buttons = [
            [
                InlineKeyboardButton(
                    "🐢 کمی کم",
                    callback_data="speed_-10"
                )
            ],
            [
                InlineKeyboardButton(
                    "🎙 متوسط",
                    callback_data="speed_0"
                )
            ],
            [
                InlineKeyboardButton(
                    "⚡ کمی زیاد",
                    callback_data="speed_10"
                )
            ],
        ]

        await query.edit_message_text(
            "🎤 Voice:\n"
            + selected["name"]
            + "\n\n"
            "⚡ سرعت را انتخاب کن:",
            reply_markup=InlineKeyboardMarkup(
                buttons
            )
        )

        return

    # -----------------------------
    # SPEED
    # -----------------------------

    if data.startswith("speed_"):

        speed = int(
            data.split("_")[1]
        )

        context.user_data["speed"] = speed

        voice = context.user_data.get(
            "voice"
        )

        if not voice:

            await query.edit_message_text(
                "❌ ابتدا Voice را انتخاب کن."
            )

            return

        names = {
            -10: "🐢 کمی کم",
            0: "🎙 متوسط",
            10: "⚡ کمی زیاد",
        }

        speed_name = names.get(
            speed,
            "🎙 متوسط"
        )

        await query.edit_message_text(
            "✅ تنظیمات آماده است.\n\n"
            "🎤 Voice: "
            + voice["name"]
            + "\n"
            "⚡ Speed: "
            + speed_name
            + "\n\n"
            "حالا متن انگلیسی را بفرست."
        )


async def text_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    text = update.message.text.strip()

    voice = context.user_data.get(
        "voice"
    )

    speed = context.user_data.get(
        "speed",
        0
    )

    if not voice:

        await update.message.reply_text(
            "ابتدا /start را بزن."
        )

        return

    await update.message.reply_text(
        "🎙 در حال ساخت فایل صوتی..."
    )

    try:

        file = await generate_voice(
            text,
            voice["value"],
            speed
        )

        with open(
            file,
            "rb"
        ) as audio:

            await update.message.reply_audio(
                audio=audio,
                filename="english_voice.mp3"
            )

        file.unlink(
            missing_ok=True
        )

    except Exception as e:

        print(
            "GENERATION ERROR:",
            repr(e)
        )

        await update.message.reply_text(
            "❌ Voice generation failed.\n\n"
            + str(e)
        )


def main():

    if not TOKEN:

        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN is missing."
        )

    app = (
        Application
        .builder()
        .token(TOKEN)
        .build()
    )

    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            button_handler
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            text_handler
        )
    )

    print(
        "BOT IS RUNNING..."
    )

    app.run_polling()


if __name__ == "__main__":
    main()
