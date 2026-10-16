"""Generator for the DOSfuscated batch fixtures (bat_dosfu_*.bat). stdlib only; never imports lib.codec.

  python3 tests/data/script_fixtures/bat_dosfu_gen.py <style> <plan> > out.bat

Styles (Bohannon's Invoke-DOSfuscation families):
  substr   alphabet variable + plan rebuilt from %_k:~n,1% picks, caret-split keywords, echo(!p! under delayed exp.
  subst    junk-interleaved plan cleaned with %VAR:junk=% / delayed !VAR:@@=|! substitution and :~n / :~0,-m trims.
  decoy    the substr machinery spelling a benign, non-plan banner.
Oracle: .venv/bin/bat -D -Q (binref refinery batch emulator) prints the echo command lines it would execute.
"""
import random, sys

style, plan = sys.argv[1], sys.argv[2]
rnd = random.Random(1337 + len(plan))


def caret(word):
    return "".join(c + ("^" if rnd.random() < 0.4 and i < len(word) - 1 else "") for i, c in enumerate(word))


out = ["@echo off", "setlocal EnableExtensions EnableDelayedExpansion"]
if style in ("substr", "decoy"):
    alpha = sorted(set(plan + "qzQZ"), key=lambda _: rnd.random())
    k = "".join(alpha)
    out.append(f'{caret("set")} "_k={k}"')
    picks = []
    for ch in plan:
        i = k.index(ch)
        picks.append(f"%_k:~{i},1%" if rnd.random() < 0.5 else f"%_k:~{i - len(k)},1%")
    for n in range(0, len(picks), 12):
        out.append(f'{caret("set")} "p{n // 12}={"".join(picks[n:n + 12])}"')
    out.append('set "p=' + "".join(f"%p{n}%" for n in range((len(picks) + 11) // 12)) + '"')
    out.append(f"{caret('echo')}(!p!")
elif style == "subst":
    junk = "#Qz"
    noisy = junk.join(plan[i:i + 5] for i in range(0, len(plan), 5)).replace("|", "@@")
    out.append(f'set "_r=XXHDR{noisy}TRL"')
    out.append('set "_c=%_r:#Qz=%"')
    out.append('s^et "_c=%_c:~5%"')
    out.append('set "_c=!_c:~0,-3!"')
    out.append('set "_c=!_c:@@=|!"')
    out.append(f"{caret('echo')}(!_c!")
out = [ln for ln in out if ln]
out.append("exit /b 0")
sys.stdout.write("\r\n".join(out) + "\r\n")
