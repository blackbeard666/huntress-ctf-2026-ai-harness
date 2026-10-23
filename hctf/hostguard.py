"""Host exclusivity guard: ONE harness copy busy on this box at a time.

2026-10-22: an rehearsal validation run (~/huntress-2026-rehearsal) shared the 12 cores with main's `hctf prebuild --parallel`
(parallel LLM workers + solver regression gates): load 37-50, fake "solver too slow" speed generalizes, every timing
of that run invalid. bin/day.sh step 0 pgrep'd prebuild host-wide but stopped it only through its OWN copy's
`prebuild --stop` (prebuild._batch_pids keeps processes whose cwd is that copy), which cannot reach another copy.

  harness_procs()       live `hctf run` / `hctf prebuild` processes that do work (not --stop/--list/--recover/--help,
                        not feed/why/dash/...), each with the harness copy ("root") it belongs to
  other_copies(root)    the subset owned by a DIFFERENT copy than `root` (main, a worktree, a replay copy)
  host_load()           (5-min loadavg, nproc)

CLI (stdlib only, no package imports: runs from a copy whose other modules are older):
  python3 -m hctf.hostguard check [--root R]                 one `OTHER <kind> pid=.. root=.. cmd=..` line per
                                                             other-copy proc; exit 1 if any, 0 if none
  python3 -m hctf.hostguard stop-other-prebuilds [--root R]  `prebuild --stop` INSIDE each other copy that has a
                                                             prebuild live (prebuild is always preemptible; a RUN is
                                                             never touched); exit 1 if one is still alive after
  python3 -m hctf.hostguard load                             load5=<x> nproc=<n> per_cpu=<x/n>
Exit 3 = the guard itself failed: callers treat it as "unknown", never as busy.

Root of a process: its cwd walked up to the nearest dir holding both hctf/ and bin/env.sh; else its PYTHONPATH /
HCTF_ROOT (bin/hctf, bin/env.sh); else a `cd <dir>` in its own (shell) or a parent shell's script; else None (never
counted as another copy). Our own pid and its ancestors are never reported.
Used by bin/preflight.sh (FAIL; HCTF_SHARED_HOST=1 -> WARN), bin/day.sh step 0 (stops other copies' prebuilds, warns
on their runs, never aborts), bin/fair_run.sh (refuses to start).
"""
from __future__ import annotations

import argparse
import os
import re
import shlex
import signal
import subprocess
import sys
import time
from pathlib import Path

KINDS = {"run": "run", "prebuild": "prebuild"}            # hctf subcommand -> kind (the ones that load the host)
IDLE_FLAGS = {"--stop", "--list", "--recover", "-h", "--help"}   # control / read-only invocations of those
SHELLS = {"sh", "bash", "dash", "zsh"}
# tokens allowed BEFORE the hctf invocation in an argv / shell segment (`timeout 60 python3 -m hctf.cli run`,
# `env X=Y hctf run`, `{ hctf run ..`, `/bin/sh .../bin/hctf run`); anything else (grep, pgrep, echo, eval) = no match
WRAPPERS = {"timeout", "nice", "ionice", "nohup", "setsid", "env", "stdbuf", "taskset", "chrt", "exec", "time",
            "command", "{", "(", "!", "then", "do", "else"}
CTRL = {";", "&&", "||", "|", "&", ";;", "|&", "(", ")"}
ENV_KEYS = ("PYTHONPATH", "HCTF_ROOT")
_PYTHON = re.compile(r"python[\d.]*")
_NUM = re.compile(r"\d+(?:\.\d+)?[smhd]?")
_ASSIGN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*=.*")
OWN_ROOT = Path(__file__).resolve().parent.parent


# ------------------------------------------------------------------------------------------------ classification
def _prefixish(tok):
    name = Path(tok).name
    return (tok in WRAPPERS or name in WRAPPERS or name in SHELLS or tok.startswith("-")
            or bool(_NUM.fullmatch(tok)) or bool(_ASSIGN.fullmatch(tok)))


