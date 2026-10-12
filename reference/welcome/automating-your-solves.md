<!-- CourseStack lesson '🤖 Automating Your Solves' (slug -automating-your-solves), captured 2026-10-12 from /api/student/events/<EV>/take -->

# 🤖 Automating Your Solves

Single Solve is a good place to learn how a challenge works. On supported Time Trial and Mastery routes, a normal attempt is untimed and still earns the flag and CourseStack points. When you are ready to race the clock, set `"run_for_time":true` on a start or retry request. A script that talks directly to the Game Master helps you solve each fresh assigned artifact quickly and reliably.

> [!IMPORTANT]
> **There are two submission paths.** If a lesson presents a native CourseStack question field or explicitly asks you to enter a returned flag there—such as **Read the Rules** or **Welcome Robots**—submit through that lesson page. Game Master challenge modes that return `answer_ids` are submitted through the Game Master API below; the Game Master validates those answers and automatically completes the corresponding CourseStack question. CourseStack remains the official scoring ledger, so if the Game Master reports `"status":"pending"`, verify the points in CourseStack before treating the challenge as fully scored.

## Endpoint

```
http://10.0.0.219/huntress-ctf-proxy
```

This proxy address is only reachable from inside the CTF environment — your **AI Homebase**, or your own machine connected over the player VPN. It will not resolve from the public internet.

Use the URL without a trailing slash. Append query parameters directly, for example
`http://10.0.0.219/huntress-ctf-proxy?op=list`, and send JSON POST requests to the
same base URL. In shell commands, quote the complete URL so `&` stays in the query.

### Use your own machine after pairing

From your authenticated Homebase, make one `POST` to
`http://10.0.0.219/huntress-ctf-proxy?op=pair`. No JSON header or body is needed:

```bash
curl -sS -X POST 'http://10.0.0.219/huntress-ctf-proxy?op=pair'
```

The Game Master returns your personal token once. Keep it
private. Then you can shut down Homebase and send the same Game Master operations
to `https://2026.huntress.ctf.games/` from your own machine, adding
`Authorization: Bearer <your-token>` to each request. Game Master access no longer
requires the Homebase VM or VPN after pairing. Private challenge targets may still
require the VPN, and using Homebase or event-provided AI still uses credits.

Do not paste the token into chat, Discord, a shared script, or a command recorded
in shell history. If you lose it, an ordinary pairing request will not reveal it
again; reconnect through CourseStack and explicitly reset the pairing. A token
stays tied to the team or solo playthrough that received it, so reconnect and
reset it after a team change.

### Replace a lost token

From your authenticated **AI Homebase** terminal:

```bash
curl -sS -X POST 'http://10.0.0.219/huntress-ctf-proxy?op=pair' \
  -H 'Content-Type: application/json' \
  --data '{"reset":true}'
```

Use the JSON boolean `true` in the body, not `?reset=true` in the URL. This returns a new token once and immediately invalidates the old one. Save the replacement privately and update your scripts' saved credential. A direct bearer request cannot reset or mint tokens.

Your challenge progress, scores, and active timers stay in place. Do not reset as part of normal play or after an update.

### Connect directly

Read your saved token privately in your own Bash terminal, then list challenges:

```bash
read -rsp 'Game Master token: ' HUNTRESS_GM_TOKEN; printf '\n'
printf 'header = "Authorization: Bearer %s"\n' "$HUNTRESS_GM_TOKEN" |
  curl -sS --config - 'https://2026.huntress.ctf.games/?op=list'
```

Reuse this Authorization header for start, status, artifact download and submit.
Gameplay POSTs still use JSON. The `--config -` pattern keeps the bearer out of
curl's process arguments. Clear your shell variable with `unset HUNTRESS_GM_TOKEN`
when finished. Updates and new challenge days do not require another token.

Your AI can discover the current API with `GET ?op=openapi` through the proxy or
your paired direct connection. It documents the empty-body pairing request,
`token`/`expires_at` response and direct bearer authentication. Only the genuine
proxy can bootstrap or explicitly reset a token; a bearer cannot mint another.

## Operations

| Operation | Request |
|---|---|
| List challenges | `GET ?op=list` |
| Filter by day and lane | `GET ?op=list&day=1&lane=warmups` |
| Start or reconnect to an attempt | `POST {"challenge":"<id>"}` |
| Opt into a timed ranking attempt | `POST {"challenge":"<id>","run_for_time":true}` on a route advertising `run_for_time_supported` |
| Retry after the current attempt ends | `POST {"op":"retry","challenge":"<id>","run_for_time":true}` for a timed run; omit `run_for_time` for ordinary untimed play on supported routes |
| Check status | `GET ?op=status&challenge=<id>` |
| Download artifact | `GET ?op=artifact&challenge=<id>` |
| Submit answers | `POST {"challenge":"<id>","answers":{"<answer-id>":"<answer>"}}` |
| Pair once through the authenticated proxy | `POST ?op=pair` (no header or body required) |
| Replace a token through the authenticated proxy | `POST ?op=pair` with JSON `{"reset":true}` |

Send POST requests with `Content-Type: application/json`.

The start response returns `answer_ids`. Use those exact values as the keys in `answers`.

Check `op=list` for `run_for_time_supported`. Older routes without it still start timed by default; the Time Trial and Mastery Mode lesson explains both contracts and what happens when fresh variants run out. Repeating `start` reconnects to the current attempt; it never spends another variant.

Submit returns `"CORRECT"`, `"incorrect"`, or `"accepted"` (partial progress — check `remaining`).

## Example

This simplified example targets the Day 1 Warmups challenge **A Little Based**, whose downloaded text contains a Base64-encoded answer. Other challenges may return archives, applications, or live targets that require different analysis.

```python
import base64, os, requests

token = os.environ.get("HUNTRESS_GM_TOKEN")
GM = "https://2026.huntress.ctf.games/" if token else "http://10.0.0.219/huntress-ctf-proxy"
session = requests.Session()
if token:
    session.headers["Authorization"] = "Bearer " + token

challenges = session.get(GM, params={
    "op": "list", "day": 1, "lane": "warmups"
}).json()["challenges"]

cid = challenges[0]["id"]
answer_id = session.post(GM, json={"challenge": cid}).json()["answer_ids"][0]

answer = base64.b64decode(
    session.get(GM, params={"op": "artifact", "challenge": cid}).content
).decode().strip()

result = session.post(GM, json={
    "challenge": cid,
    "answers": {answer_id: answer},
}).json()

print(result["result"])  # CORRECT
```

