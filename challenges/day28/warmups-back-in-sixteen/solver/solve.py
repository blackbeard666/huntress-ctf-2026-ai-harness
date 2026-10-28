#!/usr/bin/env python3
"""Solver for this challenge -- harness skeleton. Fill in `answer()`; keep the I/O contract unchanged.

    solve.py --contract <contract.json> --artifacts <dir>   ->  prints {answer_id: value} as JSON on the last line

Runs on the Homebase VM inside a ~6-7 s window for EVERY Mastery set: stdlib + lib.* + pyzipper/pyelftools/pefile/
capstone/pycryptodome/androguard only, no subprocess to 7z/jadx/etc., all sets well under 1 s. Mastery questions name
their files like 'delivery 2: sample_02.apk' or 'evidence.zip -> member': `artifact_bytes()` resolves both (by sha256
pairing first, so same-named per-set deliveries never get mixed up)."""
import re
import argparse
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from lib.common import (container_by_sha, delivery_missing, find_artifact, group_by_set, load_contract,  # noqa: E402
                        normalize)
from lib import solverrt  # noqa: E402  -- partial-emit on deadline (cumulative-lane upgrade)

_cache = {}


def artifact_bytes(root, contract, artifact):
    """Bytes for a question's `artifact` string (cached per artifact)."""
    if artifact in _cache:
        return _cache[artifact]
    container, _, member = (x.strip() for x in artifact.partition("->"))
    data = None
    p = container_by_sha(root, contract, container)
    if p is not None and not member:
        data = p.read_bytes()
    elif not delivery_missing(root, contract, container):
        for cand in (artifact, container.split(": ", 1)[-1] + (f" -> {member}" if member else "")):
            try:
                data = find_artifact(root, cand)
                break
            except FileNotFoundError:
                continue
    _cache[artifact] = data
    return data


def answer(answer_id, question, data, contract):
    """Return the value for one answer_id from its artifact bytes (None = cannot answer). Derive everything from
    `data`; never hard-code a variant's values."""
    text = data.decode("utf-8", "replace") if isinstance(data, bytes) else data
    n = _netstr(text)  # D24 "String Theory": netstrings `len:data,` concatenated
    if n is not None and not re.match(r"\s*\d{2}\t", text):
        text = n
    o = _ook(text)  # D27 "Monkey Business": the whole blob is an Ook! program (Brainfuck in Ook. Ook? Ook! pairs)
    if o is not None:
        text = o
    if _BF_RE.fullmatch(text.strip()) and "." in text:  # D26 "Food for Thought": the whole blob is a Brainfuck program
        text = _bf(text) or text
    text = _uplus_lines(text)  # D25 "You Have a Point": Unicode code points `U+004E U+0069 ...`
    text = _a85_lines(text)  # D23 "Eighty-Five": Ascii85 (<~ ... ~>) whole blob or Mastery line
    z = _b64z(text)  # D21 single/TT: the whole blob is base64 of a compressed stream
    if z is not None:
        text = z
    if re.match(r"\s*\d{2}\t", text):  # Mastery: numbered lines, line k in day k's encoding (D15 = ROT47)
        m = _slug(decode.decode_chunked(text))
        if m:  # direct per-line decode hit: skip the costly joint-ranked search (60 s on 83 sets)
            return m
        m = _slug(_rail_lines(text))
        if m:
            return m
        cands = []
        try:
            cands += decode.decode_candidates(text, 5)
        except Exception:  # noqa: BLE001
            pass
    else:
        cands = [_hex_utf16(text), _railfence_best(text.strip("\r\n")), _baconhex(text), _morsehex(text), _rot47(text.strip())]
        try:
            cands.append(decode.decode_chunk(text.strip()))
        except Exception:  # noqa: BLE001
            pass
    for c in cands:
        m = _slug(c)
        if m:
            return m
    return None


