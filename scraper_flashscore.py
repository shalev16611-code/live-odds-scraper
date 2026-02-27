from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
import time
import requests

API_URL = "http://127.0.0.1:8000/api/update-odds"

def scrape():
    print("SCRAPER STARTED")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--start-maximized"]
        )

        page = browser.new_page()
        Stealth().apply_stealth_sync(page)

        print("Opening Flashscore...")
        page.goto("https://www.flashscore.com/football/")

        # קבלת cookies אם מופיע
        try:
            page.get_by_role("button", name="Accept").click(timeout=3000)
            print("Cookies accepted")
        except:
            pass

        print("Waiting full load...")
        page.wait_for_timeout(15000)

        print("Scrolling page...")
        for _ in range(10):
            page.mouse.wheel(0, 8000)
            time.sleep(2)

        page.wait_for_selector(".event__match", timeout=30000)

        matches = page.locator(".event__match")
        count = matches.count()

        print("MATCH BLOCKS FOUND:", count)

        data = []

        for i in range(count):
            try:
                match = matches.nth(i)

                # 👇 שליפת קבוצות לפי מבנה החדש
                home_el = match.locator(".event__homeParticipant")
                away_el = match.locator(".event__awayParticipant")

                if home_el.count() == 0 or away_el.count() == 0:
                    continue

                home = home_el.inner_text().strip()
                away = away_el.inner_text().strip()

                if not home or not away:
                    continue

                time_txt = ""
                time_el = match.locator(".event__time")
                if time_el.count():
                    time_txt = time_el.inner_text().strip()

                print(f"{time_txt} | {home} vs {away}")

                data.append({
                    "home": home,
                    "away": away,
                    "time": time_txt
                })

            except Exception as e:
                print("skip match", i, e)
                continue

        print("REAL MATCHES COLLECTED:", len(data))

        if data:
            print("Sending to API...")
            r = requests.post(API_URL, json=data)
            print("API STATUS:", r.status_code)
        else:
            print("NO DATA TO SEND")

        time.sleep(5)
        browser.close()

scrape()