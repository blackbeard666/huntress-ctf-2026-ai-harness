"""Flowcharts for the harness-internals writeup, drawn as theme-native inline SVG.

Each chart is data: nodes on a grid (column, row) and edges between them. `flow()` lays them out, routes the edges
orthogonally, and returns a <figure> with a table view that links every step to its code in the public repo.
Classes come from the theme (hc-node, hc-node-ours = red, hc-node-plat = green, hc-edge, hc-rowlab), so the
charts follow light/dark mode and the two-accent rule. No inline styles (the site's CSP forbids them): fills use
presentation attributes.
"""

REPO = "https://github.com/blackbeard666/huntress-ctf-2026-ai-harness/blob/HEAD/"
PAD = 64         # outer padding (room for loop-back edges and their labels)
GAP = 44         # horizontal gap between boxes (room for a yes/no label)
RH = 96          # row pitch
BH = 62          # box height


def flow(E, figure, table, cid, title, desc, cols, nodes, edges, caption, width=960):
    """nodes: {id: N(...)}; edges: [(src, dst, label, route[, gutter])].
    route: None = auto (same row: horizontal; otherwise vertical / elbow from the source's bottom or top)
           'right' / 'left' = loop out of that side, along a gutter, into the target's same side
           'vh' = down (or up) from the source to the target's middle, then across into its near side
           'hv' = across from the source's side to the target's centre, then down (or up) into it."""
    W = width
    cw = (W - 2 * PAD) / cols
    rows = max(n["r"] for n in nodes.values()) + 1
    h = PAD + 10 + rows * RH - (RH - BH) + 14

    def box(n):
        x = PAD + n["c"] * cw + GAP / 2
        w = cw * n.get("span", 1) - GAP
        y = 12 + n["r"] * RH
        return x, y, w, BH

    geo = {k: box(n) for k, n in nodes.items()}
    out = [f'<defs><marker id="ar-{cid}" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" '
           'orient="auto-start-reverse"><path class="hc-arrowhead" d="M0,0L8,4L0,8z"/></marker></defs>']

    def lab(x, y, t, anchor="start"):
        return f'<text class="hc-rowlab" x="{x:.0f}" y="{y:.0f}" text-anchor="{anchor}">{E(t)}</text>'

    for e in edges:
        src, dst, label, route = e[:4]
        gut = e[4] if len(e) > 4 else 18
        ax, ay, aw, ah = geo[src]
        bx, by, bw, bh = geo[dst]
        acx, acy, bcx, bcy = ax + aw / 2, ay + ah / 2, bx + bw / 2, by + bh / 2
        if route in ("right", "left"):
            side = 1 if route == "right" else -1
            sx = ax + aw if side > 0 else ax
            tx = bx + bw if side > 0 else bx
            gx = (max(sx, tx) + gut) if side > 0 else (min(sx, tx) - gut)
            d = f"M{sx:.0f},{acy:.0f} H{gx:.0f} V{bcy:.0f} H{tx + 2 * side:.0f}"
            lx, ly, anc = gx + 5 * side, (acy + bcy) / 2, "start" if side > 0 else "end"
        elif route == "vh":
            down = bcy > acy
            y0 = ay + ah if down else ay
            tx = bx + bw + 2 if bcx < acx else bx - 2
            d = f"M{acx:.0f},{y0:.0f} V{bcy:.0f} H{tx:.0f}"
            lx, ly, anc = acx + 6, y0 + (16 if down else -8), "start"
        elif route == "hv":
            right = bcx > acx
            sx = ax + aw if right else ax
            ty = by - 2 if bcy > acy else by + bh + 2
            d = f"M{sx:.0f},{acy:.0f} H{bcx:.0f} V{ty:.0f}"
            lx, ly, anc = sx + (6 if right else -6), acy - 7, "start" if right else "end"
        elif abs(acy - bcy) < 1:
            if bx > ax:
                d = f"M{ax + aw:.0f},{acy:.0f} H{bx - 2:.0f}"
                lx = (ax + aw + bx) / 2
            else:
                d = f"M{ax:.0f},{acy:.0f} H{bx + bw + 2:.0f}"
                lx = (ax + bx + bw) / 2
            ly, anc = acy - 7, "middle"
        elif bcy > acy:
            if abs(acx - bcx) < 1:
                d = f"M{acx:.0f},{ay + ah:.0f} V{by - 2:.0f}"
            else:
                ym = ay + ah + (by - ay - ah) / 2
                d = f"M{acx:.0f},{ay + ah:.0f} V{ym:.0f} H{bcx:.0f} V{by - 2:.0f}"
            lx, ly, anc = acx + 7, ay + ah + 16, "start"
        else:
            if abs(acx - bcx) < 1:
                d = f"M{acx:.0f},{ay:.0f} V{by + bh + 2:.0f}"
            else:
                ym = by + bh + (ay - by - bh) / 2
                d = f"M{acx:.0f},{ay:.0f} V{ym:.0f} H{bcx:.0f} V{by + bh + 2:.0f}"
            lx, ly, anc = acx + 7, ay - 8, "start"
        out.append(f'<path class="hc-edge" fill="none" d="{d}" marker-end="url(#ar-{cid})"/>')
        if label:
            out.append(lab(lx, ly, label, anc))

    for k, n in nodes.items():
        x, y, w, hh = geo[k]
        cls = f"hc-node hc-node-{n['cls']}" if n.get("cls") else "hc-node"
        kind = n.get("k", "box")
        if kind == "dec":
            shape = (f'<polygon points="{x + 14:.0f},{y:.0f} {x + w - 14:.0f},{y:.0f} {x + w:.0f},{y + hh / 2:.0f} '
                     f'{x + w - 14:.0f},{y + hh:.0f} {x + 14:.0f},{y + hh:.0f} {x:.0f},{y + hh / 2:.0f}"/>')
            tx = x + 24
        elif kind == "end":
            shape = f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{hh}" rx="{hh / 2:.0f}"/>'
            tx = x + 26
        else:
            shape = f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{hh}"/>'
            tx = x + 14
        subs = n.get("s") or []
        ty = y + (23 if subs else hh / 2 + 5)
        txt = f'<text class="hc-node-t" x="{tx:.0f}" y="{ty:.0f}">{E(n["t"])}</text>'
        for i, line in enumerate(subs[:2]):
            txt += f'<text class="hc-node-s" x="{tx:.0f}" y="{y + 41 + i * 14:.0f}">{E(line)}</text>'
        out.append(f'<g class="{cls}"><title>{E(n["t"])}: {E(" ".join(subs))}</title>{shape}{txt}</g>')

    def code(n):
        f = n.get("f")
        if not f:
            return "-"
        return ", ".join(f'<a href="{REPO}{p}"><code>{E(p)}</code></a>' for p in f.split(","))

    order = sorted(nodes.values(), key=lambda n: (n["r"], n["c"]))
    rows_t = [(E(n["t"]), E(n.get("d") or " ".join(n.get("s") or [])), code(n)) for n in order]
    return figure(cid, title, desc, W, int(h), "".join(out), caption,
                  table(("step", "what happens", "code"), rows_t, summary="steps and code"))