def _hctf_sub(tokens):
    """(subcommand, rest) when `tokens` invoke the hctf CLI -- `<python> [-opts] -m hctf.cli SUB ..` or the bin/hctf
    wrapper `[sh] .../hctf SUB ..` -- behind wrapper-ish prefixes only; else (None, [])."""
    for i, t in enumerate(tokens):
        name = Path(t).name
        if _PYTHON.fullmatch(name):
            j = i + 1
            while j < len(tokens) and tokens[j] != "-m" and tokens[j].startswith("-"):
                j += 2 if tokens[j] in ("-X", "-W") else 1      # interpreter options (-u, -I, -X dev, -W ignore)
            if tokens[j:j + 2] == ["-m", "hctf.cli"] and len(tokens) > j + 2:
                return tokens[j + 2], tokens[j + 3:]
            return None, []
        if name == "hctf":
            return (tokens[i + 1], tokens[i + 2:]) if len(tokens) > i + 1 else (None, [])
        if not _prefixish(t):
            return None, []
    return None, []


def _shell_script(argv):
    """The command string of `bash|sh [-opts with c] <script> ..` (-c, -lc, `-c -l`), else None."""
    if not argv or Path(argv[0]).name not in SHELLS:
        return None
    has_c = False
    for tok in argv[1:]:
        if tok.startswith("--"):
            continue
        if tok.startswith("-"):
            has_c = has_c or "c" in tok[1:]
            continue
        return tok if has_c else None
    return None


def _segments(script):
    """Simple commands of a shell script as token lists (quotes honoured; split on ; && || | & and newlines)."""
    out = []
    for line in script.splitlines():
        lex = shlex.shlex(line, posix=True, punctuation_chars=True)
        lex.whitespace_split = True
        lex.commenters = ""
        try:
            toks = list(lex)
        except ValueError:          # unbalanced quotes: fall back to whitespace
            toks = line.split()
        cur = []
        for t in toks:
            if t in CTRL:
                if cur:
                    out.append(cur)
                cur = []
            else:
                cur.append(t)
        if cur:
            out.append(cur)
    return out


def classify(argv):
    """(kind, is_shell) for an hctf day run / prebuild that does work, else None.
    is_shell = a `bash -c` / `bash -lc` script that launches one (the setsid day launch, the post-run prebuild chain):
    reported so a chain shell between two prebuild lanes is still seen (and stopped before it starts the next lane)."""
    argv = list(argv or [])
    sub, rest = _hctf_sub(argv)
    if sub is not None:
        return (KINDS[sub], False) if sub in KINDS and not IDLE_FLAGS.intersection(rest) else None
    script = _shell_script(argv)
    if script:
        for seg in _segments(script):
            sub, rest = _hctf_sub(seg)
            if sub in KINDS and not IDLE_FLAGS.intersection(rest):
                return KINDS[sub], True
    return None


# ------------------------------------------------------------------------------------------------ /proc + roots
def list_procs():
    """Every live process as {pid, ppid, argv, cwd}; unreadable cwd -> None, kernel threads/zombies (no argv) skipped."""
    out = []
    for d in Path("/proc").iterdir():
        if not d.name.isdigit():
            continue
        try:
            argv = [a.decode(errors="replace") for a in (d / "cmdline").read_bytes().split(b"\0") if a]
            stat = (d / "stat").read_text(errors="replace")
        except OSError:
            continue
        if not argv:
            continue
        try:
            ppid = int(stat.rsplit(")", 1)[1].split()[1])
        except (IndexError, ValueError):
            ppid = 0
        try:
            cwd = os.readlink(d / "cwd")
        except OSError:
            cwd = None
        out.append({"pid": int(d.name), "ppid": ppid, "argv": argv, "cwd": cwd})
    return out


def _read_env(pid):
    """PYTHONPATH / HCTF_ROOT from /proc/<pid>/environ ({} when unreadable)."""
    try:
        raw = Path(f"/proc/{pid}/environ").read_bytes()
    except OSError:
        return {}
    out = {}
    for kv in raw.split(b"\0"):
        k, _, v = kv.partition(b"=")
        if k.decode(errors="replace") in ENV_KEYS:
            out[k.decode()] = v.decode(errors="replace")
    return out


