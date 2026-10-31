# Read-only capture of the CourseStack (ctf.huntress.com) points scoreboard for the retrospective.
# Runs with the WINDOWS Python against the logged-in Chromium (browser/launch.py, CDP 9222):
#   python.exe \\wsl.localhost\Ubuntu\home\testpwn\huntress-2026\reference\writeup\cs_scoreboard.py [url ...]
# Saves every JSON /api/ response seen while visiting the pages, a screenshot, and the page links.
import json
import os
import re
import sys
import time

from playwright.sync_api import sync_playwright

OUT = r"\\wsl.localhost\Ubuntu\home\testpwn\huntress-2026\reference\writeup\data\coursestack"
os.makedirs(OUT, exist_ok=True)
urls = sys.argv[1:] or ["https://ctf.huntress.com/"]

with sync_playwright() as p:
    ctx = p.chromium.connect_over_cdp("http://127.0.0.1:9222").contexts[0]
    page = ctx.new_page()
    seen = []

    def on_resp(r):
        if ("/api/" in r.url or "score" in r.url) and "json" in (r.headers.get("content-type") or ""):
            try:
                seen.append({"url": r.url, "status": r.status, "body": r.json()})
            except Exception:
                pass

    page.on("response", on_resp)
    for i, u in enumerate(urls):
        try:
            page.goto(u, wait_until="commit", timeout=60000)
        except Exception as e:
            print("goto:", e)
        time.sleep(40)
        page.screenshot(path=os.path.join(OUT, f"page{i}.png"), full_page=True)
        links = page.eval_on_selector_all("a[href]", "els => els.map(e => [e.innerText.trim(), e.href])")
        with open(os.path.join(OUT, f"page{i}_links.json"), "w", encoding="utf-8") as f:
            json.dump({"url": page.url, "links": links}, f, indent=1)
        with open(os.path.join(OUT, f"page{i}_text.txt"), "w", encoding="utf-8") as f:
            f.write(page.inner_text("body"))
    with open(os.path.join(OUT, "api_responses.json"), "w", encoding="utf-8") as f:
        json.dump(seen, f, indent=1)
    for s in seen:
        print(s["status"], s["url"][:160])
    page.close()
