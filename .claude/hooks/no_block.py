#!/usr/bin/env python3
"""PreToolUse(Bash) hook for harness workers: refuse commands that can sit forever in an unattended run (a pager, a
follow, a REPL, a listener, an un-timed network call, a long sleep) and say what to run instead. Workers have no human
to press q / Ctrl-C; the 25 s default Bash cap bounds the damage, but an explicit long timeout does not (recorded:
`7z x` waiting on stdin 120 s, SPEED.md:344). reviewer runbook rule, adapted: `timeout N ...` is OUR guard, so a
command wrapped in it is always allowed, as is run_in_background. Fails OPEN: any parse problem allows the command.
No-op outside a worker (HCTF_CHAL unset) or with HCTF_NO_BLOCK=0."""
import json
import os
import re
import shlex
import sys

if not os.environ.get("HCTF_CHAL") or os.environ.get("HCTF_NO_BLOCK", "1") == "0":
    sys.exit(0)

OPS = {"|", "||", "&&", ";", "&", "(", ")", ";;", "|&", "\n"}
PREFIX = {"sudo", "nohup", "time", "env", "exec", "command", "builtin", "nice", "stdbuf"}
PAGERS = {"less", "more", "most", "man", "watch", "top", "htop", "vi", "vim", "nano", "emacs", "telnet"}
REPLS = {"python", "python3", "node", "irb", "ruby", "php", "lua", "perl", "jshell", "ghci", "sqlite3", "bash", "sh"}
HEREDOC = re.compile(r"<<-?\s*(['\"]?)(\w+)\1[^\n]*\n.*?^\s*\2\s*$", re.S | re.M)


def segments(cmd):
    """[(words, piped_in, has_redirect_in)] per simple command; heredoc bodies stripped first (their content is data)."""
    cmd = HEREDOC.sub(lambda m: m.group(0).split("\n", 1)[0], cmd)   # keep the `cmd <<'EOF'` line, drop the body
    lex = shlex.shlex(cmd.replace("\n", " ; "), posix=True, punctuation_chars=True)
    lex.whitespace_split = True
    toks = list(lex)
    out, cur, piped = [], [], False
    for t in toks:
        if t in OPS:
            if cur:
                out.append((cur, piped))
            piped = t in ("|", "|&")
            cur = []
        else:
            cur.append(t)
    if cur:
        out.append((cur, piped))
    return out


def verdict(cmd):
    """None = allow, else the reason to refuse."""
    for words, piped in segments(cmd):
        redirect_in = any(w.startswith("<") for w in words)
        w = list(words)
        while w and (re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", w[0]) or w[0] in PREFIX):
            w.pop(0)
        if not w:
            continue
        if w[0] in ("timeout", "gtimeout"):
            continue                                            # bounded by our own guard: always fine
        name, args = os.path.basename(w[0]), w[1:]
        if name == "sleep":
            try:
                secs = sum(float(re.sub(r"[smhd]$", "", a)) * {"m": 60, "h": 3600, "d": 86400}.get(a[-1:], 1)
                           for a in args if not a.startswith("-"))
            except ValueError:
                secs = 99
            if secs > 2:
                return (f"`sleep {' '.join(args)}`: nothing is coming that a sleep waits for in this run -- do other "
                        "work and check again later (or `timeout N <cmd>` around a command that needs time)")
        elif name == "tail" and any(a in ("-f", "-F", "--follow") or (re.match(r"^-[^-]*[fF]", a) and a != "-n")
                                    for a in args):
            return "`tail -f` never returns: use `tail -n 50 FILE` (repeat later if needed)"
        elif name in PAGERS:
            return f"`{name}` is interactive and never returns here: use cat / head -n / sed -n 'A,Bp' / grep"
        elif name == "read" and not piped and not redirect_in:
            return "`read` waits on a keyboard nobody types on: read from a file (`read x < FILE`) or use a variable"
        elif name in REPLS and not piped and not redirect_in and (
                not args or "-i" in args or (name in ("python", "python3") and args == ["-"])):
            return (f"bare `{name}` opens a REPL that never returns: pass a script, `-c '...'`, or a heredoc "
                    f"(`{name} - <<'EOF' ... EOF`)")
        elif name in ("nc", "ncat", "netcat", "socat") and any(re.match(r"^-[a-zA-Z]*l", a) or a == "--listen"
                                                                for a in args):
            return f"`{name} -l` listens forever: wrap it in `timeout N` or test the other side without a listener"
        elif name == "ssh" and not any("BatchMode=yes" in a for a in args):
            return "`ssh` without `-o BatchMode=yes` can prompt for a password forever: add `-o BatchMode=yes -o ConnectTimeout=10`"
        elif name == "curl" and not any(a == "--max-time" or a.startswith("--max-time=") or re.match(r"^-[a-zA-Z]*m(\d*)$", a)
                                        for a in args):
            return "`curl` without `--max-time` can hang: add `--max-time 20`"
        elif name == "wget" and not any(a.startswith(("--timeout", "-T")) for a in args):
            return "`wget` without `--timeout` can hang: add `--timeout=20 --tries=1`"
    return None


def main():
    try:
        data = json.load(sys.stdin)
        if data.get("tool_name") != "Bash":
            return 0
        ti = data.get("tool_input") or {}
        if ti.get("run_in_background"):
            return 0
        why = verdict(str(ti.get("command") or ""))
    except Exception:  # noqa: BLE001 - fail open: a hook must never break the worker
        return 0
    if not why:
        return 0
    print(f"BLOCKED (unattended run, nothing may wait forever): {why}. Every command must be non-interactive and "
          "return on its own; redirect stdin from /dev/null for tools that may prompt (7z/unzip).", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
