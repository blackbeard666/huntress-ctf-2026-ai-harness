# One-off: submit a free-text answer to a CourseStack lesson question via the take UI, and capture the API call.
# Usage (Windows python): python.exe lesson_submit.py <lesson-slug> <answer>
import sys

from playwright.sync_api import sync_playwright

EVENT = "92371a95-2ab9-46eb-8f6f-c676bceeed62"
slug, answer = sys.argv[1], sys.argv[2]
URL = f"https://ctf.huntress.com/events/{EVENT}/take/{slug}"

with sync_playwright() as p:
    ctx = p.chromium.connect_over_cdp("http://127.0.0.1:9222").contexts[0]
    pg = ctx.new_page()
    pg.set_default_timeout(120000)
    calls = []

    def on_resp(r):
        rq = r.request
        if (rq.resource_type in ("fetch", "xhr") and rq.method in ("POST", "PUT", "PATCH")
                and "ctf.huntress.com" in r.url and not any(x in r.url for x in ("heartbeat", "monitoring", "collect"))):
            try:
                body = r.text()[:500]
            except Exception:
                body = "?"
            calls.append(f"{rq.method} {r.status} {r.url}\n    REQ {(rq.post_data or '')[:300]}\n    RES {body}")

    pg.on("response", on_resp)
    try:
        pg.goto(URL, wait_until="commit", timeout=120000)
    except Exception as e:
        print("goto note:", str(e)[:100], flush=True)
    pg.wait_for_selector("input[type=text], textarea", timeout=120000)
    inp = pg.query_selector("input[type=text], textarea")
    inp.scroll_into_view_if_needed()
    inp.fill(answer)
    clicked = None
    for b in pg.query_selector_all("button"):
        if b.is_visible() and b.inner_text().strip().lower() in (
                "submit", "check", "answer", "submit answer", "check answer", "submit flag"):
            b.click()
            clicked = b.inner_text().strip()
            break
    print("clicked:", clicked, flush=True)
    if not clicked:
        print("visible buttons:", [b.inner_text().strip() for b in pg.query_selector_all("button") if b.is_visible()][:15], flush=True)
    pg.wait_for_timeout(6000)
    print("=== calls ===")
    print("\n".join(dict.fromkeys(calls)) or "(none captured)")
    pg.close()
