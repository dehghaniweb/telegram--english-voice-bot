import os
from pathlib import Path

from playwright.async_api import async_playwright
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

VOICE_URL = "https://voicelime.com/voice-generator"


# =========================================================
# VOICES
# =========================================================

VOICES = [
    ("Ava", "en-US-AvaNeural"),
    ("Andrew", "en-US-AndrewNeural"),
    ("Emma", "en-US-EmmaNeural"),
    ("Brian", "en-US-BrianNeural"),
    ("Ana", "en-US-AnaNeural"),
    ("Andrew Multilingual", "en-US-AndrewMultilingualNeural"),
    ("Aria", "en-US-AriaNeural"),
    ("Ava Multilingual", "en-US-AvaMultilingualNeural"),
    ("Brian Multilingual", "en-US-BrianMultilingualNeural"),
    ("Christopher", "en-US-ChristopherNeural"),
    ("Emma Multilingual", "en-US-EmmaMultilingualNeural"),
    ("Eric", "en-US-EricNeural"),
    ("Guy", "en-US-GuyNeural"),
    ("Jenny", "en-US-JennyNeural"),
    ("Michelle", "en-US-MichelleNeural"),
    ("Roger", "en-US-RogerNeural"),
    ("Steffan", "en-US-SteffanNeural"),
]


# =========================================================
# START
# =========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "سلام علی 👋\n\n"
        "🇺🇸 متن انگلیسی خودت را بفرست.\n\n"
        "بعد از ارسال متن، می‌توانی گوینده را انتخاب کنی 🎙️"
    )


# =========================================================
# RECEIVE TEXT
# =========================================================

async def receive_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    text = update.message.text.strip()

    if not text:
        return

    # محدودیت VoiceLime
    if len(text) > 5000:

        await update.message.reply_text(
            f"⚠️ متن شما {len(text)} کاراکتر است.\n\n"
            "VoiceLime حداکثر ۵۰۰۰ کاراکتر قبول می‌کند.\n\n"
            "اگر متن خیلی طولانی است، بهتر است آن را به چند بخش کوتاه‌تر تقسیم کنیم."
        )

        return

    # ذخیره متن برای مرحله انتخاب Voice
    context.user_data["text"] = text

    # ساخت دکمه‌های Voice
    keyboard = []

    row = []

    for name, value in VOICES:

        button = InlineKeyboardButton(
            f"🎙 {name}",
            callback_data=f"voice:{value}"
        )

        row.append(button)

        # دو دکمه در هر ردیف
        if len(row) == 2:

            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    keyboard.append(
        [
            InlineKeyboardButton(
                "❌ لغو",
                callback_data="cancel"
            )
        ]
    )

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🇺🇸 English (United States)\n\n"
        "🎙️ لطفاً گوینده موردنظر را انتخاب کن:",
        reply_markup=reply_markup
    )


# =========================================================
# VOICE SELECTION
# =========================================================

async def voice_selected(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    # لغو
    if query.data == "cancel":

        context.user_data.pop("text", None)

        await query.edit_message_text(
            "❌ عملیات لغو شد.\n\n"
            "هر وقت خواستی یک متن جدید بفرست."
        )

        return

    # دریافت Voice
    voice = query.data.replace(
        "voice:",
        "",
        1
    )

    text = context.user_data.get("text")

    if not text:

        await query.edit_message_text(
            "⚠️ متن پیدا نشد.\n\n"
            "لطفاً دوباره متن را ارسال کن."
        )

        return

    # نام Voice
    voice_name = voice

    for name, value in VOICES:

        if value == voice:

            voice_name = name
            break

    await query.edit_message_text(
        f"🎙 Voice انتخاب شد:\n"
        f"{voice_name}\n\n"
        f"⏳ در حال ساخت فایل صوتی...\n"
        f"لطفاً صبر کن."
    )

    audio_file = Path(
        f"/tmp/voice_{query.from_user.id}.mp3"
    )

    try:

        async with async_playwright() as p:

            browser = await p.chromium.launch(
                headless=True
            )

            page = await browser.new_page(
                accept_downloads=True
            )

            # باز کردن VoiceLime
            await page.goto(
                VOICE_URL,
                wait_until="domcontentloaded",
                timeout=60000
            )

            # قبول Cookie
            accept_button = page.get_by_role(
                "button",
                name="Accept All"
            )

            if await accept_button.count() > 0:

                try:

                    await accept_button.click(
                        timeout=3000
                    )

                except Exception:
                    pass

            # صبر برای آماده شدن صفحه
            await page.wait_for_timeout(2000)

            # انتخاب زبان English US
            language = page.locator(
                "#languageSelect"
            )

            await language.select_option(
                "en-US"
            )

            # صبر برای تغییر Voice
            await page.wait_for_timeout(1500)

            # انتخاب Voice
            voice_select = page.locator(
                "#voiceSelect"
            )

            await voice_select.select_option(
                voice
            )

            # وارد کردن متن
            textarea = page.locator(
                "textarea[placeholder='Enter text up to 5000 characters...']"
            )

            await textarea.fill(
                text
            )

            # Generate Voice
            generate_button = page.get_by_role(
                "button",
                name="Generate Voice"
            )

            await generate_button.click()

            # صبر برای تولید صدا
            await page.wait_for_timeout(5000)

            # پیدا کردن Download MP3
            download_button = page.get_by_role(
                "button",
                name="⬇ Download MP3"
            )

            await download_button.wait_for(
                state="visible",
                timeout=60000
            )

            # دانلود
            async with page.expect_download(
                timeout=60000
            ) as download_info:

                await download_button.click()

            download = await download_info.value

            await download.save_as(
                str(audio_file)
            )

            await browser.close()

        # ارسال MP3 به تلگرام
        with open(
            audio_file,
            "rb"
        ) as audio:

            await context.bot.send_audio(
                chat_id=query.message.chat_id,
                audio=audio,
                title=f"English - {voice_name}",
                caption=(
                    f"🎙 {voice_name}\n"
                    f"🇺🇸 English (US)"
                )
            )

        # حذف فایل
        if audio_file.exists():

            audio_file.unlink()

        # پاک کردن متن ذخیره‌شده
        context.user_data.pop(
            "text",
            None
        )

    except Exception as e:

        if audio_file.exists():

            audio_file.unlink()

        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=(
                "❌ هنگام ساخت فایل صوتی مشکلی پیش آمد.\n\n"
                f"{str(e)[:1500]}"
            )
        )


# =========================================================
# MAIN
# =========================================================

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

    app.add_handler(
        CallbackQueryHandler(
            voice_selected
        )
    )

    print(
        "Bot is running..."
    )

    app.run_polling()


if __name__ == "__main__":

    main()
