# Usage (Windows Python): python.exe snap.py [url] -> prints url/title/visible text of the CourseStack tab
# and saves a full-page screenshot to <project>/.run/tmp/snap.png
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parent.parent / ".run" / "tmp" / "snap.png"
with sync_playwright() as p:
    page = p.chromium.connect_over_cdp("http://127.0.0.1:9222").contexts[0].pages[0]
    if len(sys.argv) > 1:
        page.goto(sys.argv[1], wait_until="domcontentloaded")
        page.wait_for_timeout(2500)
    print("URL:", page.url)
    print("TITLE:", page.title())
    page.screenshot(path=str(OUT), full_page=True)
    print(page.inner_text("body")[:6000])
