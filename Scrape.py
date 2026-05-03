from playwright.sync_api import sync_playwright
import pandas as pd
import time

url = "https://www.mobilelegends.com/rank"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(url, wait_until="networkidle", timeout=60000)

    # Scroll multiple times to load all heroes
    for _ in range(10):  # increase if needed
        page.mouse.wheel(0, 5000)
        time.sleep(2)

    page.wait_for_timeout(5000)

    text = page.locator("body").inner_text()
    browser.close()

lines = [line.strip() for line in text.splitlines() if line.strip()]

start = 19
data = []

for i in range(start, len(lines), 5):
    chunk = lines[i:i+5]

    if len(chunk) < 5:
        break

    rank, hero, pick_rate, win_rate, ban_rate = chunk

    if rank.isdigit():
        data.append({
            "rank": int(rank),
            "hero": hero,
            "pick_rate": pick_rate,
            "win_rate": win_rate,
            "ban_rate": ban_rate
        })

df = pd.DataFrame(data)

print(df)
df.to_csv("mobile_legends_rank_stats.csv", index=False)
