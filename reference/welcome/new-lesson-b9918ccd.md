<!-- CourseStack lesson '🎮 The Game Master' (slug new-lesson-b9918ccd), captured 2026-10-12 from /api/student/events/<EV>/take -->

# 🎮 The Game Master

The Huntress CTF 2026 event operates with a new mechanic: a **Game Master** acts as a broker for challenges, challenge artifacts, and convenient automatic answer submission when you have solved a challenge.

> [!IMPORTANT]
> The **Game Master** requires your verified player identity. You can use the authenticated proxy inside the CTF environment, or pair once and use the public HTTPS address from your own machine.

## Pair once, then play from any device

Open your **AI Homebase** terminal and run this one command:

```bash
curl -sS -X POST 'http://10.0.0.219/huntress-ctf-proxy?op=pair'
```

No JSON headers or request body are needed. The Game Master returns your personal
`token` and `expires_at`. Save the token privately: it is shown only once. You can
also ask your Homebase AI reviewer to help you pair, but keep the token out of
chat, screenshots, shared files and logs.

After pairing, use `https://2026.huntress.ctf.games/` with
`Authorization: Bearer <your-token>` from any compatible device. You can turn off
Homebase when you are done with it; Game Master requests no longer need the VM or
VPN. Private challenge targets may still require VPN, and AI/model or challenge VM
costs are separate.

Your token stays valid across daily challenge releases and Game Master updates.
Repeating the command returns `already_paired` and leaves your existing token
working. A lost token requires an explicit pairing reset through the proxy; do not
reset or rotate it as part of normal play. Event closure, expiry, revocation or a
team/enrollment change can end access. See **Automating Your Solves** for direct
requests and OpenAPI discovery.

### Replace a lost token

Lost your saved token? Open your **AI Homebase** terminal again and run:

```bash
curl -sS -X POST 'http://10.0.0.219/huntress-ctf-proxy?op=pair' \
  -H 'Content-Type: application/json' \
  --data '{"reset":true}'
```

Here, `reset` is a JSON boolean in the request body, not a URL parameter. The Game Master returns a new `token` and `expires_at`. **Your old token stops working immediately.** Save the new token privately and update any tools using the old one.

This replaces your access token; it does **not** reset your challenge progress, scores, or active timers. Only do this when you need a replacement, such as after losing your token or changing teams. Daily releases and Game Master updates do not need a reset.

The VPN configuration file is available for download on the very bottom of the **Systems** tab on the left-hand navigation.

The original authenticated Game Master proxy remains reachable within the CTF environment at this address:

```
http://10.0.0.219/huntress-ctf-proxy
```

Connection to the **Game Master** is prepared automatically inside the provided **AI Homebase** VM. The supported proxy URL already uses its private IP address, so you do **not** need to add anything to your hosts file.

If you connect through the player VPN and want a convenient shell variable, copy and paste:

```bash
export HUNTRESS_GAME_MASTER_URL='http://10.0.0.219/huntress-ctf-proxy'
curl -fsS "$HUNTRESS_GAME_MASTER_URL?op=list"
```

Keep the URL exactly as shown. Do not add a trailing slash before `?op=list` or any other query parameter.

> [!WARNING]
> We have observed cases where **GPT-6 Luna** receives a **404 error** while trying to reach the Game Master. If this happens, please confirm that the request uses the exact URL above **without a trailing `/`**. The proxy path is a little particular about that formatting, but correcting the URL should allow you to continue without restarting Homebase.