def _netstr(t):
    """D24: a run of netstrings `<len>:<data>,` (len in chars) -> joined data; None unless the WHOLE text parses."""
    t = t.strip()
    out, i, n = [], 0, len(t)
    while i < n:
        m = re.compile(r"\s*(\d+):").match(t, i)
        if not m:
            return None
        k, j = int(m.group(1)), m.end()
        if j + k >= n + (0 if t.endswith(",") else 1) or t[j + k:j + k + 1] not in (",", ""):
            return None
        out.append(t[j:j + k])
        i = j + k + 1
    return "".join(out) if out else None


def _a85(frag):
    """D23: Ascii85 fragment (Adobe <~ ~> delimiters, or bare) -> text; compressed payload inflated."""
    import base64, bz2, gzip, lzma, zlib
    f = re.sub(r"\s+", "", frag)
    delim = f.startswith("<~") and f.endswith("~>")
    try:
        b = base64.a85decode(f, adobe=True) if delim else base64.a85decode(f)
    except Exception:  # noqa: BLE001
        return None
    for magic, kind in _ZMAGIC:
        if b.startswith(magic):
            try:
                b = {"gzip": gzip.decompress, "bz2": bz2.decompress, "lzma": lzma.decompress,
                     "zlib": zlib.decompress}[kind](b)
            except Exception:  # noqa: BLE001
                pass
            break
    try:
        r = b.decode("utf-8")
    except Exception:  # noqa: BLE001
        return None
    return r if r and (r.isprintable() or "\n" in r) else None


def _a85_lines(text):
    """Decode a whole-blob <~...~> Ascii85, or each Mastery `NN\t<~...~>` line, in place."""
    t = text.strip()
    if t.startswith("<~") and t.endswith("~>") and "\t" not in t:
        return _a85(t) or text
    if decode is not None:  # Mastery: line 23 is decoded by the registered day-23 codec (positional/joint), not here --
        return text         # a pre-decoded plain line is re-"decoded" as an unknown last line (et-54 -> et-09)
    def sub(m):
        d = _a85(m.group(2))
        return m.group(1) + d if d is not None and "\n" not in d else m.group(0)
    return re.sub(r"(?m)^(\s*\d{2}\t)(<~.*?~>)\s*$", sub, text)


_ZMAGIC = ((b"\x1f\x8b", "gzip"), (b"BZh", "bz2"), (b"\xfd7zXZ", "lzma"), (b"\x78", "zlib"))


def _b64z(t):
    """D21 "A familiar wrapper. Something compressed inside": base64 (std or url-safe, padding optional) of a
    gzip/zlib/bz2/xz stream -> its UTF-8 text (None if the fragment isn't that)."""
    import base64, bz2, gzip, lzma, zlib
    t = re.sub(r"\s+", "", t.strip().strip('"'))
    if len(t) < 12 or len(t) % 4 == 1 or not re.fullmatch(r"[A-Za-z0-9+/_-]+={0,2}", t):
        return None
    try:
        b = base64.urlsafe_b64decode(t.replace("+", "-").replace("/", "_").rstrip("=") + "=" * (-len(t.rstrip("=")) % 4))
    except Exception:  # noqa: BLE001
        return None
    for magic, kind in _ZMAGIC:
        if b.startswith(magic):
            try:
                raw = {"gzip": gzip.decompress, "bz2": bz2.decompress, "lzma": lzma.decompress,
                       "zlib": zlib.decompress}[kind](b)
                return raw.decode("utf-8")
            except Exception:  # noqa: BLE001
                return None
    return None


def _hex_utf16(t):
    """D19: hex of UTF-16 bytes (BOM fffe/feff, or BOM-less alternating NULs)."""
    t = re.sub(r"\s+", "", t)
    if not re.fullmatch(r"(?:[0-9a-fA-F]{2})+", t):
        return None
    b = bytes.fromhex(t)
    for enc in (("utf-16",) if b[:2] in (b"\xff\xfe", b"\xfe\xff") else ("utf-16-le", "utf-16-be")):
        try:
            r = b.decode(enc)
        except Exception:  # noqa: BLE001
            continue
        if r.isprintable() or "\n" in r:
            return r
    return None


