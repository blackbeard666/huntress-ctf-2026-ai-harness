# Read-only GETs of the CourseStack scoreboard API through the logged-in Chromium (CDP 9222), like hctf/hbpower.py.
#   python.exe \\wsl.localhost\Ubuntu\home\testpwn\huntress-2026\reference\writeup\cs_api.py
import json
import os

from playwright.sync_api import sync_playwright

OUT = r"\\wsl.localhost\Ubuntu\home\testpwn\huntress-2026\reference\writeup\data\coursestack"
EV = "92371a95-2ab9-46eb-8f6f-c676bceeed62"
H = "https://ctf.huntress.com/api"
PATHS = {
    "huntress_scoreboard": f"{H}/student/huntress/scoreboard",
    "event_scoreboard": f"{H}/student/events/{EV}/scoreboard",
    "public_event_scoreboard": f"{H}/events/{EV}/scoreboard",
}

with sync_playwright() as p:
    rq = p.chromium.connect_over_cdp("http://127.0.0.1:9222").contexts[0].request
    for name, url in PATHS.items():
        r = rq.get(url, timeout=120000)
        body = r.body()
        print(name, r.status, len(body))
        if r.ok:
            with open(os.path.join(OUT, f"{name}.json"), "wb") as f:
                f.write(body)
