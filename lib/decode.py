"""Generic layered decoder for the warmups lane (and any 'peel the encodings' task).

peel(data) does a breadth-first search over decode steps (base64/32/85/a85, hex, binary, gzip/zlib/bz2/xz,
url, rot-N, single-byte xor, reversal, decimal char codes) and returns the first decoded text that an
`accept` predicate recognizes, plus the chain of steps taken. Variant-proof: detects layers, no fixed list.
"""
import base64
import binascii
import bz2
import codecs
import gzip
import io
import json
import lzma
import math
import os
import re
import time
import urllib.parse
import zlib
import zipfile
from urllib.parse import unquote_to_bytes

_B64 = re.compile(rb"^[A-Za-z0-9+/=\s]+$")
_B64URL = re.compile(rb"^[A-Za-z0-9_\-=\s]+$")
_B32 = re.compile(rb"^[A-Z2-7=\s]+$")
_HEX = re.compile(rb"^(?:[0-9a-fA-F]{2}[\s:]*)+$")
_BIN = re.compile(rb"^[01\s]+$")


def _printable(b):
    try:
        s = b.decode("utf-8")
    except Exception:
        return None
    return s if s and sum(c.isprintable() or c in "\r\n\t" for c in s) / len(s) > 0.95 else None


def _candidates(b):
    s = b.strip()
    for magic, fn in ((b"\x1f\x8b", gzip.decompress), (b"BZh", bz2.decompress),
                      (b"\xfd7zXZ", lzma.decompress), (b"x", zlib.decompress)):
        if b.startswith(magic):
            try:
                yield "z:" + magic.hex(), fn(b)
            except Exception:
                pass
    if b.startswith(b"PK\x03\x04"):
        try:
            with zipfile.ZipFile(io.BytesIO(b)) as z:
                yield "zip", b"\n".join(z.read(n) for n in z.namelist())
        except Exception:
            pass
    compact = re.sub(rb"\s+", b"", s)
    if compact:
        if _BIN.match(s) and len(compact) % 8 == 0:
            yield "bin", int(compact, 2).to_bytes(len(compact) // 8, "big")
        if _HEX.match(s):
            try:
                yield "hex", binascii.unhexlify(re.sub(rb"[\s:]", b"", s))
            except Exception:
                pass
        if _B32.match(s) and len(compact) % 8 == 0:
            try:
                yield "b32", base64.b32decode(compact)
            except Exception:
                pass
        if _B64.match(s):
            try:
                yield "b64", base64.b64decode(compact + b"=" * (-len(compact) % 4), validate=True)
            except Exception:
                pass
        if _B64URL.match(s):
            try:
                yield "b64url", base64.urlsafe_b64decode(compact + b"=" * (-len(compact) % 4))
            except Exception:
                pass
        for name, fn in (("b85", base64.b85decode), ("a85", base64.a85decode)):
            try:
                yield name, fn(compact)
            except Exception:
                pass
    if b"%" in s:
        yield "url", unquote_to_bytes(s)
    t = _printable(b)
    if t is not None:
        # strip a leading per-line index/prefix like "01\t", "1: ", "3 - " (seen in Mastery variants)
        stripped = "\n".join(re.sub(r"^\s*\d+\s*[:.\-\t ]\s*", "", ln) for ln in t.splitlines())
        if stripped != t:
            yield "deprefix", stripped.encode()
        # also try just the longest line (prompts sometimes wrap the payload in chatter)
        longest = max(t.splitlines(), key=len, default="")
        if longest and longest != t.strip():
            yield "longline", longest.encode()
        yield "rev", t[::-1].encode()
        if re.fullmatch(r"[\d\s,]+", t.strip()) and re.search(r"\d", t):
            try:
                yield "dec", bytes(int(x) for x in re.split(r"[\s,]+", t.strip()) if x)
            except Exception:
                pass
        for n in range(1, 26):
            yield f"rot{n}", bytes(((c - 65 + n) % 26 + 65) if 65 <= c <= 90 else
                                   ((c - 97 + n) % 26 + 97) if 97 <= c <= 122 else c for c in t.encode())


def _expand(data):
    yield from _candidates(data)
    if _printable(data) is None:
        for k in range(1, 256):
            x = bytes(c ^ k for c in data)
            if _printable(x):
                yield f"xor{k:#x}", x


def solve_deadline():
    """Epoch by which an in-window solver must stop searching (HCTF_SOLVE_DEADLINE, set by the timed runner), or None."""
    try:
        return float(os.environ["HCTF_SOLVE_DEADLINE"])
    except (KeyError, ValueError):
        return None


def peel(data, accept, max_nodes=60000, deadline=None):
    """BFS; return (accepted_text, [steps]) for the shortest chain whose output `accept(text)` is truthy. Gives up
    (None, []) at `deadline` / HCTF_SOLVE_DEADLINE, whichever is first: one 60k-node search is ~6 s (D12 warmups)."""
    if isinstance(data, str):
        data = data.encode()
    ends = [d for d in (deadline, solve_deadline()) if d]
    end = min(ends) if ends else None
    seen, frontier, n = {data}, [(data, ())], 0
    while frontier:
        nxt = []
        for cur, path in frontier:
            if end is not None and time.time() > end:
                return None, []
            t = _printable(cur)
            if t is not None and accept(t):
                return t, list(path)
            for name, out in _expand(cur):
                n += 1
                if out and out not in seen and n < max_nodes:
                    seen.add(out)
                    nxt.append((out, path + (name,)))
        frontier = nxt
    return None, []


# Numbered mixed-encoding chunks ("NN<TAB>payload" per line, each line its own encoding, split mid-word), from
# Day 6 "Eight Is Enough" Mastery (GM-confirmed 28/28 sets): decode each chunk by its own strict format, join in
# index order WITHOUT trimming chunk spaces. decode_chunked() returns None when the text is not chunked.
_CHUNK = re.compile(r"^(\d+)(?:\t|[:.)|\]] )(.*)$")
_NUMS = re.compile(r"^\d{1,3}(?:[\s,]+\d{1,3})*$")
_BINS = re.compile(r"^[01]{8}(?:[\s,]*[01]{8})*$")
_HEXS = re.compile(r"^(?:[0-9a-fA-F]{2})+$")
_B64S = re.compile(r"^[A-Za-z0-9+/]+={0,2}$")
_B32S = re.compile(r"^[A-Z2-7]+=*$")
_B64U = re.compile(r"^[A-Za-z0-9_-]+={0,2}$")
# English letter frequencies (%), for picking a rot-N shift on short chunks
_FREQ = dict(zip("abcdefghijklmnopqrstuvwxyz",
                 (8.2, 1.5, 2.8, 4.3, 12.7, 2.2, 2.0, 6.1, 7.0, 0.15, 0.77, 4.0, 2.4, 6.7, 7.5, 1.9, 0.095,
                  6.0, 6.3, 9.1, 2.8, 0.98, 2.4, 0.15, 2.0, 0.074)))


def _ascii(b):
    """Printable ASCII text (plus \\t\\r\\n) or None."""
    if b and all(32 <= c < 127 or c in (9, 10, 13) for c in b):
        return b.decode()
    return None


def _wordy(s):
    return sum(c.isalnum() or c in " .,!?:;'-_\n" for c in s) / max(len(s), 1)


def _rot(s, n):
    return "".join(chr((ord(c) - 97 + n) % 26 + 97) if "a" <= c <= "z" else
                   chr((ord(c) - 65 + n) % 26 + 65) if "A" <= c <= "Z" else c for c in s)


def _atbash(s):
    """a<->z mirror (warmups Day 13 "Opposite Day"); digits/punctuation kept. Its own inverse, and no rot-N equals it."""
    return "".join(chr(219 - ord(c)) if "a" <= c <= "z" else chr(155 - ord(c)) if "A" <= c <= "Z" else c for c in s)


def _eng(s):
    letters = [c for c in s.lower() if "a" <= c <= "z"]
    return sum(math.log(_FREQ[c]) for c in letters) / max(len(letters), 1)


# English letter-pair frequencies (% of all bigrams; standard corpus table + rare-but-valid pairs). Unigram scoring
# (`_eng`) picked the wrong rot-N for ~27% of short lines (rot16 'Dysu meha tusetydw' outscored 'Nice work decoding');
# bigram log-likelihood recovers 98% of every GM warmups answer under all 25 shifts.
_BIGRAM = {t[:2]: float(t[2:]) / 100 for t in (
    "th3.56 he3.07 in2.43 er2.05 an1.99 re1.85 on1.76 at1.49 en1.45 nd1.35 ti1.34 es1.34 or1.28 te1.20 of1.17 ed1.17 "
    "is1.13 it1.12 al1.09 ar1.07 st1.05 to1.04 nt1.04 ng.95 se.93 ha.93 as.87 ou.87 io.83 le.83 ve.83 co.79 me.79 "
    "de.76 hi.76 ri.73 ro.73 ic.70 ne.69 ea.69 ra.69 ce.65 li.62 ch.60 ll.58 be.58 ma.57 si.55 om.55 ur.54 ca.54 "
    "el.53 ta.53 la.52 ns.51 di.50 fo.50 ho.50 pe.49 ec.48 pr.47 no.47 ct.46 us.45 ac.45 ot.44 il.43 tr.43 ly.43 "
    "nc.42 et.42 ut.41 ss.41 so.40 rs.40 un.39 lo.38 wa.38 ge.38 ie.38 wh.37 ee.37 wi.37 em.37 ad.36 ol.36 rt.36 "
    "po.35 we.35 na.35 ul.35 ni.34 ts.34 mo.34 ow.33 pa.33 im.33 mi.33 ai.32 sh.32 ir.32 su.31 id.30 os.29 iv.29 "
    "ia.29 am.28 fi.28 ci.28 vi.27 pl.27 ig.26 tu.26 ev.25 ld.25 ry.25 mp.24 fe.24 bl.24 ab.23 gh.23 ty.22 op.22 "
    "wo.22 sa.22 ay.21 ex.21 ke.21 fr.21 oo.21 av.21 ag.21 if.20 ap.20 gr.20 od.20 bo.20 sp.19 rd.19 do.19 uc.19 "
    "bu.19 ei.18 ov.18 by.18 rm.18 ep.17 tt.17 oc.17 fa.17 ef.17 cu.17 rn.16 sc.16 gi.16 da.16 yo.16 cr.16 cl.16 "
    "du.16 ga.16 qu.15 ue.15 ff.15 ba.15 ey.15 ls.15 va.14 um.14 pp.14 ua.14 up.14 lu.14 go.14 ht.14 ru.14 ug.13 "
    "ds.13 lt.13 pi.13 rc.13 rr.13 eg.13 au.13 ck.13 ew.13 mu.13 br.13 bi.12 pt.12 ak.12 pu.12 ui.12 rg.12 ib.12 "
    "tl.12 ny.11 ki.11 rk.11 ys.11 ob.11 mm.11 fu.11 ph.10 og.10 ms.10 ye.10 ud.10 mb.10 ip.10 ub.10 oi.10 rl.10 "
    "gu.10 dr.10 hr.10 cc.10 tw.09 ft.09 wn.09 nu.09 af.08 hu.08 nn.08 eo.08 vo.08 rv.08 nf.08 xp.08 gn.07 sm.07 "
    "fl.07 iz.07 ok.07 nl.07 my.07 gl.07 aw.07 ju.07 oa.07 sy.07 sl.07 ps.07 jo.06 rf.06 na.06 dv.06 ze.06 kn.06"
).split()}
_BIGRAM.update({k: v for k, v in {
    "zz": .0007, "zy": .0004, "py": .0012, "ky": .0007, "zi": .0005, "za": .0006, "az": .0006, "ze": .0006, "ap": .002,
    "ja": .0004, "je": .0004, "ji": .0003, "xi": .0004, "xa": .0003, "ox": .0003, "ix": .0003, "ax": .0003, "wl": .0003,
    "wr": .0004, "dg": .0005, "nk": .0008, "sk": .0008, "ek": .0004, "lk": .0003, "yl": .0004, "ym": .0003, "yn": .0002,
    "rb": .0007, "lm": .0004, "lp": .0004, "lv": .0003, "mn": .0002, "nv": .0004, "nj": .0003, "tz": .0002,
}.items() if k not in _BIGRAM})


def _bigram(s):
    """Mean log-probability of the letter pairs inside words (higher = more English)."""
    pairs = [w[i:i + 2] for w in re.findall(r"[a-z]+", s.lower()) for i in range(len(w) - 1)]
    return sum(math.log(_BIGRAM.get(x, 0.00005)) for x in pairs) / len(pairs) if pairs else -12.0


def _best_rot(p):
    return max((_rot(p, n) for n in range(26)), key=lambda s: (_bigram(s), _eng(s), s == _rot(p, 13)))


def decode_chunk(p, _nested=False):
    """Decode one chunk payload by its own format; strict formats first, rot-N last."""
    t = p.strip()
    cands = []  # (decoded_text, priority)
    if re.fullmatch(r"(?:%[0-9A-Fa-f]{2}|[^%\s])+", t) and len(re.findall(r"%[0-9A-Fa-f]{2}", t)) * 3 >= len(t) // 2:
        # URL percent-encoding (warmups Day 7 "Percent Chance": line 7 = '%2d%69%73...'), mostly %XX by length
        cands.append((_ascii(urllib.parse.unquote_to_bytes(t)), 0))
    if re.fullmatch(r"(?:&(?:#\d+|#[xX][0-9a-fA-F]+|[A-Za-z]+\d*);)+", t):
        # HTML character entities (warmups Day 8 "Entity Relations": line 8 = '&#109;&#109;&#105;...'), whole fragment
        import html
        cands.append((html.unescape(t), 0))
    if re.fullmatch(r'"?(?:\\(?:u[0-9a-fA-F]{4}|x[0-9a-fA-F]{2}|[nrtbf"\\/]))+"?', t):
        # JSON/C string escapes (warmups Day 9 "Escape Room": line 9 = '"\u0065\u0072\u002d..."'), whole fragment
        q = t[1:-1] if len(t) >= 2 and t[0] == t[-1] == '"' else t
        try:
            cands.append((q.encode().decode("unicode_escape") if "\\x" in q else json.loads('"' + q + '"'), 0))
        except (ValueError, UnicodeDecodeError):
            pass
    if _BINS.match(t):
        bits = re.sub(r"[\s,]", "", t)
        cands.append((_ascii(int(bits, 2).to_bytes(len(bits) // 8, "big")), 0))
    if _NUMS.match(t):
        toks = re.split(r"[\s,]+", t)
        padded = any(len(x) == 3 and x[0] == "0" for x in toks)
        if all(re.fullmatch(r"[0-7]+", x) for x in toks) and max(int(x, 8) for x in toks) < 256:
            cands.append((_ascii(bytes(int(x, 8) for x in toks)), 1 if padded else 2))
        if max(int(x) for x in toks) < 256:
            cands.append((_ascii(bytes(int(x) for x in toks)), 3 if padded else 1))
    if _HEXS.match(t):
        cands.append((_ascii(binascii.unhexlify(t)), 4))
    if _B32S.match(t) and len(t) % 8 == 0:
        try:
            cands.append((_ascii(base64.b32decode(t)), 5))
        except Exception:
            pass
    if _B64S.match(t) and len(t) % 4 == 0:
        try:
            cands.append((_ascii(base64.b64decode(t, validate=True)), 6))
        except Exception:
            pass
    if _B64U.match(t) and len(t.rstrip("=")) % 4 != 1 and ("-" in t or "_" in t or len(t) % 4):
        # URL-safe base64, '=' padding dropped (warmups Day 11 "Safe Travels": whole 147-char blob, len % 4 == 3)
        try:
            u = t.rstrip("=")
            cands.append((_ascii(base64.urlsafe_b64decode(u + "=" * (-len(u) % 4))), 6))
        except Exception:
            pass
    good = [(s, pr) for s, pr in cands if s is not None and _wordy(s) >= 0.85]
    if good:
        return min(good, key=lambda x: (-round(_wordy(x[0]), 2), x[1]))[0]
    if _nested:
        return None
    # An encoding none of the classes above names (a new line encoding on a new day): try the other text encodings
    # lib knows -- reversed text of a strict class, \\u/\\x escapes, HTML entities, Morse, base58, quoted-printable,
    # base85 -- and keep one only if it reads more like English than the best rot-N of the raw line.
    gen = [g for g in _generic_chunk(t) if g and _wordy(g) >= 0.85]
    best_rot = _best_rot(p) if re.search(r"[A-Za-z]", p) else None
    if gen:
        g = max(gen, key=_bigram)
        if best_rot is None or (re.search(r"[A-Za-z]", g) and _bigram(g) > _bigram(best_rot)):
            return g
    # plain REVERSED text (warmups Day 12 "Back at You": line 12 = '69-enud-m' -> 'm-dune-96', whole blob
    # '56-ztrauq-... :retsaM emaG'): a leading 'NN-word' is a reversed slug tail, else keep the reversal only if it
    # reads more like English than every rot-N (rot-N of '69-enud-m' gives 'fove'; 0 hits on Days 3-11 fragments)
    if best_rot is not None and re.fullmatch(r"\d{2,}-[A-Za-z][A-Za-z-]*", t):
        return t[::-1]
    # ATBASH (warmups Day 13 "Opposite Day", "A met Z": whole blob 'Mrxv dlip wvxlwrmt ... gsv Tznv Nzhgvi: <slug>'):
    # best rot-N of Atbash text is gibberish (rot22 'Intr zhel ...' was submitted and rejected), so the mirror competes
    # with rot-N and the reversal on bigram score and must beat both.
    if best_rot is not None:
        atb = _atbash(p)
        if _bigram(atb) > max(_bigram(best_rot), _bigram(t[::-1])):
            return atb
        if _bigram(t[::-1]) > _bigram(best_rot):
            return t[::-1]
    # free text: plain or rot-N (pick the shift that reads most like English); keep spacing exactly
    return best_rot if best_rot is not None else p


def _generic_chunk(t):
    from lib import ciphers
    import html
    out = []
    rev = decode_chunk(t[::-1], _nested=True)
    if rev:
        out.append(rev)
    esc = re.findall(r"\\+u([0-9a-fA-F]{4})|\\+x([0-9a-fA-F]{2})", t)
    if esc and len("".join(a or b for a, b in esc)) * 1.5 >= len(t) // 2:
        out.append(_ascii(bytes(int(a or b, 16) for a, b in esc if int(a or b, 16) < 256)))
    if "&#" in t or "&" in t and ";" in t:
        out.append(html.unescape(t))
    if re.fullmatch(r"[.\-/ ]+", t) and "." in t:
        out.append(ciphers.morse_decode(t))
    if re.fullmatch(r"(?:=[0-9A-Fa-f]{2}|[^=\s])+", t) and t.count("=") >= 2:
        out.append(ciphers.quoted_printable_decode(t))
    if re.fullmatch(r"[1-9A-HJ-NP-Za-km-z]{4,}", t):
        try:
            out.append(_ascii(ciphers.base58_decode(t)))
        except Exception:  # noqa: BLE001
            pass
    for fn in (base64.b85decode, base64.a85decode):
        try:
            out.append(_ascii(fn(t)))
        except Exception:  # noqa: BLE001
            pass
    return [x for x in out if x]


# Warmups Mastery: line k is encoded with day k's codec. The FREE-TEXT codecs (no alphabet signature) are told apart only
# by how English the result reads, which per-line guessing gets wrong on short fragments (D13: Atbash put on '-tliuq-d').
# Each is used ONCE per blob -> (name, day introduced); a blob of k lines can only contain codecs of days <= k.
FREE_CODECS = (("rot", 2), ("rev", 12), ("atb", 13))
_SLUG_END = re.compile(r"[a-z]+(?:-[a-z]+)+-\d{2,}\s*$")


def _free_line(p):
    """A letter-bearing fragment no strict codec claims: decode_chunk fell through to rot-N / reversal / Atbash."""
    t = p.strip()
    if not re.search(r"[A-Za-z]", t):
        return False
    d = decode_chunk(p)
    return d is not None and (d.strip() == t[::-1] or d == _atbash(p) or any(d == _rot(p, n) for n in range(26)))


def _free_cands(name, p):
    if name == "rev":
        return [p.strip()[::-1] if p.strip() == p else p[::-1]]
    if name == "atb":
        return [_atbash(p)]
    best = _best_rot(p)
    return [best] + ([_rot(p, 13)] if _rot(p, 13) != best else [])


def _joint_free(rows):
    """Assign the free-text codecs to the free lines jointly (each codec once, only days <= the blob's last line) and
    keep the assignment whose text ends in a slug, then reads most like English. None = no consistent assignment."""
    import itertools
    kmax = max(k for k, _ in rows)
    free = [i for i, (_, p) in enumerate(rows) if _free_line(p)]
    names = [n for n, day in FREE_CODECS if kmax >= day]
    if not free or len(free) > len(names):
        return None
    fixed = [None if i in free else decode_chunk(p) for i, (_, p) in enumerate(rows)]
    if any(x is None for i, x in enumerate(fixed) if i not in free):
        return None
    best = None
    for combo in itertools.permutations(names, len(free)):
        for picks in itertools.product(*(_free_cands(n, rows[i][1]) for n, i in zip(combo, free))):
            parts = list(fixed)
            for i, v in zip(free, picks):
                parts[i] = v
            text = "".join(parts)
            last = [ln for ln in text.splitlines() if ln.strip()]
            sc = (bool(last) and _SLUG_END.search(last[-1]) is not None, _bigram(text))
            if best is None or sc > best[0]:
                best = (sc, text)
    return best[1] if best and best[0][0] else None


def decode_chunked(text):
    rows = []
    for ln in text.splitlines():
        m = _CHUNK.match(ln.rstrip("\r\n"))
        if m:
            rows.append((int(m.group(1)), m.group(2)))
        elif ln.strip():
            return None
    if len(rows) < 2:
        return None
    rows.sort(key=lambda r: r[0])
    return _joint_free(rows) or "".join(decode_chunk(p) for _, p in rows)