def _rail_dec(c, r, off=0):
    """D18: rail-fence (zigzag) decrypt with r rails, start offset off."""
    n = len(c)
    cyc = 2 * (r - 1)
    pat = [(p if p < r else cyc - p) for p in ((i + off) % cyc for i in range(n))]
    idx = sorted(range(n), key=lambda i: (pat[i], i))
    out = [""] * n
    for k, i in enumerate(idx):
        out[i] = c[k]
    return "".join(out)


def _railfence_best(t):
    """D18 "Three rails": anagram of the crib sentence -> rail fence. Prefer 3 rails, offset 0; then others."""
    if not t or len(t) < 4:
        return None
    tries = [(3, 0)] + [(r, o) for r in range(2, 12) for o in range(2 * (r - 1)) if (r, o) != (3, 0)]
    for r, o in tries:
        if r >= len(t):
            break
        d = _rail_dec(t, r, o)
        if re.search(r"Master:\s*[a-z]+-[a-z]+-[a-z]+-\d{2}\s*$", d):
            return d
    return None


def _rail_lines(text):
    """Mastery fallback: decode each numbered line by decode_chunk, but rail-fence (3 rails) any one line."""
    rows = [re.match(r"\s*(\d+)\t(.*)$", ln) for ln in text.splitlines()]
    rows = sorted((int(m.group(1)), m.group(2)) for m in rows if m)
    base = []
    for _, f in rows:
        try:
            base.append(decode.decode_chunk(f) or "")
        except Exception:  # noqa: BLE001
            base.append("")
    for i, (_, f) in enumerate(rows):
        for r, o in ((3, 0), (2, 0), (3, 1), (3, 2), (3, 3)):
            if r >= len(f):
                continue
            cand = "".join(base[:i]) + _rail_dec(f, r, o) + "".join(base[i + 1:])
            if _slug(cand):
                return cand
    return None


def _morsehex(s):
    """D16: Morse code whose symbols are hex digits of the UTF-8 text (or plain Morse text)."""
    t = s.strip().strip('"')
    if not t or not re.fullmatch(r"[.\-/ \t\r\n]+", t) or not re.search(r"[.\-]", t):
        return None
    try:
        from lib.ciphers import morse_decode
        m = morse_decode(t)
    except Exception:  # noqa: BLE001
        return None
    h = re.sub(r"\s", "", m or "")
    if re.fullmatch(r"(?:[0-9A-Fa-f]{2})+", h):
        try:
            return bytes.fromhex(h).decode("utf-8")
        except Exception:  # noqa: BLE001
            pass
    return m.lower() if m else None


def _baconhex(s):
    """D17: Baconian 5-symbol a/b groups; each group's index (a=0, b=1) is one hex nibble of the UTF-8 text
    ("Sixteen guests"). Groups >= 16 -> plain Bacon letters (26-letter, else 24-letter I=J/U=V alphabet)."""
    t = s.strip().strip('"')
    if not t or not re.fullmatch(r"[abAB\s]+", t):
        return None
    bits = re.sub(r"\s", "", t).lower().replace("a", "0").replace("b", "1")
    if not bits or len(bits) % 5:
        return None
    vals = [int(bits[i:i + 5], 2) for i in range(0, len(bits), 5)]
    if max(vals) < 16 and len(vals) % 2 == 0:
        try:
            return bytes.fromhex("".join("%x" % v for v in vals)).decode("utf-8")
        except Exception:  # noqa: BLE001
            pass
    a26 = "abcdefghijklmnopqrstuvwxyz"
    if max(vals) < 26:
        return "".join(a26[v] for v in vals)
    return None


_UTOK = r"(?:[Uu]\+|\\[Uu]|%[Uu]|0x)([0-9A-Fa-f]{2,8})"


_BF_RE = re.compile(r"[+\-<>\[\].,\s]+")