def is_root(d):
    try:
        return (Path(d) / "hctf").is_dir() and (Path(d) / "bin" / "env.sh").is_file()
    except OSError:
        return False


def root_of(path):
    """Nearest dir at or above `path` that is a harness copy (hctf/ + bin/env.sh), as a real path; else None."""
    if not path:
        return None
    s = str(path)
    s = s[:-len(" (deleted)")] if s.endswith(" (deleted)") else s
    s = os.path.expanduser(s.replace("${HOME}", "~").replace("$HOME", "~"))
    p = Path(s)
    if not p.is_absolute():
        return None
    for d in (p, *p.parents):
        if is_root(d):
            return os.path.realpath(d)
    return None


def _ancestry(pid, by_pid):
    out, seen = [], {pid}
    cur = by_pid.get(pid, {}).get("ppid")
    while cur and cur not in seen and len(out) < 64:
        out.append(cur)
        seen.add(cur)
        cur = by_pid.get(cur, {}).get("ppid")
    return out


def _cd_root(argv):
    """Harness root named by a `cd <dir>` in a shell's -c script."""
    script = _shell_script(argv)
    if not script:
        return None
    for seg in _segments(script):
        if len(seg) > 1 and seg[0] == "cd":
            r = root_of(seg[1])
            if r:
                return r
    return None


def resolve_root(p, by_pid, env_reader=None):
    r = root_of(p.get("cwd"))
    if r:
        return r
    env = p["env"] if "env" in p else (env_reader(p["pid"]) if env_reader else {})
    for key in ENV_KEYS:
        for entry in (env or {}).get(key, "").split(":"):
            r = root_of(entry)
            if r:
                return r
    for pid in [p["pid"], *_ancestry(p["pid"], by_pid)[:3]]:   # own script (a chain shell), then parent shells
        q = by_pid.get(pid)
        r = _cd_root(q.get("argv") or []) if q else None
        if r:
            return r
    return None


# ------------------------------------------------------------------------------------------------ API
def harness_procs(proc_lister=None, self_pid=None, env_reader=None):
    """[{pid, kind: run|prebuild, root, cmd, shell, ppid, ancestors}] for every live hctf day run / prebuild, minus
    our own pid and its ancestors. `proc_lister()` -> [{pid, ppid, argv, cwd[, env]}] (default: /proc)."""
    procs = list((proc_lister or list_procs)())
    if env_reader is None and proc_lister is None:
        env_reader = _read_env
    by_pid = {p["pid"]: p for p in procs}
    me = os.getpid() if self_pid is None else self_pid
    skip = {me, *_ancestry(me, by_pid)}
    out = []
    for p in procs:
        if p["pid"] in skip:
            continue
        c = classify(p.get("argv"))
        if not c:
            continue
        out.append({"pid": p["pid"], "kind": c[0], "root": resolve_root(p, by_pid, env_reader),
                    "cmd": " ".join(p.get("argv") or []), "shell": c[1], "ppid": p.get("ppid"),
                    "ancestors": _ancestry(p["pid"], by_pid)})
    return out


def own_root(root=None):
    if root:
        return root_of(os.path.abspath(os.path.expanduser(str(root)))) or os.path.realpath(root)
    return root_of(OWN_ROOT) or os.path.realpath(OWN_ROOT)


def other_copies(root=None, procs=None, proc_lister=None, self_pid=None):
    """harness_procs() owned by a harness copy other than `root` (default: this module's copy); unresolved roots
    are never counted."""
    own = own_root(root)
    if procs is None:
        procs = harness_procs(proc_lister, self_pid)
    return [p for p in procs if p.get("root") and p["root"] != own]


def leaves(procs):
    """Drop a proc when another listed proc descends from it (a chain/launch shell whose python child is listed)."""
    return [p for p in procs if not any(p["pid"] in q.get("ancestors", ()) for q in procs)]


def describe(p, width=200):
    cmd = p["cmd"] if len(p["cmd"]) <= width else p["cmd"][:width - 3] + "..."
    return f"OTHER {p['kind']} pid={p['pid']} root={p['root']} cmd={cmd}"


def host_load():
    return os.getloadavg()[1], os.cpu_count() or 1