def N(c, r, t, s=(), k="box", cls="", f=None, d=None, span=1):
    return dict(c=c, r=r, t=t, s=list(s) if not isinstance(s, str) else [s], k=k, cls=cls, f=f, d=d, span=span)


def build(E, figure, table):
    F = lambda *a, **k: flow(E, figure, table, *a, **k)
    out = {}

    # 1 ---------------------------------------------------------------- the whole orchestration
    out["fl-orch"] = F(
        "fl-orch", "The whole orchestration, one day",
        "Warm-up and preflight, arming the launch, polling for the release, one chain per challenge, the operator's "
        "monitoring loop, the GM-solved gate, then the post-run, post-mortem, fixes and rehearsal.", 3,
        {
            "warm": N(0, 0, "warm-up", ["the operator session", "(Claude Code) starts the day"], "end", "ours",
                      "bin/preflight.sh", "A long-running Claude Code session that I talk to; it never solves a challenge."),
            "pf": N(0, 1, "preflight green?", ["~78 checks in 11 sections, incl.", "the fault-replay suite"], "dec", "",
                    "bin/preflight.sh,tests/test_fault_replay.py", "A red check or a red fault suite is a FAIL."),
            "fix": N(1, 1, "fix the cause", ["e.g. --fix kills a duplicate VPN", "client; then preflight again"],
                     f="bin/preflight.sh", d="The operator fixes what failed and re-runs the checks."),
            "arm": N(0, 2, "arm the launch", ["bin/day.sh N --wait: hctf run as a", "systemd unit with a memory cap"],
                     f="bin/day.sh", d="Armed before the drop; after this nothing is re-checked."),
            "poll": N(0, 3, "is today listed?", ["ask the GM every 0.3 s;", "no → ask again"], "dec", "plat",
                      "hctf/orchestrate.py", "wait_for_release; release lag ended up 1-3 s."),
            "spawn": N(0, 4, "one chain per challenge", ["threads; LLM workers share five", "slots (--local 5)"],
                       f="hctf/orchestrate.py", d="A process governor caps background solvers so a fan-out can't starve the machine."),
            "run": N(0, 5, "chains run in parallel", ["single → Time Trial → Mastery,", "each as soon as it can"],
                     cls="ours", f="hctf/orchestrate.py", d="Each chain is the single-solve, timed and failure flowcharts below."),
            "watch": N(0, 6, "operator reads the feed", ["one line per milestone + a", "heartbeat (hctf feed)"],
                       f="hctf/feed.py", d="Solved k/N, blocked, generalize, duel, hint, !!! alerts."),
            "all": N(0, 7, "every mode GM-CORRECT?", ["checked against the GM, not", "local state (reconcile)"], "dec",
                     "plat", "hctf/driftwatch.py", "The post-run is held until the GM confirms the whole board."),
            "stuck": N(1, 7, "a chain in trouble?", ["blocked, HELP.md, !!! alert,", "no progress"], "dec", "",
                       "hctf/cli.py", "hctf why says WORKING, BLOCKED or DONE for each chain."),
            "step": N(1, 8, "operator steps in", ["arena reset, relaunch, a fix,", "or answer a HELP"], cls="ours",
                      f="hctf/cli.py", d="Only on a hard stop."),
            "post": N(0, 8, "post-run", ["ratchet, speed-harden, train,", "prebuild, coverage"], f="hctf/postrun.py",
                      d="Resumable phases, each behind a test gate (post-run flowchart below)."),
            "pm": N(0, 9, "post-mortem", ["hctf timeline + KPI row +", "the slowest chains' logs"], cls="ours",
                    f="hctf/timeline.py,hctf/kpi.py", d="The operator writes a numbered fix plan; I approve, reject or reorder."),
            "fx": N(0, 10, "fixes, each with a test", ["parallel agents on disjoint", "files; new fault scenarios"],
                    cls="ours", f="tests/test_fault_replay.py", d="Every new failure mode becomes a scenario the next preflight runs."),
            "reh": N(0, 11, "rehearsal → next warm-up", ["replay a solved day on the", "fake GM, compare per mode"],
                     "end", "", "hctf/replay_gm.py", "Critical-path changes are replayed before the next drop."),
        },
        [("warm", "pf", "", None), ("pf", "fix", "no", None), ("pf", "arm", "yes", None), ("arm", "poll", "", None),
         ("poll", "spawn", "yes", None), ("spawn", "run", "", None), ("run", "watch", "", None),
         ("watch", "all", "", None), ("all", "stuck", "no", None), ("stuck", "step", "yes", None),
         ("stuck", "watch", "no", "right", 18), ("step", "run", "", "right", 40), ("all", "post", "yes", None),
         ("post", "pm", "", None), ("pm", "fx", "", None), ("fx", "reh", "", None)],
        "One loop per day. Red: where reasoning happens (the operator session, its agents, the workers). Green: the "
        "platform.")

    # 2 ---------------------------------------------------------------- single solve
    out["fl-single"] = F(
        "fl-single", "A single solve, from release to handoff",
        "Download, warm worker and reuse race start together; a full race win skips the worker; otherwise triage, GO, "
        "solve and submit, with a watcher that stops the worker at CORRECT.", 3,
        {
            "rel": N(0, 0, "challenge listed", ["the chain enters single:fetch"], "end", "plat", "hctf/orchestrate.py"),
            "fetch": N(0, 1, "start + download", ["GM attempt, contract, artifacts;", "tools named in the text install"],
                       f="hctf/timed.py,hctf/toolchain.py"),
            "warm": N(1, 1, "warm worker", ["claude -p reads the static", "prompt and replies READY"], cls="ours",
                      f="hctf/workers.py", d="Launched before the bytes land."),
            "race": N(2, 1, "reuse race", ["yesterday's solvers on today's", "bytes (flowchart below)"], cls="ours",
                      f="hctf/solvers.py"),
            "tri": N(0, 2, "triage, no LLM", ["toolchain, contract shape,", "similar past solves"],
                     f="hctf/triage.py", d="Writes triage.md (flowchart below)."),
            "won": N(2, 2, "race answered every field?", ["and its seed solver reproduces", "them all"], "dec", "",
                     "hctf/orchestrate.py", "A full win hands off without ever sending the worker its task."),
            "go": N(0, 3, "GO", ["triage + contracts: the second", "message to the warm worker"], cls="ours",
                    f="hctf/orchestrate.py", d="Sent at the download mark."),
            "snap": N(2, 3, "snapshot, stop the worker", ["verified copy pushed to Homebase"], cls="ours",
                      f="hctf/orchestrate.py", d="60% of worker time used to be spent after CORRECT."),
            "solve": N(0, 4, "worker solves", ["CLI tools; writes solver/solve.py"], cls="ours",
                       f="hctf/prompts/single.md", d="Inside the sandbox, steered by hooks (worker flowchart below)."),
            "af": N(1, 4, "answer-first worker", ["medium effort, only the fields", "still open; ≤3 shards"], cls="ours",
                    f="hctf/prompts/answer_first.md", d="Posts every value it confirms to the main worker's inbox."),
            "tt": N(2, 4, "Time Trial", ["timed flowchart below"], "end", "", "hctf/timed.py"),
            "sub": N(0, 5, "hctf submit --from-solver", ["runs solve.py, submits, bisects", "a bulk 'wrong'"],
                     f="hctf/cli.py", d="In the same shell call that writes the solver."),
            "ok": N(0, 6, "GM CORRECT?", ["+ solver passes its cases", "(watcher, every 0.25 s)"], "dec", "plat",
                    "hctf/orchestrate.py"),
            "help": N(0, 7, "relaunch, or HELP.md", ["≤3 launches; the stop hook", "refuses ≤10 times"],
                      f=".claude/hooks/stop_gate.py", d="Stopping without CORRECT needs HELP.md; the chain becomes single:help."),
        },
        [("rel", "fetch", "", None), ("fetch", "warm", "∥", None), ("warm", "race", "∥", None),
         ("fetch", "tri", "", None), ("race", "won", "", None), ("won", "tri", "no", None), ("won", "snap", "yes", None),
         ("tri", "go", "", None), ("go", "solve", "", None), ("go", "af", "∥", "hv"), ("snap", "tt", "", None),
         ("solve", "sub", "", None), ("sub", "ok", "", None), ("ok", "snap", "yes", "right", 18),
         ("ok", "help", "no", None), ("help", "solve", "retry", "left")],
        "Red: model work. Green: the GM. The answer-first worker races the main worker; whichever gets CORRECT first wins.")

    # 3 ---------------------------------------------------------------- triage
    out["fl-triage"] = F(
        "fl-triage", "Triage: from bytes to triage.md, with no LLM",
        "Tool prefetch, contract-shape check, header and artifact description, then reconnaissance and the toolchain "
        "check in parallel, written within seconds with placeholders if needed.", 3,
        {
            "pre": N(0, 0, "prefetch tools", ["from the challenge's name", "and description"], f="hctf/toolchain.py"),
            "shape": N(0, 1, "contract-shape guard", ["a template contract is", "flagged loudly"], f="hctf/contract.py",
                       d="answer_ids are the authority."),
            "head": N(0, 2, "header + formats", ["STATUS n/N; >60 fields →", "a family table"], f="hctf/triage.py"),
            "desc": N(0, 3, "describe each artifact", ["type, size, members"], f="hctf/triage.py"),
            "recon": N(0, 4, "reconnaissance", ["extract and decode (in background", "when a prior solver covers most)"],
                       f="hctf/triage.py"),
            "tool": N(1, 4, "toolchain check", ["detect from the bytes; install a", "missing tool in background"],
                      f="hctf/toolchain.py", d="Per tool: present, installing (≤900 s), or a logged gap."),
            "rdy": N(0, 5, "ready within 1 s / 5 s?", ["toolchain / reconnaissance"], "dec", "", "hctf/triage.py"),
            "ph": N(1, 5, "write with placeholders", ["rewritten when done (dropped", "if already solved)"],
                    f="hctf/triage.py"),
            "write": N(0, 6, "triage.md written", ["+ top 3 similar past solves", "(TF-IDF ≥ 0.12)"], "end", "",
                       "hctf/triage.py,hctf/retrieval.py"),
        },
        [("pre", "shape", "", None), ("shape", "head", "", None), ("head", "desc", "", None),
         ("desc", "recon", "", None), ("desc", "tool", "∥", "hv"), ("recon", "rdy", "", None), ("tool", "rdy", "", None),
         ("rdy", "write", "yes", None), ("rdy", "ph", "no", None), ("ph", "write", "", "vh")],
        "The worker can start before triage finishes; `hctf tool-wait` blocks on a tool still installing (≤600 s).")

    # 4 ---------------------------------------------------------------- a worker's life
    out["fl-worker"] = F(
        "fl-worker", "A worker's life",
        "Slot, usage-limit gate, sandboxed launch, READY and GO, the hook-wrapped tool loop, the stop gate, and how "
        "each kind of exit is handled.", 3,
        {
            "slot": N(0, 0, "take a worker slot", ["5 local slots; urgent and warm", "workers skip the queue"],
                      f="hctf/orchestrate.py"),
            "gate": N(0, 1, "usage limit hit?", ["one gate for the whole account"], "dec", "", "hctf/workers.py"),
            "wait": N(1, 1, "wait for the reset", ["≤6 h + 60 s; the stage deadline", "is extended by the wait"],
                      f="hctf/workers.py", d="One !!! alert, then a quiet wait."),
            "launch": N(0, 2, "launch in bwrap", ["claude -p, Opus 5.5 high,", "turn cap by role"], cls="ours",
                        f="hctf/workers.py", d="Other projects, transcripts, secrets and the Windows drive are masked."),
            "ready": N(0, 3, "message 1 → READY → GO", ["static prompt first; GO with", "triage at the download mark"],
                       cls="ours", f="hctf/workers.py"),
            "pre": N(0, 4, "blocking command?", ["PreToolUse hook: pager, REPL,", "tail -f, listener"], "dec", "",
                     ".claude/hooks/no_block.py"),
            "ref": N(1, 4, "refused with a reason", ["the model rewrites it with", "a timeout"],
                     f=".claude/hooks/no_block.py"),
            "tool": N(0, 5, "run the tool call", ["Bash (25 s default timeout),", "Read, Write, Edit, Skill, Task"],
                      cls="ours", f="hctf/workers.py"),
            "inbox": N(0, 6, "inbox → HARNESS UPDATE", ["PostToolUse hook; nudges at", "10 and 30 minutes"],
                       f=".claude/hooks/nudge.py,hctf/inbox.py", d="The only way to reach a worker mid-run."),
            "corr": N(1, 6, "stopped at CORRECT", ["the watcher kills the worker", "(the usual ending)"], "end", "plat",
                      "hctf/orchestrate.py"),
            "stop": N(0, 7, "may it stop?", ["Stop hook: CORRECT + cases", "pass, or HELP.md written"], "dec", "",
                      ".claude/hooks/stop_gate.py"),
            "blk": N(1, 7, "blocked (≤10 times)", ["told what is missing;", "keeps working"],
                     f=".claude/hooks/stop_gate.py"),
            "exit": N(0, 8, "how did it exit?", ["ok · max_turns · auth · limit ·", "transient · error"], "dec", "",
                      "hctf/workers.py"),
            "auth": N(1, 8, "auth → !!! alert", ["chain help: claude auth login"], f="hctf/workers.py"),
            "rel": N(0, 9, "transient → relaunch", ["≤3×: 20 / 60 / 180 s, fresh", "session, back to the gate"], "end",
                     "", "hctf/workers.py", d="Needs ≥90 s of stage time left."),
        },
        [("slot", "gate", "", None), ("gate", "wait", "yes", None), ("gate", "launch", "no", None),
         ("wait", "launch", "", "vh"), ("launch", "ready", "", None), ("ready", "pre", "", None),
         ("pre", "ref", "yes", None), ("pre", "tool", "no", None), ("ref", "tool", "", "vh"),
         ("tool", "inbox", "", None), ("inbox", "corr", "done", None), ("inbox", "stop", "", None),
         ("inbox", "pre", "next", "left"), ("stop", "blk", "no", None), ("blk", "tool", "", "right", 18),
         ("stop", "exit", "yes", None), ("exit", "auth", "auth", None), ("exit", "rel", "transient", None)],
        "Three Claude Code hooks wrap every tool call and the stop. Red: model work. Green: the GM's verdict ends it.")

    # 5 ---------------------------------------------------------------- prompt assembly
    out["fl-prompt"] = F(
        "fl-prompt", "How a prompt is assembled and delivered",
        "A template per role, filled with lane-specific slots, rendered into a static first message and a second GO "
        "message; during the run the inbox hook is the only channel.", 3,
        {
            "tpl": N(0, 0, "template for the role", ["single, generalize, live, answer-", "first, codify, ratchet…"],
                     f="hctf/prompts/single.md", d="15 Markdown templates with {slot} placeholders."),
            "s1": N(0, 1, "persona + lane skill", ["the skill inlined so no turn", "is spent loading it"],
                    f="hctf/workers.py,skills/huntress-ctf/SKILL.md"),
            "s2": N(0, 2, "helper index + label grammar", ["helpers from lib/ via Python's", "ast; lib/playbook.py"],
                    f="hctf/workers.py,lib/playbook.py"),
            "s3": N(0, 3, "technique log + rules", ["capped excerpts; rules with", "their incidents; a budget"],
                    f="hctf/orchestrate.py", d="The 60 s / 3 min budget and the subagent policy."),
            "rend": N(0, 4, "render", ["str.replace of {slot};", "over 100 KB → stdin"], f="hctf/workers.py"),
            "m1": N(0, 5, "message 1", ["the static prompt +", "'reply with exactly READY'"], cls="ours",
                    f="hctf/workers.py", d="Sent at launch, before the bytes have landed."),
            "tri": N(1, 6, "triage + contracts", ["triage ≤6,000 chars; prior", "solver; timed contracts"],
                     f="hctf/orchestrate.py"),
            "m2": N(0, 6, "message 2: GO", ["sent after READY, at the", "download mark"], cls="ours",
                    f="hctf/orchestrate.py"),
            "co": N(1, 7, "coordinator (stalled only)", ["Sonnet 5.5, one turn, no tools:", "NONE or one hint"],
                    f="hctf/coordinator.py", d="9 reviews and 3 hints all month."),
            "inb": N(0, 7, "inbox during the run", ["race results, rejected values,", "hints: after every tool call"],
                     "end", "", "hctf/inbox.py,.claude/hooks/nudge.py"),
        },
        [("tpl", "s1", "", None), ("s1", "s2", "", None), ("s2", "s3", "", None), ("s3", "rend", "", None),
         ("rend", "m1", "", None), ("m1", "m2", "READY", None), ("tri", "m2", "", None), ("m2", "inb", "", None),
         ("co", "inb", "", None)],
        "Static parts first and per-challenge parts last is also what makes prompt caching work.")

    # 6 ---------------------------------------------------------------- reuse race
    out["fl-race"] = F(
        "fl-race", "The reuse race",
        "Pick prior solvers, run them on today's bytes (inside the CTF network for big binaries), merge and gate their "
        "answers, bank them in stages, and hand off without a worker on a full win.", 3,
        {
            "cand": N(0, 0, "pick candidates", ["lane solver + newest 3 (or", "newest + 2 most similar)"],
                      f="hctf/solvers.py", d="Web races only its lane solver (14 s)."),
            "big": N(0, 1, "single ≥ 10 MB?", ["non-web lanes"], "dec", "", "hctf/orchestrate.py"),
            "hb": N(1, 1, "race on Homebase", ["inside the CTF network; ≤30 s", "for a relay channel, 75 s cap"],
                    cls="plat", f="hctf/orchestrate.py", d="Stands down if the local bytes land first."),
            "run": N(0, 2, "run them in parallel", ["≤6 at once, 20 s each"], f="hctf/solvers.py"),
            "merge": N(0, 3, "merge the answers", ["newest wins a field; 'high' if", "GM-verified in its own cases"],
                       f="hctf/solvers.py"),
            "gate": N(0, 4, "format / slug gate", ["implausible values never reach", "the GM"],
                      f="hctf/orchestrate.py"),
            "bank": N(0, 5, "bank the answers", ["complete → confident → speculative;", "≤200 probes in total"],
                      f="hctf/orchestrate.py", d="The race is the attempt's only bisector; the worker's submit waits on it."),
            "all": N(0, 6, "every field confirmed?", ["and the seed solver reproduces", "every confirmed answer"],
                     "dec", "plat", "hctf/orchestrate.py"),
            "hand": N(1, 6, "race-first handoff", ["no worker launched; the timed", "modes start (≤12 s)"], "end",
                      "ours", "hctf/orchestrate.py"),
            "lab": N(0, 7, "resolve stray labels", ["in parallel, with the other", "solvers' values as alternates"],
                     f="hctf/labels.py"),
            "inb": N(0, 8, "tell the worker", ["HARNESS UPDATE: n/N fields", "confirmed"], f="hctf/inbox.py"),
            "af": N(0, 9, "residual → answer-first", ["a medium worker takes the", "fields still open"], "end", "ours",
                    "hctf/prompts/answer_first.md"),
        },
        [("cand", "big", "", None), ("big", "hb", "yes", None), ("big", "run", "no", None), ("hb", "merge", "", "vh"),
         ("run", "merge", "", None), ("merge", "gate", "", None), ("gate", "bank", "", None), ("bank", "all", "", None),
         ("all", "hand", "yes", None), ("all", "lab", "no", None), ("lab", "inb", "", None), ("inb", "af", "", None)],
        "Every single solve from day 12 started with this. Red: what saves model time. Green: the platform.")

    # 7 ---------------------------------------------------------------- timed attempt
    out["fl-timed"] = F(
        "fl-timed", "One timed attempt",
        "Reuse a pre-started attempt or start one, download, solve with a forked warm solver under a budget, submit "
        "once, then localize wrong fields or bank partial answers.", 3,
        {
            "pre": N(0, 0, "attempt already started?", ["at the previous mode's CORRECT"], "dec", "",
                     "hctf/orchestrate.py"),
            "start": N(1, 0, "start, hedged", ["status/start on both paths; first", "judged reply wins"],
                       f="hctf/gmroute.py", d="A submit is never sent twice."),
            "dl": N(0, 1, "download", ["in parallel; per set when ≥20 MB;", "big replies avoid the SSH channel"],
                    f="hctf/hb_timed.py"),
            "bud": N(0, 2, "set the solve budget", ["time left − 1.5 s (untimed:", "60-300 s by size)"],
                     f="hctf/hb_timed.py"),
            "fork": N(0, 3, "fork the warm solver", ["zygote: 15-51 ms vs 150-230 ms", "cold; one fork per set"],
                      cls="ours", f="hctf/hb_zygote.py,hctf/hb_daemon.py"),
            "sub": N(0, 4, "submit once", ["all answers in one call"], cls="plat", f="hctf/hb_timed.py"),
            "ok": N(0, 5, "correct?", [], "dec", "plat", "hctf/timed.py"),
            "rec": N(1, 5, "record a regression case", ["auto-<mode>-<attempt>, with the", "GM-verified answers"],
                     "end", "", "hctf/timed.py"),
            "kind": N(0, 6, "what went wrong?", [], "dec", "", "hctf/hb_timed.py"),
            "loc": N(1, 6, "localize", ["bisect per set; fix labels from", "the cache, no model"],
                     f="hctf/hb_timed.py"),
            "part": N(0, 7, "partial submit", ["bank what the solver produced"], f="hctf/hb_timed.py"),
            "fail": N(0, 8, "failure path", ["next flowchart"], "end", "ours", "hctf/orchestrate.py"),
        },
        [("pre", "start", "no", None), ("pre", "dl", "yes", None), ("start", "dl", "", "vh"), ("dl", "bud", "", None),
         ("bud", "fork", "", None), ("fork", "sub", "", None), ("sub", "ok", "", None), ("ok", "rec", "yes", None),
         ("ok", "kind", "no", None), ("kind", "loc", "wrong", None), ("kind", "part", "incomplete", None),
         ("part", "fail", "", None), ("loc", "fail", "still wrong", "vh")],
        "No model in the loop. It runs on Homebase first and falls back to the same code locally.")

    # 8 ---------------------------------------------------------------- failure / generalize
    out["fl-fail"] = F(
        "fl-fail", "When a timed variant fails",
        "The variant becomes a regression case, then repairs race: a library racer, a live answer and a transactional "
        "generalize; up to five retries, then an untimed fallback, then a human.", 3,
        {
            "cap": N(0, 0, "capture the variant", ["a regression case with the GM's", "per-field verdicts"],
                     f="hctf/orchestrate.py", d="Expected answers only ever come from the GM."),
            "probe": N(0, 1, "probe the fields", ["which are wrong, which missing"], f="hctf/timed.py"),
            "snap": N(0, 2, "snapshot (the 'before')", ["solver, the cases that pass,", "every expected.json"],
                      f="hctf/orchestrate.py"),
            "live": N(1, 2, "live answer", ["a worker answers the open attempt", "by hand (≤80 fields)"], cls="ours",
                      f="hctf/prompts/live.md", d="Untimed attempts only; medium effort at ≤5 fields; 900 s."),
            "lib": N(2, 2, "library racer", ["warmups: lane decoder, no", "model, ≤60 probes"],
                     f="hctf/libracer.py"),
            "gen": N(0, 3, "generalize (+ duel)", ["fix the construct family, not", "this sample"], cls="ours",
                     f="hctf/prompts/generalize.md,hctf/duel.py", d="Opus at medium plus a Sonnet racer; first verified fix wins."),
            "win": N(1, 3, "first repair to pass wins", ["the others are stopped"], "end", "plat",
                     "hctf/orchestrate.py"),
            "rest": N(0, 4, "restore every expected.json", ["workers never author", "expected answers"],
                      f="hctf/orchestrate.py"),
            "test": N(0, 5, "anything broken?", ["run every case that passed", "before"], "dec", "",
                      "hctf/orchestrate.py"),
            "rej": N(1, 6, "restore the snapshot", ["the edit goes to", ".generalize-rejected/"],
                     f="hctf/orchestrate.py"),
            "acc": N(0, 6, "keep the edit", [], cls="ours", f="hctf/orchestrate.py"),
            "ret": N(0, 7, "retries left (≤5)?", ["rate limits and refused starts", "don't count"], "dec", "",
                     "hctf/orchestrate.py"),
            "again": N(0, 8, "next timed attempt", ["usually passes: the solver", "now knows this variant"], "end", "",
                       "hctf/timed.py"),
            "unt": N(1, 7, "untimed fallback", ["3 rounds on a fresh untimed", "attempt"], f="hctf/orchestrate.py"),
            "blk": N(1, 8, "blocked → a human", ["!!! in the feed"], "end", "ours", "hctf/feed.py"),
        },
        [("cap", "probe", "", None), ("probe", "snap", "", None), ("probe", "live", "∥", None),
         ("probe", "lib", "", None), ("snap", "gen", "", None), ("live", "win", "", None), ("lib", "win", "", None),
         ("gen", "rest", "", None), ("rest", "test", "", None), ("test", "rej", "yes", "hv"), ("test", "acc", "no", None),
         ("acc", "ret", "", None), ("rej", "ret", "", None), ("ret", "again", "yes", None), ("ret", "unt", "no", None),
         ("unt", "blk", "still failing", None)],
        "The three repairs run at once; whichever passes the attempt first wins. Red: model work.")

    # 9 ---------------------------------------------------------------- label resolution
    out["fl-labels"] = F(
        "fl-labels", "Learning the GM's spelling",
        "For a rejected exact-text field: use the enum if there is one; otherwise rank candidates, filter known-bad "
        "spellings, check locally, probe within a budget, and cache what the GM accepts.", 3,
        {
            "enum": N(0, 0, "is the field an enum?", ["answer_format.kind"], "dec", "plat", "hctf/labels.py"),
            "pick": N(1, 0, "pick from accepted_values", ["never probe a listed field"], "end", "", "hctf/labels.py"),
            "rank": N(0, 1, "rank candidates", ["solver value → playbook seeds →", "alternates → sibling labels"],
                      f="hctf/labels.py", d="Then terms composed from the artifact."),
            "filt": N(0, 2, "filter", ["drop playbook-rejected and", "already-wrong spellings"], f="lib/playbook.py"),
            "guard": N(0, 3, "local guards", ["format, enum, slug, a real ATT&CK", "id, wrong-answer caps"],
                       f="hctf/cli.py,lib/refs/attack.py"),
            "probe": N(0, 4, "probe one at a time", ["budget 25 per field; rate-", "limited for the whole account"],
                       cls="plat", f="hctf/ratebucket.py"),
            "ok": N(0, 5, "accepted?", [], "dec", "plat", "hctf/labels.py"),
            "cache": N(1, 5, "cache in vocab.json", ["read inside the timed window", "next time"], "end", "ours",
                       "lib/vocab.json"),
            "more": N(0, 6, "budget left?", [], "dec", "", "hctf/labels.py"),
            "comp": N(0, 7, "depth-3 search, then HELP", ["three-token labels before", "inventing new words"],
                      "end", "", "hctf/labels.py"),
        },
        [("enum", "pick", "yes", None), ("enum", "rank", "no", None), ("rank", "filt", "", None),
         ("filt", "guard", "", None), ("guard", "probe", "", None), ("probe", "ok", "", None),
         ("ok", "cache", "yes", None), ("ok", "more", "no", None), ("more", "rank", "retry", "left"),
         ("more", "comp", "no", None)],
        "The actual labels stay out of this post; the grammar that generates them is described in the text.")

    # 10 --------------------------------------------------------------- web lane
    out["fl-web"] = F(
        "fl-web", "The web lane",
        "Take a target slot, wait for the target (reviving or kicking it), dispatch on its clue keys to racing exploit "
        "handlers, submit the proof, then codify the winner as a plugin.", 3,
        {
            "slot": N(0, 0, "take a target slot", ["5 per team (a file lock), held", "for the whole chain"],
                      f="hctf/webtarget.py", d="The next mode's target is pre-provisioned."),
            "up": N(0, 1, "target up?", ["poll every 2 s, wait ≤480 s"], "dec", "plat", "hctf/webtarget.py"),
            "kick": N(1, 1, "revive or kick it", ["arena start every 30 s (≤6);", "kick every 15 s (≤4)"],
                      cls="plat", f="hctf/webtarget.py", d="Arena reset is the organizers' sanctioned recovery."),
            "clue": N(0, 2, "read the clue keys", ["GET /api/clues → which", "handlers apply"],
                      f="lib/web/__init__.py"),
            "kit": N(0, 3, "one-shot credit kit?", ["a side-effect-free audit", "request first"], "dec", "",
                     "lib/web/__init__.py", "A one-shot target must not be spent by a helper request."),
            "alone": N(1, 3, "RUN_ALONE handlers only", ["nothing else touches the", "target; ≥25 s budget"],
                       f="lib/web/handlers/__init__.py"),
            "race": N(0, 4, "race the candidates", ["LFI probe, key handlers, ladder,", "earlier days (kit: RUN_ALONE only)"],
                      cls="ours", f="lib/websolve.py", d="Known class 20 s, unknown 12 s; the first proof wins."),
            "proof": N(0, 5, "proof found?", ["≤4 retries, 2.5 s apart"], "dec", "plat", "lib/web/__init__.py"),
            "heal": N(1, 5, "self-heal, or a worker", ["credit kit: arena reset (≤2);", "else the LLM worker"],
                      cls="ours", f="hctf/orchestrate.py"),
            "codify": N(0, 6, "codify the winner", ["a worker turns it into a plugin;", "verified live (≤300 s)"],
                        cls="ours", f="hctf/prompts/codify.md,lib/web/plugin.py"),
            "prom": N(0, 7, "promote atomically", ["os.replace; the old copy", "is backed up"], "end", "ours",
                      "lib/web/plugin.py", "The next target of this class is solved in seconds."),
        },
        [("slot", "up", "", None), ("up", "kick", "no", None), ("up", "clue", "yes", None), ("kick", "clue", "", "vh"),
         ("clue", "kit", "", None), ("kit", "alone", "yes", None), ("kit", "race", "no", None),
         ("alone", "race", "", "vh"), ("race", "proof", "", None), ("proof", "heal", "no", None),
         ("proof", "codify", "yes", None), ("codify", "prom", "", None)],
        "Time Trial and Mastery each get a fresh target; arena stop frees the slot when a mode is done.")

    # 11 --------------------------------------------------------------- post-run
    out["fl-post"] = F(
        "fl-post", "Overnight: the post-run",
        "Held until the GM confirms the whole board, then resumable phases, each with its own keep-or-rollback gate.", 3,
        {
            "gate": N(0, 0, "board GM-solved?", ["holdouts are listed in the", "feed"], "dec", "plat",
                      "hctf/driftwatch.py", "Solve everything before learning anything."),
            "hold": N(1, 0, "held", ["finish the stragglers, then", "hctf postrun --day N"], f="hctf/postrun.py"),
            "rat": N(0, 1, "ratchet", ["workers' proposals → lib/; a", "technique log per lane"], cls="ours",
                     f="hctf/prompts/ratchet.md,hctf/prompts/ratchet_log.md", d="The only writer to the shared library."),
            "rg": N(0, 2, "suites still pass?", ["baseline-aware; edited", "assertions restored first"], "dec", "",
                    "hctf/orchestrate.py"),
            "rv": N(2, 2, "revert lib/ + tests/", [], f="hctf/orchestrate.py"),
            "sh": N(0, 3, "speed-harden", ["slowest case >2.5 s → a speed", "generalize"], cls="ours",
                    f="hctf/orchestrate.py", d="Failing verified cases get a correctness fix first."),
            "fast": N(0, 4, "≥5% faster?", ["or a new case passes"], "dec", "", "hctf/orchestrate.py"),
            "keep": N(1, 4, "keep the faster solver", [], f="hctf/orchestrate.py"),
            "back": N(0, 5, "restore the snapshot", [], f="hctf/orchestrate.py"),
            "train": N(0, 6, "train", ["replay every earlier day; adopt", "misses (≤2 rounds)"], f="hctf/train.py",
                       d="Nothing learned on day 20 may break day 8."),
            "pre": N(0, 7, "prebuild until the warm-up", ["speculative modules behind", "fixtures; $60 per lane"],
                     cls="ours", f="hctf/prebuild.py", d="Stops 30 minutes before the next drop (gate flowchart below)."),
            "cov": N(0, 8, "coverage + KPI row", ["toolchain report;", "hctf kpi --record"], "end", "",
                     "hctf/kpi.py"),
        },
        [("gate", "hold", "no", None), ("gate", "rat", "yes", None), ("rat", "rg", "", None), ("rg", "rv", "no", None),
         ("rg", "sh", "yes", None), ("sh", "fast", "", None), ("fast", "keep", "yes", None),
         ("fast", "back", "no", None), ("back", "train", "", None), ("keep", "train", "", "vh"),
         ("rv", "train", "", "vh"), ("train", "pre", "", None), ("pre", "cov", "", None)],
        "Each phase is recorded in .run/dayNN.postrun.json and can be resumed after a crash.")

    # 12 --------------------------------------------------------------- prebuild gate
    out["fl-prebuild"] = F(
        "fl-prebuild", "The prebuild gate",
        "Off-peak workers build speculative decoders on a private copy of the library; a module merges only through a "
        "layered gate, one at a time.", 3,
        {
            "q": N(0, 0, "pick a target", ["coverage gaps → ranked", "TARGETS.json → the rest"], f="hctf/prebuild.py",
                   d="Skips done targets and ones that failed twice."),
            "w": N(0, 1, "a worker builds one module", ["private lib/ copy; no GM token,", "no secrets"], cls="ours",
                   f="hctf/prompts/prebuild.md"),
            "p": N(0, 2, "allowed paths and calls?", ["AST import/call allowlist; no", "subprocess, eval, file I/O"],
                   "dec", "", "hctf/prebuild.py"),
            "fx": N(0, 3, "fixtures pass?", ["≥2 per format incl. a decoy;", "≤1 s; independent oracle"], "dec", "",
                    "hctf/prebuild.py"),
            "su": N(0, 4, "suites + replay green?", ["lane tests; verified cases", "still pass"], "dec", "",
                    "hctf/prebuild.py", "Merged one at a time under a lock."),
            "mg": N(0, 5, "merge into lib/", ["a race entry only, never the", "critical path"], "end", "ours",
                    "hctf/prebuild.py"),
            "rs": N(1, 4, "throw it away", ["tree changed outside the", "gate → !!! and stop"], f="hctf/prebuild.py"),
        },
        [("q", "w", "", None), ("w", "p", "", None), ("p", "fx", "yes", None), ("fx", "su", "yes", None),
         ("su", "mg", "yes", None), ("su", "rs", "no", None), ("p", "rs", "no", "hv"), ("fx", "rs", "no", "hv"),
         ("rs", "q", "next target", "right", 18)],
        "Most of lib/'s 195k lines came through this gate: 189 metadata modules covering 25,099 format-field keys.")
    return out
