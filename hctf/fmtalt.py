"""Deterministic SPELLING alternates for a value the GM just rejected (same content, different rendering).

The metadata worker had the right value by T+16-20 on D10 and D13 and still lost ~20 s each to its spelling: D10 an
entry-point RVA not zero-padded to the 8-digit struct width (`0x65bd0` -> `0x00065bd0`), D13 an MSI ProductCode
stripped of its braces (`XXXXXXXX-...` -> `{XXXXXXXX-...}`). The value's SHAPE + the field id say which renderings
exist; probing <= 3 of them costs ~1 s each inside the worker's own submit call, instead of an LLM retry turn.

  alternates(aid, value, q, exclude=())  ->  [(alt_value, transform_name), ...]  best first
  record(aid, transform)                 ->  remember which rendering the GM accepted for this field ending

Learned ordering lives in lib/format_conventions.json ({field_ending: {transform: count}}); it travels with lib/.
Never for flags, enums (accepted_values is the closed set), values already judged wrong, or renderings the local
format checks would refuse.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONV = ROOT / "lib" / "format_conventions.json"
_HEX = re.compile(r"(0[xX])?([0-9a-fA-F]+)")
_GUID = re.compile(r"\{?([0-9a-fA-F]{8})-([0-9a-fA-F]{4})-([0-9a-fA-F]{4})-([0-9a-fA-F]{4})-([0-9a-fA-F]{12})\}?")
_FLAG_HINT = re.compile(r"md5|\[0-9a-f\]\{32\}|32 lowercase hex|flag", re.I)


def ending(aid):
    """Field ending used as the convention key: 'd09-pe-001-pe-address-of-entry-point-rva-hex' -> 'rva-hex'."""
    parts = [p for p in re.split(r"[-_.]", aid.lower()) if p and not p.isdigit()]
    return "-".join(parts[-2:]) if len(parts) >= 2 else (parts[-1] if parts else aid.lower())


def _conventions():
    try:
        return json.loads(CONV.read_text())
    except (OSError, ValueError):
        return {}


def record(aid, transform):
    conv = _conventions()
    d = conv.setdefault(ending(aid), {})
    d[transform] = d.get(transform, 0) + 1
    try:
        CONV.write_text(json.dumps(conv, indent=1, sort_keys=True) + "\n")
    except OSError:
        pass


def _hex_alts(aid, v, af_text, ci):
    m = _HEX.fullmatch(v)
    if not m or not (m.group(1) or "hex" in aid.lower() or "hex" in af_text):
        return []
    body, had_0x = m.group(2), bool(m.group(1))
    digits = body.lstrip("0") or "0"
    out = []
    widths = [w for w in (2, 4, 8, 16) if w >= len(digits)]
    for w in widths[:2]:                       # smallest standard struct width that fits, then the next one up
        out.append((("0x" if had_0x else "") + digits.zfill(w).lower(), f"pad{w}"))
    fixes_prefix = "0x" in af_text
    if not fixes_prefix:
        out.append(((body if had_0x else "0x" + body).lower(), "toggle0x"))
    if not ci and "lowercase" not in af_text and "uppercase" not in af_text:
        out.append((("0x" if had_0x else "") + body.upper(), "upper"))
    return out


def _guid_alts(v, ci):
    m = _GUID.fullmatch(v)
    if not m:
        return []
    g = m.groups()
    plain = "-".join(g)
    le = "-".join(["".join(reversed([g[0][i:i + 2] for i in range(0, 8, 2)])),
                   "".join(reversed([g[1][i:i + 2] for i in range(0, 4, 2)])),
                   "".join(reversed([g[2][i:i + 2] for i in range(0, 4, 2)])), g[3], g[4]])
    out = [("{" + plain.upper() + "}", "braces-upper"), (plain.upper(), "bare-upper"), (plain.lower(), "bare-lower"),
           ("{" + plain.lower() + "}", "braces-lower"), (le.lower(), "bytes_le"), ("{" + le.upper() + "}", "bytes_le-braces")]
    if ci:
        out = [(a, t) for a, t in out if not t.endswith("upper")]
    return out


def _generic_alts(v):
    out = []
    s = v.strip()
    if s != v:
        out.append((s, "trim"))
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'`":
        out.append((s[1:-1], "unquote"))
    if s.endswith(".") and not s.endswith(".."):
        out.append((s[:-1], "strip-period"))
    return out


def alternates(aid, value, q=None, exclude=(), max_n=3):
    """Ranked spelling alternates of `value` for field `aid` (question dict `q`), excluding `exclude` and `value`."""
    q = q or {}
    v = str(value)
    af = q.get("answer_format") if isinstance(q.get("answer_format"), dict) else {}
    af_text = json.dumps(q.get("answer_format", "")).lower()
    if _FLAG_HINT.search(af_text) or re.fullmatch(r"[0-9a-f]{32}", v):
        return []
    if af.get("kind") == "enum" and af.get("accepted_values"):
        return []
    ci = q.get("normalization") == "case_insensitive"
    cands = _guid_alts(v, ci) or _hex_alts(aid, v, af_text, ci)
    cands += _generic_alts(v)
    learned = _conventions().get(ending(aid), {})
    cands.sort(key=lambda c: -learned.get(c[1], 0))          # stable: shape order breaks ties
    seen, out = {v, *map(str, exclude)}, []
    try:
        from . import cli
        bad = lambda a: cli._format_problem(a, q)  # noqa: E731
    except Exception:  # noqa: BLE001
        bad = lambda a: None  # noqa: E731
    for alt, t in cands:
        if alt in seen or bad(alt):
            continue
        seen.add(alt)
        out.append((alt, t))
        if len(out) >= max_n:
            break
    return out
