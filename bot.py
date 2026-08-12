import asyncio
from playwright.async_api import async_playwright


async def main():

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
            ],
        )

        page = await browser.new_page(
            viewport={
                "width": 1440,
                "height": 900
            },
            locale="fa-IR",
        )

        print("🌐 Opening TTSMaker...", flush=True)

        try:

            await page.goto(
                "https://ttsmaker.com/fa",
                wait_until="domcontentloaded",
                timeout=60000,
            )

        except Exception as e:

            print(
                f"⚠️ Page load warning: {e}",
                flush=True
            )

        print(
            "✅ Page loaded or partially loaded.",
            flush=True
        )

        # صبر برای اجرای JavaScript سایت
        await page.wait_for_timeout(10000)

        # ==================================================
        # PAGE INFORMATION
        # ==================================================

        print("\n━━━━━━━━━━━━━━━━━━━━", flush=True)
        print("🔎 PAGE INFORMATION", flush=True)
        print("━━━━━━━━━━━━━━━━━━━━", flush=True)

        print(
            "URL:",
            page.url,
            flush=True
        )

        print(
            "TITLE:",
            await page.title(),
            flush=True
        )

        # ==================================================
        # PAGE TEXT
        # ==================================================

        print("\n━━━━━━━━━━━━━━━━━━━━", flush=True)
        print("📝 PAGE TEXT", flush=True)
        print("━━━━━━━━━━━━━━━━━━━━", flush=True)

        try:

            body_text = await page.locator(
                "body"
            ).inner_text(
                timeout=15000
            )

            print(
                body_text[:20000],
                flush=True
            )

        except Exception as e:

            print(
                "❌ Could not read page text:",
                e,
                flush=True
            )

        # ==================================================
        # INPUTS
        # ==================================================

        print("\n━━━━━━━━━━━━━━━━━━━━", flush=True)
        print("🔹 INPUTS", flush=True)
        print("━━━━━━━━━━━━━━━━━━━━", flush=True)

        inputs = await page.locator(
            "input"
        ).all()

        print(
            f"Total inputs: {len(inputs)}",
            flush=True
        )

        for i, element in enumerate(inputs):

            try:

                print(
                    f"#{i}",
                    "type=",
                    await element.get_attribute("type"),
                    "id=",
                    await element.get_attribute("id"),
                    "name=",
                    await element.get_attribute("name"),
                    "placeholder=",
                    await element.get_attribute(
                        "placeholder"
                    ),
                    flush=True
                )

            except Exception:
                pass

        # ==================================================
        # TEXTAREAS
        # ==================================================

        print("\n━━━━━━━━━━━━━━━━━━━━", flush=True)
        print("📝 TEXTAREAS", flush=True)
        print("━━━━━━━━━━━━━━━━━━━━", flush=True)

        textareas = await page.locator(
            "textarea"
        ).all()

        print(
            f"Total textareas: {len(textareas)}",
            flush=True
        )

        for i, element in enumerate(textareas):

            try:

                print(
                    f"#{i}",
                    "id=",
                    await element.get_attribute("id"),
                    "name=",
                    await element.get_attribute("name"),
                    "placeholder=",
                    await element.get_attribute(
                        "placeholder"
                    ),
                    flush=True
                )

            except Exception:
                pass

        # ==================================================
        # SELECTS
        # ==================================================

        print("\n━━━━━━━━━━━━━━━━━━━━", flush=True)
        print("🎙 SELECTS", flush=True)
        print("━━━━━━━━━━━━━━━━━━━━", flush=True)

        selects = await page.locator(
            "select"
        ).all()

        print(
            f"Total SELECTs: {len(selects)}",
            flush=True
        )

        for i, select in enumerate(selects):

            try:

                select_id = await select.get_attribute(
                    "id"
                )

                select_name = await select.get_attribute(
                    "name"
                )

                current_value = await select.input_value()

                print(
                    f"\nSELECT #{i}",
                    flush=True
                )

                print(
                    "ID:",
                    select_id,
                    flush=True
                )

                print(
                    "Name:",
                    select_name,
                    flush=True
                )

                print(
                    "Value:",
                    current_value,
                    flush=True
                )

                options = await select.locator(
                    "option"
                ).all()

                print(
                    "Options:",
                    len(options),
                    flush=True
                )

                for option in options:

                    try:

                        option_text = (
                            await option.inner_text()
                        ).strip()

                        option_value = (
                            await option.get_attribute(
                                "value"
                            )
                        )

                        if option_text:

                            print(
                                f"• {option_text} | value={option_value}",
                                flush=True
                            )

                    except Exception:
                        pass

            except Exception as e:

                print(
                    f"⚠️ SELECT #{i} error:",
                    e,
                    flush=True
                )

        # ==================================================
        # BUTTONS
        # ==================================================

        print("\n━━━━━━━━━━━━━━━━━━━━", flush=True)
        print("🔘 BUTTONS", flush=True)
        print("━━━━━━━━━━━━━━━━━━━━", flush=True)

        buttons = await page.locator(
            "button"
        ).all()

        print(
            f"Total buttons: {len(buttons)}",
            flush=True
        )

        for i, button in enumerate(buttons):

            try:

                button_text = (
                    await button.inner_text()
                ).strip()

                print(
                    f"#{i}",
                    f"text={button_text!r}",
                    "id=",
                    await button.get_attribute("id"),
                    "name=",
                    await button.get_attribute("name"),
                    "aria=",
                    await button.get_attribute(
                        "aria-label"
                    ),
                    "title=",
                    await button.get_attribute(
                        "title"
                    ),
                    flush=True
                )

            except Exception:
                pass

        # ==================================================
        # LINKS
        # ==================================================

        print("\n━━━━━━━━━━━━━━━━━━━━", flush=True)
        print("🔗 LINKS", flush=True)
        print("━━━━━━━━━━━━━━━━━━━━", flush=True)

        links = await page.locator(
            "a"
        ).all()

        print(
            f"Total links: {len(links)}",
            flush=True
        )

        for i, link in enumerate(links):

            try:

                link_text = (
                    await link.inner_text()
                ).strip()

                href = await link.get_attribute(
                    "href"
                )

                if link_text or href:

                    print(
                        f"#{i}",
                        f"text={link_text!r}",
                        f"href={href!r}",
                        flush=True
                    )

            except Exception:
                pass

        # ==================================================
        # SEARCH FOR PERSIAN
        # ==================================================

        print("\n━━━━━━━━━━━━━━━━━━━━", flush=True)
        print("🇮🇷 PERSIAN SEARCH", flush=True)
        print("━━━━━━━━━━━━━━━━━━━━", flush=True)

        try:

            content = await page.content()

            keywords = [
                "Persian",
                "فارسی",
                "Iran",
                "fa-IR",
                "fa_IR",
                "🔥",
            ]

            found = False

            for keyword in keywords:

                if keyword.lower() in content.lower():

                    print(
                        f"✅ FOUND: {keyword}",
                        flush=True
                    )

                    found = True

            if not found:

                print(
                    "❌ Persian keywords not found.",
                    flush=True
                )

        except Exception as e:

            print(
                "⚠️ Persian search error:",
                e,
                flush=True
            )

        # ==================================================
        # SAVE HTML
        # ==================================================

        print("\n━━━━━━━━━━━━━━━━━━━━", flush=True)
        print("💾 SAVING HTML", flush=True)
        print("━━━━━━━━━━━━━━━━━━━━", flush=True)

        try:

            html = await page.content()

            with open(
                "ttsmaker_page.html",
                "w",
                encoding="utf-8"
            ) as file:

                file.write(html)

            print(
                "✅ ttsmaker_page.html saved.",
                flush=True
            )

        except Exception as e:

            print(
                "❌ Could not save HTML:",
                e,
                flush=True
            )

        # ==================================================

        await browser.close()

        print(
            "\n🏁 SCAN FINISHED.",
            flush=True
        )


if __name__ == "__main__":

    asyncio.run(main())