def stop_other_prebuilds(root=None, proc_lister=None, self_pid=None, runner=None, killer=None, log=print,
                         settle=3.0):
    """`timeout 120 <this python> -m hctf.cli prebuild --stop` with cwd=<that root> (PYTHONPATH=<that root>) for every
    OTHER copy with a prebuild live; its chain shells get SIGTERM first so they cannot start the next lane (prebuild
    --stop only matches `bash -c '<python> -m hctf.cli prebuild ..'` chains, not the systemd `bash -lc 'cd ..; ..'`
    one). Runs are never touched. Returns 0 when no other-copy prebuild is left, else 1."""
    runner = runner or subprocess.run
    killer = killer or os.kill
    others = [p for p in other_copies(root, proc_lister=proc_lister, self_pid=self_pid) if p["kind"] == "prebuild"]
    if not others:
        log("no other harness copy's prebuild is running.")
        return 0
    for r in sorted({p["root"] for p in others}):
        mine = [p for p in others if p["root"] == r]
        log(f"stopping the prebuild of {r} (pids {' '.join(str(p['pid']) for p in mine)})")
        for p in mine:
            if p["shell"]:
                try:
                    killer(p["pid"], signal.SIGTERM)
                    log(f"  SIGTERM chain shell {p['pid']}")
                except (ProcessLookupError, PermissionError) as e:
                    log(f"  chain shell {p['pid']}: {type(e).__name__}")
        env = dict(os.environ, PYTHONPATH=r, HCTF_ROOT=r, PATH=f"{r}/bin:{os.environ.get('PATH', '')}")
        cmd = ["timeout", "120", sys.executable, "-m", "hctf.cli", "prebuild", "--stop"]
        try:
            res = runner(cmd, cwd=r, env=env, capture_output=True, text=True, timeout=150)
            rc, text = res.returncode, (res.stdout or "") + (res.stderr or "")
        except (OSError, subprocess.SubprocessError) as e:
            rc, text = None, f"{type(e).__name__}: {e}"
        for line in text.splitlines():
            log(f"  [{Path(r).name}] {line}")
        log(f"  prebuild --stop in {r}: rc={rc}")
    end = time.time() + settle
    while True:
        left = [p for p in other_copies(root, proc_lister=proc_lister, self_pid=self_pid) if p["kind"] == "prebuild"]
        if not left or time.time() >= end:
            break
        time.sleep(0.5)
    for p in leaves(left):
        log("still alive: " + describe(p))
    return 1 if left else 0


# ------------------------------------------------------------------------------------------------ CLI
def main(argv=None, proc_lister=None, self_pid=None, runner=None, killer=None, out=None, settle=3.0):
    out = out or sys.stdout

    def say(m):
        print(m, file=out, flush=True)

    ap = argparse.ArgumentParser(prog="python3 -m hctf.hostguard",
                                 description="one harness copy busy per host (see the module docstring)")
    sp = ap.add_subparsers(dest="cmd", required=True)
    for name in ("check", "stop-other-prebuilds"):
        sp.add_parser(name).add_argument("--root", help="this copy's root (default: the copy holding this module)")
    sp.add_parser("load")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "check":
            procs = harness_procs(proc_lister, self_pid)
            others = other_copies(a.root, procs)
            for p in leaves(others):
                say(describe(p))
            for p in leaves([p for p in procs if not p.get("root")]):
                print(f"note: {p['kind']} pid={p['pid']} with an unresolved harness root (not counted): "
                      f"{p['cmd'][:160]}", file=sys.stderr)
            if not others:
                say(f"ok: no other harness copy is running a day run or prebuild (own root {own_root(a.root)})")
            return 1 if others else 0
        if a.cmd == "stop-other-prebuilds":
            return stop_other_prebuilds(a.root, proc_lister, self_pid, runner, killer, log=say, settle=settle)
        l5, n = host_load()
        say(f"load5={l5:.2f} nproc={n} per_cpu={l5 / n:.2f}")
        return 0
    except Exception as e:  # noqa: BLE001 - the guard failing is "unknown", never "busy"
        print(f"hostguard error: {type(e).__name__}: {e}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
