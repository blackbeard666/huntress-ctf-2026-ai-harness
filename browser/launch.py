# Long-lived headed Chromium for the CourseStack session, with CDP on 127.0.0.1:9222.
# Run with the WINDOWS Python (Chromium is a Windows app):
#   python.exe \\wsl.localhost\Ubuntu\home\testpwn\huntress-2026\browser\launch.py
# hctf/hbpower.py attaches to it with connect_over_cdp to control the Homebase VM and read credits.
#
# The one thing outside the project: Chromium cannot keep its profile on the WSL share. A UNC path is
# silently rewritten to C:\wsl.localhost\..., and a mapped drive silently falls back to a temp profile.
# So the logged-in profile stays on a local Windows disk.
import time

from playwright.sync_api import sync_playwright

PROFILE = r"C:\Users\cavila\Desktop\ctf\huntress-2026\.browser\profile"
CHROME = "C:/Users/cavila/AppData/Local/ms-playwright/chromium-1243/chrome-win64/chrome.exe"

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        PROFILE, headless=False, executable_path=CHROME, viewport={"width": 1400, "height": 900},
        args=["--remote-debugging-port=9222"])
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.goto("https://ctf.huntress.com/")
    print("BROWSER_READY", flush=True)
    while ctx.pages:
        time.sleep(2)
