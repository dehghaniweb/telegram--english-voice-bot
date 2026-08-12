import asyncio
from playwright.async_api import async_playwright


async def main():

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
        )

        page = await browser.new_page(
            viewport={"width": 1440, "height": 900},
            locale="fa-IR",
        )

        print("🌐 Opening TTSMaker...")

        await page.goto(
            "https://ttsmaker.com/fa",
            wait_until="networkidle",
            timeout=90000,
        )

        print("✅ Page loaded.")

        await page.wait_for_timeout(10000)

        print("\n━━━━━━━━━━━━━━━━━━━━")
        print("🔎 PAGE INFORMATION")
        print("━━━━━━━━━━━━━━━━━━━━")

        print("URL:", page.url)

        title = await page.title()
        print("TITLE:", title)

        # --------------------------------------------------
        # TEXT
        # --------------------------------------------------

        text = await page.locator("body").inner_text()

        print("\n━━━━━━━━━━━━━━━━━━━━")
        print("📝 PAGE TEXT")
        print("━━━━━━━━━━━━━━━━━━━━")

        print(text[:15000])

        # --------------------------------------------------
        # INPUTS
        # --------------------------------------------------

        inputs = await page.locator("input").all()

        print("\n━━━━━━━━━━━━━━━━━━━━")
        print(f"🔹 INPUTS: {len(inputs)}")
        print("━━━━━━━━━━━━━━━━━━━━")

        for i, element in enumerate(inputs):

            try:

                print(
                    i,
                    "type=",
                    await element.get_attribute("type"),
                    "id=",
                    await element.get_attribute("id"),
                    "name=",
                    await element.get_attribute("name"),
                    "placeholder=",
                    await element.get_attribute("placeholder"),
                )

            except Exception:
                pass

        # --------------------------------------------------
        # TEXTAREAS
        # --------------------------------------------------

        textareas = await page.locator("textarea").all()

        print("\n━━━━━━━━━━━━━━━━━━━━")
        print(f"📝 TEXTAREAS: {len(textareas)}")
        print("━━━━━━━━━━━━━━━━━━━━")

        for i, element in enumerate(textareas):

            try:

                print(
                    i,
                    "id=",
                    await element.get_attribute("id"),
                    "name=",
                    await element.get_attribute("name"),
                    "placeholder=",
                    await element.get_attribute("placeholder"),
                )

            except Exception:
                pass

        # --------------------------------------------------
        # SELECTS
        # --------------------------------------------------

        selects = await page.locator("select").all()

        print("\n━━━━━━━━━━━━━━━━━━━━")
        print(f"🎙 SELECTS: {len(selects)}")
        print("━━━━━━━━━━━━━━━━━━━━")

        for i, select in enumerate(selects):

            try:

                print(
                    f"\nSELECT #{i}",
                    "id=",
                    await select.get_attribute("id"),
                    "name=",
                    await select.get_attribute("name"),
                )

                options = await select.locator("option").all()

                print(
                    "Options:",
                    len(options)
                )

                for option in options:

                    text_option = (
                        await option.inner_text()
                    ).strip()

                    value = (
                        await option.get_attribute(
                            "value"
                        )
                    )

                    if text_option:

                        print(
                            f"• {text_option} | value={value}"
                        )

            except Exception as e:

                print(
                    "ERROR:",
                    e
                )

        # --------------------------------------------------
        # BUTTONS
        # --------------------------------------------------

        buttons = await page.locator("button").all()

        print("\n━━━━━━━━━━━━━━━━━━━━")
        print(f"🔘 BUTTONS: {len(buttons)}")
        print("━━━━━━━━━━━━━━━━━━━━")

        for i, button in enumerate(buttons):

            try:

                text_button = (
                    await button.inner_text()
                ).strip()

                print(
                    f"#{i} text={text_button!r}",
                    "id=",
                    await button.get_attribute("id"),
                    "aria=",
                    await button.get_attribute(
                        "aria-label"
                    ),
                )

            except Exception:
                pass

        # --------------------------------------------------
        # SAVE HTML
        # --------------------------------------------------

        html = await page.content()

        with open(
            "ttsmaker_page.html",
            "w",
            encoding="utf-8"
        ) as f:

            f.write(html)

        print(
            "\n💾 HTML saved to ttsmaker_page.html"
        )

        # --------------------------------------------------

        await browser.close()

        print("\n🏁 SCAN FINISHED.")


if __name__ == "__main__":

    asyncio.run(main())
