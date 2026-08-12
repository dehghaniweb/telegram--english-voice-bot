import asyncio
from playwright.async_api import async_playwright


async def main():

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=True
        )

        page = await browser.new_page()

        print("🌐 Opening TTSMaker...")

        await page.goto(
            "https://ttsmaker.com/fa",
            wait_until="domcontentloaded",
            timeout=60000
        )

        await page.wait_for_timeout(5000)

        print("✅ TTSMaker opened.")

        # پیدا کردن SELECT ها
        selects = await page.locator("select").all()

        print(f"\n🎙 تعداد SELECT ها: {len(selects)}")

        for i, select in enumerate(selects):

            try:
                element_id = await select.get_attribute("id")
                value = await select.input_value()

                print("\n━━━━━━━━━━━━━━━━━━━━")
                print(f"SELECT #{i}")
                print(f"ID: {element_id}")
                print(f"Value: {value}")

                options = await select.locator("option").all()

                print(f"Options: {len(options)}")

                for option in options:

                    text = (await option.inner_text()).strip()
                    value = await option.get_attribute("value")

                    if text:
                        print(
                            f"• {text} | value={value}"
                        )

            except Exception as e:

                print(
                    f"⚠️ Error reading SELECT #{i}: {e}"
                )

        # بررسی متن صفحه برای فارسی
        body_text = await page.locator("body").inner_text()

        print("\n━━━━━━━━━━━━━━━━━━━━")
        print("🔎 بررسی Persian / فارسی")
        print("━━━━━━━━━━━━━━━━━━━━")

        if "Persian" in body_text or "فارسی" in body_text:

            print("✅ Persian language detected.")

        else:

            print("❌ Persian language not detected.")

        await browser.close()

        print("\n🏁 Scan finished.")


if __name__ == "__main__":
    asyncio.run(main())
