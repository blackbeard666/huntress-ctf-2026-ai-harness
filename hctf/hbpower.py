# Homebase VM power and credit balance through the CourseStack API.
# Runs with the WINDOWS Python: it borrows the logged-in Chromium session (CDP on 127.0.0.1:9222,
# started by .browser/launch.py), so no CourseStack credentials are stored anywhere.
# Usage: python.exe hbpower.py on|off|status   -> prints {"state": ..., "credits": ..., "ip": ...}
import json
import sys
import time

from playwright.sync_api import sync_playwright

PT, SYSID = "36fc3c4d-796f-47ba-880f-9362883f7909", "aaf8fe6c-081c-4db9-8dbc-4ee4939f2694"
EV, CUST = "92371a95-2ab9-46eb-8f6f-c676bceeed62", "f846c680-8c3f-4777-b41c-9b965949101e"
H = "https://ctf.huntress.com/api/student"

with sync_playwright() as p:
    rq = p.chromium.connect_over_cdp("http://127.0.0.1:9222").contexts[0].request

    def system():
        return rq.get(f'{H}/courses/{PT}/systems?courseSystemIds=["{SYSID}"]').json()["systems"][0]["system"]

    def credits():
        # The UI's "N credits remaining" = unused included runtime + purchased credit hours.
        t = rq.get(f"{H}/events/{EV}/take").json()["course"]
        c = rq.get(f"{H}/credits/{CUST}").json()
        used, included = t["course_gb_seconds"], t["course_playthrough"]["included_runtime_gb_seconds"]
        return round((included - used) / 3600 + c["remaining_credit_hours"], 3)

    act = sys.argv[1] if len(sys.argv) > 1 else "status"
    if act in ("on", "off"):
        rq.post(f"{H}/courses/{PT}/systems/{SYSID}/power", data={"power": act})
        want = "running" if act == "on" else "stopped"
        for _ in range(72):
            if system()["state"] == want:
                break
            time.sleep(5)
    s = system()
    print(json.dumps({"state": s["state"], "ip": s["ip"], "credits": credits()}))