def _bf(prog, max_steps=5_000_000):
    """D26: run a Brainfuck program (8-bit wrapping cells, no input) -> its output text, or None."""
    c = re.sub(r"[^+\-<>\[\].]", "", prog)
    st, jmp = [], {}
    for j, ch in enumerate(c):
        if ch == "[":
            st.append(j)
        elif ch == "]":
            if not st:
                return None
            k = st.pop()
            jmp[k], jmp[j] = j, k
    if st:
        return None
    t, p, i, out, n = [0] * 65536, 0, 0, [], 0
    try:
        while i < len(c) and n < max_steps:
            ch = c[i]
            if ch == "+":
                t[p] = (t[p] + 1) & 255
            elif ch == "-":
                t[p] = (t[p] - 1) & 255
            elif ch == ">":
                p += 1
            elif ch == "<":
                p -= 1
            elif ch == ".":
                out.append(chr(t[p]))
            elif ch == "[" and not t[p]:
                i = jmp[i]
            elif ch == "]" and t[p]:
                i = jmp[i]
            i += 1
            n += 1
    except IndexError:
        return None
    r = "".join(out)
    return r if r and (r.isprintable() or "\n" in r) else None


_OOK = {"Ook. Ook?": ">", "Ook? Ook.": "<", "Ook. Ook.": "+", "Ook! Ook!": "-", "Ook! Ook.": ".", "Ook. Ook!": ",",
        "Ook! Ook?": "[", "Ook? Ook!": "]"}


def _ook(t):
    """D27: Ook! (token pairs of `Ook.`/`Ook?`/`Ook!`, = Brainfuck) -> program output text, or None."""
    toks = re.findall(r"Ook([.?!])", t, re.I)
    if not toks or len(toks) % 2 or re.sub(r"(?i)Ook[.?!]|\s", "", t):
        return None
    try:
        prog = "".join(_OOK["Ook%s Ook%s" % (toks[i], toks[i + 1])] for i in range(0, len(toks), 2))
    except KeyError:
        return None
    return _bf(prog)


def _ook_enc(s):
    inv = {v: k for k, v in _OOK.items()}
    return " ".join(inv[c] for c in "".join("+" * ord(ch) + ".>" for ch in s))


def _ook_dec(t):
    r = _ook(t)
    if r is None:
        raise ValueError("not ook")
    return r


try:  # Mastery line 26: positional day codec, registered at runtime (lib/warmups_codecs has no day 26 yet)
    from lib import warmups_codecs as _wc
    if _wc.day_codec(26) is None:
        _wc.DAYS.append((26, "brainfuck", lambda s: "".join("+" * ord(ch) + ".>" for ch in s), _bf, False))
    if _wc.day_codec(27) is None:  # Mastery line 27: Ook!
        _wc.DAYS.append((27, "ook", _ook_enc, _ook_dec, False))
except Exception:  # noqa: BLE001
    pass


def _uplus(frag):
    """D25: a fragment made only of code-point tokens (U+XXXX, also u+/\\u/\\U/%u/0x forms) -> the characters."""
    f = frag.strip()
    if not f or not re.fullmatch(r"(?:%s[\s,;]*)+" % _UTOK, f):
        return None
    try:
        return "".join(chr(int(h, 16)) for h in re.findall(_UTOK, f))
    except (ValueError, OverflowError):
        return None


def _uplus_lines(text):
    if not re.search(r"[Uu]\+[0-9A-Fa-f]{4}", text):
        return text
    w = _uplus(text)
    if w is not None and not re.match(r"\s*\d{2}\t", text):
        return w
    if decode is not None:  # Mastery: line 25 goes through the registered day-25 codec (positional), like _a85_lines --
        return text         # a pre-decoded plain line is re-"decoded" as an unknown last line (le-52 -> ...-07)
    out = []
    for line in text.splitlines():
        m = re.match(r"(\s*\d{2}\t)(.*)$", line)
        if m:
            d = _uplus(m.group(2))
            if d is not None and "\n" not in d:
                line = m.group(1) + d
        out.append(line)
    return "\n".join(out)


def _rot47(s):
    return "".join(chr(33 + (ord(ch) - 33 + 47) % 94) if 33 <= ord(ch) <= 126 else ch for ch in s)


def _slug(c):
    if isinstance(c, (list, tuple)):
        c = c[0] if c and isinstance(c[0], str) else (c[1] if len(c) > 1 and isinstance(c[1], str) else "")
    if not isinstance(c, str):
        return None
    lines = [l for l in c.splitlines() if l.strip()]
    if not lines:
        return None
    m = re.search(r"([a-z]+(?:-[a-z]+){2}-\d{2})\s*$", lines[-1])
    return m.group(1) if m else None


try:
    from lib import decode
    decode.register_free("rot47", 15, lambda p: [_rot47(p)])
    decode.register_free("morsehex", 16, lambda p: [x for x in [_morsehex(p)] if x])
    decode.register_free("baconhex", 17, lambda p: [x for x in [_baconhex(p)] if x])
    decode.register_free("b64z", 21, lambda p: [x for x in [_b64z(p)] if x])
    decode.register_free("netstr", 24, lambda p: [x for x in [_netstr(p)] if x])
    decode.register_free("uplus", 25, lambda p: [x for x in [_uplus(p)] if x and "\n" not in x])
    decode.register_free("a85", 23, lambda p: [x for x in [_a85(p)] if x and "\n" not in x]
                         if re.fullmatch(r"\s*<~.*~>\s*", p) else [])
except Exception:  # noqa: BLE001
    decode = None


def fallback(answer_id, question, data, contract):
    """Called ONLY when answer() found nothing (None or an exception): a cheap generic second try for a variant shape
    the direct parse doesn't know (Time Trial / Mastery mutate the task) -- e.g. the lane lib's name-agnostic decoder
    over `data`, then a match against question["answer_format"]. None = give up on this field only."""
    return None


def _past_deadline():
    """The timed runner's HCTF_SOLVE_DEADLINE (epoch) has passed: print the answers found so far instead."""
    try:
        return time.time() > float(os.environ["HCTF_SOLVE_DEADLINE"])
    except (KeyError, ValueError):
        return False


def _solve_pairs(job):
    """Answer one group of (answer_id, question) pairs -- a whole Mastery set, or the whole contract."""
    root, contract, pairs = job
    out = {}
    for aid, q in pairs:
        data = artifact_bytes(root, contract, q.get("artifact") or "")
        try:
            v = answer(aid, q, data, contract)
        except Exception as e:  # noqa: BLE001 - one bad field must not sink the other answers
            print(f"{aid}: {e!r}", file=sys.stderr)
            v = None
        if v is None and not _past_deadline():   # in-window: never let a fallback search eat the kill margin
            try:
                v = fallback(aid, q, data, contract)
            except Exception as e:  # noqa: BLE001
                print(f"{aid}: fallback {e!r}", file=sys.stderr)
        if v is not None:
            out[aid] = normalize(v, q)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", required=True)
    ap.add_argument("--artifacts", required=True)
    a = ap.parse_args()
    contract, pairs = load_contract(a.contract)
    groups = group_by_set(pairs)
    # out/pool are shared with the deadline watchdog: if the solve runs past HCTF_SOLVE_DEADLINE, whatever has been
    # collected so far is printed (a partial the untimed runner finishes in-attempt) instead of being SIGKILLed with no
    # output (which scores exec_error and forces a blocking generalize). run_sets merges each Mastery set as it finishes
    # (one forked process per set), then emit_and_exit prints once, kills any lingering pool/probe child, and os._exit(0).
    out, pool = {}, []
    solverrt.arm_deadline(out, pool)
    jobs = [(a.artifacts, contract, g) for g in groups.values()] if len(groups) >= 2 else [(a.artifacts, contract, pairs)]
    solverrt.run_sets(jobs, _solve_pairs, out, pool)
    solverrt.emit_and_exit(out, pool)


if __name__ == "__main__":
    main()
