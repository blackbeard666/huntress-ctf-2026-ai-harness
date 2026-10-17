"""Android/APK analysis helpers for the mobile lane.

Before this, each mobile solver was a copy-pasted *JSON reader*: it pulled assets/huntress_puzzle.json and
regex'd the answer, never touching the dex/manifest/resources — so it broke the instant the answer moved,
with zero obfuscation. This module is the robust fallback chain:

    extract_answer(apk):  puzzle-json decode  ->  raw scan of every zip entry  ->  dex strings  ->  nested zip/dex  ->
                          apktool (manifest/resources/smali)  ->  jadx (decompiled sources)

plus manifest_facts() for the exported-component / deep-link / allowBackup questions the lane actually asks.
Tools (apktool, jadx) are on PATH via bin/env.sh; each stage is best-effort with a timeout and degrades
gracefully if a tool is missing. Static only — we never install/run the APK.
"""
import base64
import binascii
import bz2
import codecs
import io
import json
import lzma
import re
import struct
import subprocess
import time
import xml.etree.ElementTree as ET
import zipfile
import zlib
from functools import lru_cache
from pathlib import Path

ANS_RE_T = re.compile(r"ANS-[0-9A-Fa-f]{16}")
ANS_RE_B = re.compile(rb"ANS-[0-9A-Fa-f]{16}")
_ANDROID_NS = "{http://schemas.android.com/apk/res/android}"


# --- codec decode (the primary puzzle-json path, kept identical to the per-day solvers) ----------
def _key_bytes(key):
    if key is None:
        return b"\x00"
    if isinstance(key, int):
        return bytes([key & 0xFF])
    if isinstance(key, (bytes, bytearray)):  # a derived key (identity_key_scan: digest bytes)
        return bytes(key) or b"\x00"
    s = str(key)
    if re.fullmatch(r"\d+", s):
        return bytes([int(s) & 0xFF])
    return s.encode("utf-8") or b"\x00"


def decode_payload(codec, data, key=None, accept=ANS_RE_T.search):
    """Decode a huntress_puzzle.json payload by its declared codec: plain/split, xor (base64 + repeating key), base64,
    base32, hex, rot13, reverse, caesar (every char's code point shifted by key). When the declared reading doesn't yield
    an answer (`accept`, default: an `ANS-<16 hex>` code) -- an unknown or renamed codec -- `decode_any()` searches the
    known primitives instead; if that finds nothing either, the declared reading (unknown codec: data unchanged) is
    returned as before."""
    out = _decode_declared(codec, data, key)
    if accept is None or (out and accept(out)):
        return out
    return decode_any(data, key, accept) or out


def _decode_declared(codec, data, key=None):
    codec = (codec or "plain").strip().lower()
    try:
        if codec in ("plain", "", "none", "raw", "identity", "split"):
            return data if isinstance(data, str) else str(data)
        if codec == "xor":
            raw = base64.b64decode(data)
            k = _key_bytes(key)
            return bytes(b ^ k[i % len(k)] for i, b in enumerate(raw)).decode("utf-8", "replace")
        if codec in ("base64", "b64"):
            return base64.b64decode(data).decode("utf-8", "replace")
        if codec in ("base32", "b32"):
            return base64.b32decode(data).decode("utf-8", "replace")
        if codec in ("hex", "base16"):
            return binascii.unhexlify(str(data).strip()).decode("utf-8", "replace")
        if codec in ("rot13", "rot-13"):
            return codecs.decode(data, "rot13")
        if codec in ("reverse", "reversed"):
            return data[::-1]
        if codec in ("caesar", "shift", "char_shift"):
            # Day 7 (webview-bridge): EVERY character's code point shifted by `key` (']'->'S', '7'->'-'), not just
            # letters -- lib.ciphers.caesar_all can't express it. Decode = subtract the key.
            k = int(key)
            return "".join(chr((ord(c) - k) % 0x110000) for c in str(data))
    except Exception:  # noqa: BLE001 - a wrong codec guess should just miss, not crash
        return ""
    return data


def _b64ish(b, alt=False):
    t = re.sub(rb"\s", b"", b)
    if not t or not re.fullmatch(rb"[A-Za-z0-9_\-]+={0,2}" if alt else rb"[A-Za-z0-9+/]+={0,2}", t):
        return None
    t += b"=" * (-len(t) % 4)
    return base64.urlsafe_b64decode(t) if alt else base64.b64decode(t)


def _readings(b):
    """Byte -> byte primitives a puzzle codec is built from (decode direction)."""
    yield b[::-1]
    for fn in (_b64ish, lambda x: _b64ish(x, True),
               lambda x: base64.b32decode(re.sub(rb"\s", b"", x)) if re.fullmatch(rb"[A-Z2-7]+=*", re.sub(rb"\s", b"", x) or b"-") else None,
               lambda x: binascii.unhexlify(re.sub(rb"[\s:,\-]", b"", x)) if re.fullmatch(rb"(?:[0-9a-fA-F]{2}[\s:,\-]*)+", x.strip() or b"-") else None,
               lambda x: bytes(int(t) for t in re.split(rb"[\s,;]+", x.strip())) if re.fullmatch(rb"\d+(?:[\s,;]+\d+)+", x.strip()) and all(int(t) < 256 for t in re.split(rb"[\s,;]+", x.strip())) else None,
               lambda x: base64.b85decode(x)):
        try:
            r = fn(b)
        except Exception:  # noqa: BLE001 - not this encoding
            r = None
        if r:
            yield r
    t = b.decode("latin-1")
    yield codecs.decode(t, "rot13").encode("latin-1")


def _keyed(b, key):
    """Keyed primitives (xor / add / sub mod 256 / code-point shift) for every reading of the key."""
    keys = []
    for k in (_key_bytes(key), str(key).encode() if key is not None and not isinstance(key, (bytes, bytearray)) else None):
        if k and k not in keys:
            keys.append(k)
    for k in keys:
        yield bytes(x ^ k[i % len(k)] for i, x in enumerate(b))
        if len(k) == 1:
            yield bytes((x - k[0]) % 256 for x in b)
            yield bytes((x + k[0]) % 256 for x in b)
    try:
        n = int(str(key), 0)
    except (TypeError, ValueError):
        return
    t = b.decode("utf-8", "replace")
    for d in (-n, n):
        try:
            yield "".join(chr((ord(c) + d) % 0x110000) for c in t).encode("utf-8")
        except (ValueError, UnicodeEncodeError):
            pass


_CHAIN_MAX_IN = 16384  # extended passes (2-3) only for puzzle-sized payloads, never a whole APK (day 10 fallback)
_UNZ_MAX = 1 << 20     # decompressed-output cap per step


def _atbash(t):
    return "".join(chr(219 - ord(c)) if "a" <= c <= "z" else chr(155 - ord(c)) if "A" <= c <= "Z" else c for c in t)


def _rot47(t):
    return "".join(chr(33 + (ord(c) - 33 + 47) % 94) if 33 <= ord(c) <= 126 else c for c in t)


def _vigenere(t, key, every=False):
    """Vigenere decrypt by the key's letters (case kept, non-letters pass); the key advances on letters only (CyberChef
    / textbook) or, `every`, on every character."""
    ks = [ord(c) - 65 for c in str(key).upper() if "A" <= c <= "Z"]
    if not ks:
        return None
    out, j = [], 0
    for c in t:
        if "a" <= c <= "z" or "A" <= c <= "Z":
            base = 97 if c >= "a" else 65
            out.append(chr((ord(c) - base - ks[j % len(ks)]) % 26 + base))
            j += 1
        else:
            out.append(c)
            j += every
    return "".join(out)


def _rail_fence(t, rails):
    """Decode a zig-zag rail-fence ciphertext written with `rails` rails."""
    n = len(t)
    if rails < 2 or rails >= n:
        return None
    cyc = 2 * rails - 2
    rows = [min(i % cyc, cyc - i % cyc) for i in range(n)]
    order = sorted(range(n), key=lambda i: rows[i])  # stable: positions per rail, left to right
    out = [""] * n
    for c, i in zip(t, order):
        out[i] = c
    return "".join(out)


def _unz(b):
    if b[:2] == b"\x1f\x8b":
        d = zlib.decompressobj(31)
    elif b[:1] == b"x":
        d = zlib.decompressobj()
    elif b[:3] == b"BZh":
        d = bz2.BZ2Decompressor()
    elif b[:5] == b"\xfd7zXZ":
        d = lzma.LZMADecompressor()
    else:
        return None
    return d.decompress(b, _UNZ_MAX)


def _readings2(b):
    """Pass-2 primitives (Row 36): atbash, rot47, rail-fence 2-6, binary/octal char codes, a85, zlib/gzip/bz2/xz."""
    t = b.decode("latin-1")
    yield _atbash(t).encode("latin-1")
    yield _rot47(t).encode("latin-1")
    if 3 <= len(t) <= 4096:
        for n in range(2, 7):
            r = _rail_fence(t, n)
            if r:
                yield r.encode("latin-1")
    s = re.sub(rb"\s", b"", b)
    for fn in (lambda: int(s, 2).to_bytes(len(s) // 8, "big") if re.fullmatch(rb"(?:[01]{8})+", s) else None,
               lambda: bytes(int(x, 8) for x in b.split()) if re.fullmatch(rb"[0-7]{3}(?:\s+[0-7]{3})+", b.strip()) else None,
               lambda: base64.a85decode(b.strip(), adobe=b.strip().startswith(b"<~")),
               lambda: _unz(b)):
        try:
            r = fn()
        except Exception:  # noqa: BLE001 - not this encoding
            r = None
        if r:
            yield r


def _keyed2(b, key):
    """Pass-2 keyed primitives: Vigenere by a string key, rail-fence by an integer key."""
    t = b.decode("latin-1")
    for every in (False, True):
        r = _vigenere(t, key, every)
        if r:
            yield r.encode("latin-1")
    try:
        n = int(str(key), 0)
    except (TypeError, ValueError):
        return
    if 6 < n < len(t):
        r = _rail_fence(t, n)
        if r:
            yield r.encode("latin-1")


def _bfs(start, key, accept, depth, cap, extended=False, end=None):
    seen, frontier = {start}, [start]
    for _ in range(depth):
        nxt = []
        for b in frontier:
            if end is not None and time.time() > end:
                return None
            for r in (*_readings(b), *(_keyed(b, key) if key is not None else ()),
                      *(_readings2(b) if extended else ()),
                      *(_keyed2(b, key) if extended and key is not None else ())):
                if not r or r in seen:
                    continue
                seen.add(r)
                t = r.decode("utf-8", "replace")
                if accept(t):
                    return t
                nxt.append(r)
                if len(seen) > cap:
                    return None
        frontier = nxt
    return None


def decode_any(data, key=None, accept=ANS_RE_T.search, depth=3, cap=4000, chain=True, chain_s=0.35):
    """Name-agnostic decode: breadth-first over the primitives puzzle codecs are composed of (reverse, base64/urlsafe/
    base32/hex/decimal/base85, rot13, xor/add/sub/code-point shift by `key`), up to `depth` steps, returning the first
    reading that satisfies `accept` (default: contains an ANS-<16 hex> code). The answer shape is the oracle, so a new
    or renamed codec name never matters (Day 7 `caesar` was such a name). None if nothing within the budget matches.
    When that finds nothing and `chain` (payloads <= 16 KB): a second pass adds atbash / rot47 / Vigenere (string key) /
    rail-fence / binary / octal / a85 / zlib-gzip-bz2-xz, then lib.decode.peel (rot-N, url, single-byte xor, longer
    chains) runs until `chain_s` seconds. Pass 1 is unchanged, so every answer it found before is still found first."""
    start = data.encode("utf-8", "replace") if isinstance(data, str) else bytes(data or b"")
    hit = _bfs(start, key, accept, depth, cap)
    if hit is not None or not chain or not start or len(start) > _CHAIN_MAX_IN:
        return hit
    end = time.time() + chain_s
    try:
        hit = _bfs(start, key, accept, depth, cap, extended=True, end=end)
        if hit is None and time.time() < end:
            from lib.decode import peel
            hit = peel(start, lambda t: bool(accept(t)), max_nodes=20000, deadline=end)[0]
    except Exception:  # noqa: BLE001 - a search miss, never a crash
        hit = None
    return hit


def _split_assemblies(parts, order):
    parts = [str(p) for p in parts]
    n = len(parts)
    outs = []
    if order and sorted(int(o) for o in order) == list(range(n)):
        o = [int(x) for x in order]
        slots = [None] * n
        for i, pos in enumerate(o):
            slots[pos] = parts[i]
        outs.append("".join(slots))
        outs.append("".join(parts[x] for x in o))
    outs.append("".join(parts))
    outs.append("".join(reversed(parts)))
    return outs


def puzzle_candidates(apk):
    """Decoded candidate strings from assets/*huntress_puzzle.json (the primary, fast path)."""
    out, names = [], []
    try:
        with zipfile.ZipFile(apk) as z:
            names = [n for n in z.namelist() if n.endswith("huntress_puzzle.json")]
            for n in names:
                try:
                    p = json.loads(z.read(n))
                except ValueError:
                    continue
                data, codec, key = p.get("data", p.get("payload", "")), p.get("codec"), p.get("key")
                if (codec or "").lower() == "split" or "parts" in p:
                    out += _split_assemblies(p.get("parts", []), p.get("order"))
                else:
                    out.append(decode_payload(codec, data, key))
    except (OSError, zipfile.BadZipFile):
        pass
    out = [c for c in out if c]
    if names and not any(ANS_RE_T.search(c) for c in out):  # undecodable payload: maybe AES/DES under a static key
        out += static_key_cipher_scan(apk)
        if not any(ANS_RE_T.search(c) for c in out):  # ... or keyed by the app's identity (package / case / secret)
            out += identity_key_scan(apk)
    return out


# --- fallback scans (dex / resources / decompiled code) ------------------------------------------
def raw_entry_scan(apk):
    """Every zip entry's bytes, scanned for a literal ANS token (plaintext-anywhere fallback). When no ASCII token
    exists anywhere, falls back to string_pool_scan() (UTF-16LE tokens + decoded AXML/resources.arsc pool strings), then
    hermes_string_scan() (decoded strings of a React Native Hermes bytecode bundle), then
    local_store_scan() (SQLite db cells / shared_prefs values / adb backup .ab members), then
    il2cpp_literal_scan() (decoded C# string literals of a Unity IL2CPP global-metadata.dat), then
    webview_asset_scan() (decoded JS literals / char-code arrays of assets/**/*.html|js|json)."""
    hits = []
    try:
        with zipfile.ZipFile(apk) as z:
            for n in z.namelist():
                try:
                    hits += [m.decode() for m in ANS_RE_B.findall(z.read(n))]
                except (OSError, RuntimeError):
                    continue
    except (OSError, zipfile.BadZipFile):
        pass
    if not hits:
        hits = string_pool_scan(apk)
    if not hits:
        hits = hermes_string_scan(apk)
    if not hits:
        hits = local_store_scan(apk)
    if not hits:
        hits = il2cpp_literal_scan(apk)
    if not hits:
        hits = webview_asset_scan(apk)
    return hits


# --- UTF-16 string pools: binary AXML manifest / layouts and resources.arsc (coverage atlas rows 22, 60, 61) ----------
ANS_RE_U16 = re.compile(rb"A\x00N\x00S\x00-\x00(?:[0-9A-Fa-f]\x00){16}")
_POOL_HDR = b"\x01\x00\x1c\x00"  # RES_STRING_POOL_TYPE, headerSize 0x1c
_POOL_MAX_ENTRY = 32 << 20
_POOL_MAX_STRINGS = 200_000
_POOL_DECODE_BUDGET = 400  # pool strings run through decode_any (each is bounded by its cap)
_POOL_ENCODED = re.compile(r"[\x21-\x7e]{16,4096}")


def _pool_len(b, i, utf8):
    """(length, next offset) of a ResStringPool length prefix (u8 pair with 0x80 flag / u16 pair with 0x8000 flag)."""
    if utf8:
        n = b[i]
        return ((n & 0x7F) << 8 | b[i + 1], i + 2) if n & 0x80 else (n, i + 1)
    n = int.from_bytes(b[i:i + 2], "little")
    if n & 0x8000:
        return (n & 0x7FFF) << 16 | int.from_bytes(b[i + 2:i + 4], "little"), i + 4
    return n, i + 2


def _pool_strings(b):
    """Every string of every ResStringPool chunk in an AXML / resources.arsc blob (UTF-8 and UTF-16 pools). Locates
    pool headers by signature, so it walks the manifest, compiled layouts, and all arsc packages alike; a malformed
    chunk is skipped, never raised."""
    out = []
    at = b.find(_POOL_HDR)
    while at >= 0 and len(out) < _POOL_MAX_STRINGS:
        try:
            size, count, _styles, flags, s_start = (int.from_bytes(b[at + o:at + o + 4], "little") for o in (4, 8, 12, 16, 20))
            end = at + size
            if 0x1c <= s_start <= size <= len(b) - at and count <= (size - 0x1c) // 4:
                utf8 = bool(flags & 0x100)
                base = at + s_start
                for k in range(min(count, _POOL_MAX_STRINGS - len(out))):
                    i = base + int.from_bytes(b[at + 0x1c + 4 * k:at + 0x20 + 4 * k], "little")
                    if i >= end:
                        continue
                    if utf8:
                        _, i = _pool_len(b, i, True)       # UTF-16 length, then the UTF-8 byte length
                        n, i = _pool_len(b, i, True)
                        out.append(b[i:min(i + n, end)].decode("utf-8", "replace"))
                    else:
                        n, i = _pool_len(b, i, False)
                        out.append(b[i:min(i + 2 * n, end)].decode("utf-16-le", "replace"))
        except (IndexError, ValueError):
            pass
        at = b.find(_POOL_HDR, at + 4)
    return out


def string_pool_scan(apk):
    """ANS tokens the ASCII scans miss: (1) a UTF-16LE `ANS-<16 hex>` in any zip entry (AXML manifest <meta-data
    android:value>, a UTF-16 arsc pool, a UTF-16 asset), then (2) the string pools of AndroidManifest.xml, res/*.xml
    and resources.arsc parsed and each pool string read directly and, when it looks encoded (printable, >= 16 chars),
    through decode_any (an encoded value in strings.xml). [] when absent; never raises."""
    hits = []
    try:
        with zipfile.ZipFile(apk) as z:
            pools = []
            for info in z.infolist():
                if info.is_dir() or info.file_size > _POOL_MAX_ENTRY:
                    continue
                try:
                    b = z.read(info)
                except (OSError, RuntimeError, zipfile.BadZipFile, EOFError, ValueError):
                    continue
                hits += [m.decode("utf-16-le") for m in ANS_RE_U16.findall(b)]
                n = info.filename
                if n == "AndroidManifest.xml" or n == "resources.arsc" or (n.startswith("res/") and n.endswith(".xml")):
                    if b[:2] in (b"\x03\x00", b"\x02\x00"):  # RES_XML_TYPE / RES_TABLE_TYPE
                        pools.append(b)
            if hits:
                return list(dict.fromkeys(hits))
            budget = _POOL_DECODE_BUDGET
            for b in pools:
                for s in _pool_strings(b):
                    m = ANS_RE_T.search(s)
                    if m:
                        hits.append(m.group(0))
                        continue
                    if budget > 0 and _POOL_ENCODED.fullmatch(s.strip()):
                        budget -= 1
                        d = decode_any(s.strip(), depth=2, cap=200, chain=False)
                        if d:
                            hits += ANS_RE_T.findall(d)
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        pass
    return list(dict.fromkeys(hits))


# --- React Native Hermes bytecode string table (coverage atlas row 54) ------------------------------------------------
_HBC_MAGIC = b"\xc6\x1f\xbc\x03\xc1\x03\x19\x1f"
_HBC_MAX_ENTRY = 32 << 20
_HBC_MAX_STRINGS = 500_000
_HBC_DECODE_BUDGET = 400
_HBC_HEX = re.compile(r"(?:[0-9a-fA-F]{2}){16,}")
_HBC_B32 = re.compile(r"[A-Z2-7]{16,}=*")
_HBC_B64 = re.compile(r"(?=.*\d|.*[+/=])(?=.*[a-z])(?=.*[A-Z])(?:[A-Za-z0-9+/]{4})+(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?")


def _hbc_rank(r):
    """Decode order for Hermes string runs: strict hex / base32 / base64 shapes, then url-safe alphabets, then the rest
    (a real bundle has tens of thousands of identifier-like strings ahead of one encoded payload)."""
    if _HBC_HEX.fullmatch(r) or _HBC_B32.fullmatch(r) or _HBC_B64.fullmatch(r):
        return 0
    return 1 if re.fullmatch(r"[A-Za-z0-9_=-]{20,}", r) and re.search(r"\d", r) else 2


def _a4(i):
    return (i + 3) & ~3


def hermes_strings(b):
    """Every string of a Hermes bytecode (.hbc / index.android.bundle) blob: header -> function headers -> string
    kinds -> identifier hashes -> small string table (u32 isUTF16:1 offset:23 length:8; length 255 = index into the
    overflow table of {offset u32, length u32}) -> string storage (Latin-1 or UTF-16LE). [] when not HBC / truncated."""
    try:
        if b[:8] != _HBC_MAGIC or len(b) < 128:
            return []
        version = struct.unpack_from("<I", b, 8)[0]
        if not 40 <= version <= 255:
            return []
        fn_count, kind_count, ident_count, count, ovf_count, storage_size = struct.unpack_from("<6I", b, 40)
        if count > _HBC_MAX_STRINGS or max(fn_count, kind_count, ident_count, ovf_count) > _HBC_MAX_STRINGS:
            return []
        i = 128 + fn_count * (12 if version >= 97 else 16)   # header is 97..113 bytes, padded to 32 in every version
        i = _a4(_a4(i) + 4 * kind_count)
        i = _a4(i + 4 * ident_count)
        small, i = i, _a4(i + 4 * count)
        ovf, i = i, _a4(i + 8 * ovf_count)
        if i + storage_size > len(b):
            return []
        storage = b[i:i + storage_size]
        out = []
        for k in range(count):
            e = struct.unpack_from("<I", b, small + 4 * k)[0]
            utf16, off, n = e & 1, (e >> 1) & 0x7FFFFF, e >> 24
            if n == 0xFF:
                if off >= ovf_count:
                    continue
                off, n = struct.unpack_from("<II", b, ovf + 8 * off)
            raw = storage[off:off + (2 * n if utf16 else n)]
            out.append(raw.decode("utf-16-le", "replace") if utf16 else raw.decode("latin-1"))
        return out
    except (struct.error, IndexError, ValueError):
        return []


def hermes_string_scan(apk, deadline_s=1.0):
    """ANS tokens from the string table of every Hermes bytecode zip entry (assets/index.android.bundle or a renamed
    one, found by HBC magic): a literal token in any string (incl. UTF-16 ones), then printable runs (>= 16 chars,
    base64/hex-looking first) through decode_any. [] when absent; never raises."""
    hits, runs = [], []
    try:
        with zipfile.ZipFile(apk) as z:
            for info in z.infolist():
                if info.is_dir() or info.file_size > _HBC_MAX_ENTRY or info.file_size < 128:
                    continue
                try:
                    with z.open(info) as f:
                        if f.read(8) != _HBC_MAGIC:
                            continue
                    b = z.read(info)
                except (OSError, RuntimeError, zipfile.BadZipFile, EOFError, ValueError):
                    continue
                for s in hermes_strings(b):
                    m = ANS_RE_T.findall(s)
                    if m:
                        hits += m
                    elif not hits:
                        runs += _POOL_ENCODED.findall(s)
        if hits:
            return list(dict.fromkeys(hits))
        runs = sorted(dict.fromkeys(runs), key=_hbc_rank)
        end = time.monotonic() + deadline_s
        for r in runs[:_HBC_DECODE_BUDGET]:
            if time.monotonic() > end:
                break
            d = decode_any(r, depth=2, cap=200, chain=False)
            if d:
                hits += ANS_RE_T.findall(d)
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        pass
    return list(dict.fromkeys(hits))


def dex_strings(apk):
    """ANS tokens from the UTF-8 string pool of every classes*.dex (handles multidex, renamed code). When no literal
    token exists, falls back to cert_pin_scan() (a token encoded as a `sha256/<b64>` pin / NSC <pin>), then
    split_native_assembly() (an `ANS-` prefix + hex fragments split across dex and .so), then
    dex_array_scan() (a <clinit> byte/char array xor'd with a class constant), then dex_gated_branch_scan() (an encoded
    const-string behind a Java root / emulator / signature check), then native_export_scan() (a token computed by a .so export: xor constants, then unicorn emulation)."""
    hits = []
    try:
        with zipfile.ZipFile(apk) as z:
            for n in z.namelist():
                if re.fullmatch(r"classes\d*\.dex", Path(n).name):
                    hits += [m.decode() for m in ANS_RE_B.findall(z.read(n))]
    except (OSError, zipfile.BadZipFile):
        pass
    if not hits:
        hits = cert_pin_scan(apk)
    if not hits:
        hits = split_native_assembly(apk)
    if not hits:
        hits = dex_array_scan(apk)
    if not hits:
        hits = dex_gated_branch_scan(apk)
    if not hits:
        hits = native_export_scan(apk)
    return hits


# --- answer split across dex const-strings and .so .rodata (coverage atlas row 38) ------------------------------------
_HEXFRAG = re.compile(r"[0-9A-Fa-f]{4,16}")
_ANCHOR = re.compile(r"ANS-[0-9A-Fa-f]{0,15}")
_SPLIT_MAX_DEX = 32 << 20
_SPLIT_MAX_UNITS = 1_500_000  # code units decoded across all methods (keeps a 20 MB dex well under 1 s)
# Dalvik instruction width in 16-bit code units, by opcode (unused opcodes = 1).
_DOP_W = bytearray([1] * 256)
for _lo, _hi, _w in ((0x02, 0x02, 2), (0x03, 0x03, 3), (0x05, 0x05, 2), (0x06, 0x06, 3), (0x08, 0x08, 2),
                     (0x09, 0x09, 3), (0x13, 0x13, 2), (0x14, 0x14, 3), (0x15, 0x16, 2), (0x17, 0x17, 3),
                     (0x18, 0x18, 5), (0x19, 0x1a, 2), (0x1b, 0x1b, 3), (0x1c, 0x1c, 2), (0x1f, 0x20, 2),
                     (0x22, 0x23, 2), (0x24, 0x26, 3), (0x29, 0x29, 2), (0x2a, 0x2c, 3), (0x2d, 0x3d, 2),
                     (0x44, 0x6d, 2), (0x6e, 0x72, 3), (0x74, 0x78, 3), (0x90, 0xaf, 2), (0xd0, 0xe2, 2),
                     (0xfa, 0xfb, 4), (0xfc, 0xfd, 3), (0xfe, 0xff, 2)):
    for _o in range(_lo, _hi + 1):
        _DOP_W[_o] = _w


def _uleb(b, i):
    r = s = 0
    while True:
        x = b[i]
        i += 1
        r |= (x & 0x7F) << s
        if x < 0x80:
            return r, i
        s += 7
        if s > 35:
            raise ValueError("uleb")


def _dex_class_strings(d, budget):
    """[(class_idx, [[str, ...] per method in code order] + [static-value strings])] for one dex; strings that are hex
    fragments or `ANS-` anchors only. Methods whose bytecode cannot reference such a string are skipped cheaply."""
    import struct
    if d[:4] != b"dex\n" or len(d) < 0x70:
        return []
    u32 = lambda o: struct.unpack_from("<I", d, o)[0]  # noqa: E731
    n_str, o_str, n_cls, o_cls = u32(0x38), u32(0x3C), u32(0x60), u32(0x64)
    if n_str > 1 << 22 or n_cls > 1 << 20 or o_str + 4 * n_str > len(d) or o_cls + 32 * n_cls > len(d):
        return []
    keep = {}
    for i in range(n_str):
        off = u32(o_str + 4 * i)
        _, j = _uleb(d, off)
        if d[j:j + 1] in (b"", b"\0") or not (0x30 <= d[j] <= 0x41 or 0x61 <= d[j] <= 0x66):
            continue  # first char can't start a hex fragment or "ANS-"
        e = d.find(b"\0", j, j + 20)
        if e < 0:
            continue
        t = d[j:e].decode("ascii", "replace")
        if _HEXFRAG.fullmatch(t) or _ANCHOR.fullmatch(t):
            keep[i] = t
    if not keep:
        return []
    out = []
    for c in range(n_cls):
        base = o_cls + 32 * c
        cdata, sval = u32(base + 24), u32(base + 28)
        meths = []
        if cdata and budget[0] > 0:
            i = cdata
            sf, i = _uleb(d, i)
            inf, i = _uleb(d, i)
            dm, i = _uleb(d, i)
            vm, i = _uleb(d, i)
            for _ in range(2 * (sf + inf)):
                _, i = _uleb(d, i)
            for _ in range(dm + vm):
                _, i = _uleb(d, i)
                _, i = _uleb(d, i)
                code, i = _uleb(d, i)
                if not code or code + 16 > len(d):
                    continue
                n_ins = u32(code + 12)
                ins = d[code + 16:code + 16 + 2 * n_ins]
                if b"\x1a" not in ins and b"\x1b" not in ins:
                    continue
                budget[0] -= n_ins
                if budget[0] < 0:
                    break
                got, pc = [], 0
                while pc < n_ins:
                    p = 2 * pc
                    op = ins[p]
                    if op == 0x1A or op == 0x1B:
                        si = struct.unpack_from("<H" if op == 0x1A else "<I", ins, p + 2)[0]
                        if si in keep:
                            got.append(keep[si])
                    elif op == 0 and ins[p + 1] in (1, 2, 3):  # switch / fill-array payloads
                        if ins[p + 1] == 1:
                            pc += 4 + 2 * struct.unpack_from("<H", ins, p + 2)[0]
                        elif ins[p + 1] == 2:
                            pc += 2 + 4 * struct.unpack_from("<H", ins, p + 2)[0]
                        else:
                            w, n = struct.unpack_from("<HI", ins, p + 2)
                            pc += 4 + (w * n + 1) // 2
                        continue
                    pc += _DOP_W[op]
                if got:
                    meths.append(got)
        if sval and sval < len(d):  # static final String constants (encoded_array of the class)
            try:
                n, i = _uleb(d, sval)
                vals = []
                for _ in range(min(n, 4096)):
                    t = d[i]
                    i += 1
                    vt, arg = t & 0x1F, t >> 5
                    if vt == 0x17:
                        vals.append(keep.get(int.from_bytes(d[i:i + arg + 1], "little")))
                    elif vt in (0x1C, 0x1D):
                        break  # nested array/annotation: stop rather than mis-parse
                    if vt not in (0x1E, 0x1F):
                        i += arg + 1
                vals = [v for v in vals if v]
                if vals:
                    meths.append(vals)
            except (IndexError, ValueError):
                pass
        if meths:
            out.append(meths)
    return out


def _so_rodata_seqs(b):
    """Hex fragments / anchors of one ELF .so: (.rodata strings by address, exported .rodata objects by symbol name)."""
    from elftools.elf.elffile import ELFFile
    elf = ELFFile(io.BytesIO(b))
    seqs = []
    for idx, sec in enumerate(elf.iter_sections()):
        if not (sec.name == ".rodata" or sec.name.startswith(".rodata.")) or sec["sh_type"] == "SHT_NOBITS":
            continue
        data, addr = sec.data(), sec["sh_addr"]
        seqs.append([t for t in (m.group(0).decode() for m in re.finditer(rb"[\x20-\x7e]{4,}", data))
                     if _HEXFRAG.fullmatch(t) or _ANCHOR.fullmatch(t)])
        syms = []
        for st in elf.iter_sections():
            if st["sh_type"] not in ("SHT_DYNSYM", "SHT_SYMTAB"):
                continue
            for s in st.iter_symbols():
                if s["st_info"]["type"] == "STT_OBJECT" and s["st_shndx"] == idx and s["st_size"]:
                    off = s["st_value"] - addr
                    t = data[off:off + min(s["st_size"], 32)].split(b"\0")[0].decode("latin-1")
                    if 0 <= off < len(data) and (_HEXFRAG.fullmatch(t) or _ANCHOR.fullmatch(t)):
                        syms.append((s.name, t))
        if syms:  # numbered siblings first (k_part1, k_part2 / secret_0, secret_1), then every export by name
            syms = sorted(dict(syms).items(), key=lambda kv: [int(x) if x.isdigit() else x
                                                              for x in re.split(r"(\d+)", kv[0])])
            stems = {}
            for name, t in syms:
                stems.setdefault(re.sub(r"\d+", "#", name), []).append(t)
            seqs[:0] = [v for k, v in stems.items() if "#" in k and len(v) > 1] + [[t for _, t in syms]]
    return seqs


def _windows(seq, need, maxlen=4):
    """Contiguous runs of hex fragments in `seq` whose total length is exactly `need` (need 0 -> the empty run)."""
    if need == 0:
        yield ""
        return
    for i in range(len(seq)):
        acc = ""
        for t in seq[i:i + maxlen]:
            if not _HEXFRAG.fullmatch(t):
                break
            acc += t
            if len(acc) >= need:
                if len(acc) == need:
                    yield acc
                break


def split_native_assembly(apk, cap=64):
    """Rebuild an answer split between the dex and native code: an `ANS-` prefix (alone or with some hex) plus 4-16 hex
    fragments from classes*.dex const-strings (code order per method, then the class's other methods / static values)
    and from lib/*/*.so .rodata (exported objects by symbol name, then strings by address). Candidates whose
    concatenation is `ANS-` + exactly 16 hex, most code-like order first: the anchor's own method alone, then that
    method + a native run, then the class's other dex fragments (+ native). Needs an anchor; [] when absent; never raises."""
    out = []
    try:
        dex_classes, so_seqs = [], []
        budget = [_SPLIT_MAX_UNITS]
        with zipfile.ZipFile(apk) as z:
            for info in z.infolist():
                if info.file_size > _SPLIT_MAX_DEX:
                    continue
                n = info.filename
                try:
                    if re.fullmatch(r"classes\d*\.dex", Path(n).name):
                        dex_classes += _dex_class_strings(z.read(info), budget)
                    elif n.startswith("lib/") and n.endswith(".so") and len(so_seqs) < 16:
                        so_seqs += _so_rodata_seqs(z.read(info))
                except Exception:  # noqa: BLE001 - a malformed dex / .so contributes nothing
                    continue
        native = [s for s in so_seqs if s]

        def add(c):
            if ANS_RE_T.fullmatch(c) and c not in out:
                out.append(c)

        for meths in dex_classes:
            flat = [t for m in meths for t in m]
            for m in meths:
                for a, t in enumerate(m):
                    if not _ANCHOR.fullmatch(t):
                        continue
                    tail = [x for x in m[a + 1:] if _HEXFRAG.fullmatch(x)]
                    heads = [t]
                    for x in tail[:4]:
                        heads.append(heads[-1] + x)
                    for h in heads:
                        if len(h) == 20:
                            add(h)
                    for h in heads:
                        for seq in native:
                            for w in _windows(seq, 20 - len(h)):
                                add(h + w)
                    for w in _windows([x for x in flat if x not in m], 20 - len(t)):
                        add(t + w)
                    for seq in native + [flat]:
                        for w1 in _windows([x for x in flat if x not in m], 20 - len(t) - 8):
                            for w2 in _windows(seq, 8):
                                add(t + w1 + w2)
                    if len(out) >= cap:
                        return out[:cap]
        if not out:  # anchor on the native side: native run after it, then dex fragments in code order
            dflat = [t for meths in dex_classes for m in meths for t in m if _HEXFRAG.fullmatch(t)]
            for seq in native:
                for a, t in enumerate(seq):
                    if _ANCHOR.fullmatch(t):
                        rest = seq[a + 1:]
                        for k in range(0, 5):
                            h = t + "".join(rest[:k])
                            if k and not _HEXFRAG.fullmatch(rest[k - 1] if k <= len(rest) else ""):
                                break
                            if len(h) > 20:
                                break
                            for s2 in (dflat, seq):
                                for w in _windows(s2, 20 - len(h)):
                                    add(h + w)
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        pass
    return out[:cap]


# --- string-encryption helper: xor'd byte/char arrays built in <clinit> (coverage atlas rows 35, 46) -----------------
_DXA_MAX_DEX, _DXA_UNITS, _DXA_BUDGET_S = 32 << 20, 1_000_000, 0.6
_DXA_MAX_ARRS, _DXA_MAX_KEYS, _DXA_MAX_LEN, _DXA_DEEP = 256, 48, 4096, 64
_DXA_OPS = frozenset((0x26, 0xD7, 0xDF))  # fill-array-data, xor-int/lit16, xor-int/lit8 (plain xor-int is in every hashCode)
_DXA_APUT = bytes(range(0x4B, 0x52))


def _dxa_hot(ins):
    """A method worth walking: fill-array-data / xor-literal ops, or new-array followed by a long aput run."""
    ops = ins[0::2]
    return not _DXA_OPS.isdisjoint(ops) or (0x23 in ops and sum(ops.count(x) for x in _DXA_APUT) >= 16)


def _s16(v):
    return v - 0x10000 if v & 0x8000 else v


def _dex_array_classes(d, budget, deadline):
    """[(arrays, int_keys, str_keys)] per class of one dex: element lists from fill-array-data payloads and from
    new-array + aput-with-constants runs, plus the class's int literals (const*, xor/add lits, static values) and
    short const-strings. Only methods whose code holds an array / xor opcode are walked."""
    if d[:4] != b"dex\n" or len(d) < 0x70:
        return []
    u32 = lambda o: struct.unpack_from("<I", d, o)[0]  # noqa: E731
    n_str, o_str, n_cls, o_cls = u32(0x38), u32(0x3C), u32(0x60), u32(0x64)
    if n_str > 1 << 22 or n_cls > 1 << 20 or o_str + 4 * n_str > len(d) or o_cls + 32 * n_cls > len(d):
        return []

    def sget(si):
        if si >= n_str:
            return None
        _, j = _uleb(d, u32(o_str + 4 * si))
        e = d.find(b"\0", j, j + 66)
        return d[j:e].decode("utf-8", "replace") if e > j else None

    out = []
    for c in range(n_cls):
        if budget[0] <= 0 or time.time() > deadline:
            break
        base = o_cls + 32 * c
        cdata, sval = u32(base + 24), u32(base + 28)
        arrs, ikeys, skeys = [], [], []
        if cdata:
            i = cdata
            sf, i = _uleb(d, i)
            inf, i = _uleb(d, i)
            dm, i = _uleb(d, i)
            vm, i = _uleb(d, i)
            for _ in range(2 * (sf + inf)):
                _, i = _uleb(d, i)
            codes = []
            for _ in range(dm + vm):
                _, i = _uleb(d, i)
                _, i = _uleb(d, i)
                code, i = _uleb(d, i)
                if code and code + 16 <= len(d):
                    n_ins = u32(code + 12)
                    codes.append((n_ins, d[code + 16:code + 16 + 2 * n_ins]))
            if not any(_dxa_hot(ins) for _, ins in codes):
                codes = []  # no array / xor op in the class: its constants can't be a decrypt key here
            for n_ins, ins in codes:
                budget[0] -= n_ins
                if budget[0] < 0:
                    break
                regs, built, pc = {}, {}, 0
                while pc < n_ins:
                    p = 2 * pc
                    op = ins[p]
                    if op == 0x12:  # const/4 vA, #+B
                        regs[ins[p + 1] & 0xF] = ((ins[p + 1] >> 4) ^ 8) - 8
                    elif op in (0x13, 0x15, 0x14):  # const/16, const/high16, const
                        v = struct.unpack_from("<H", ins, p + 2)[0]
                        v = _s16(v) if op == 0x13 else (v << 16 if op == 0x15 else struct.unpack_from("<i", ins, p + 2)[0])
                        regs[ins[p + 1]] = v
                        ikeys.append(v)
                    elif op in (0x1A, 0x1B):
                        s = sget(struct.unpack_from("<H" if op == 0x1A else "<I", ins, p + 2)[0])
                        if s and len(s) <= 64:
                            skeys.append(s)
                    elif op == 0x23:  # new-array vA, vB, type
                        a = ins[p + 1] & 0xF
                        if built.get(a):
                            arrs.append(built[a])
                        built[a] = {}
                        regs.pop(a, None)
                    elif 0x4B <= op <= 0x51:  # aput* vAA(value), vBB(array), vCC(index)
                        va, arr, ix = ins[p + 1], ins[p + 2], ins[p + 3]
                        if arr in built and va in regs and ix in regs and 0 <= regs[ix] < _DXA_MAX_LEN:
                            built[arr][regs[ix]] = regs[va]
                    elif op == 0x26:  # fill-array-data vAA, +BBBBBBBB -> payload (ident 0x0300, width, size, data)
                        q = 2 * (pc + struct.unpack_from("<i", ins, p + 2)[0])
                        if 0 <= q and q + 8 <= len(ins) and ins[q:q + 2] == b"\x00\x03":
                            w, n = struct.unpack_from("<HI", ins, q + 2)
                            if w in (1, 2, 4, 8) and 0 < n <= _DXA_MAX_LEN and q + 8 + w * n <= len(ins):
                                raw = ins[q + 8:q + 8 + w * n]
                                arrs.append(list(raw) if w == 1 else
                                            [int.from_bytes(raw[k:k + w], "little") for k in range(0, w * n, w)])
                    elif 0xD0 <= op <= 0xD7:  # binop/lit16
                        ikeys.append(_s16(struct.unpack_from("<H", ins, p + 2)[0]))
                    elif 0xD8 <= op <= 0xE2:  # binop/lit8
                        ikeys.append((ins[p + 3] ^ 0x80) - 0x80)
                    elif op == 0 and ins[p + 1] in (1, 2, 3):  # switch / fill-array payloads
                        if ins[p + 1] == 1:
                            pc += 4 + 2 * struct.unpack_from("<H", ins, p + 2)[0]
                        elif ins[p + 1] == 2:
                            pc += 2 + 4 * struct.unpack_from("<H", ins, p + 2)[0]
                        else:
                            w, n = struct.unpack_from("<HI", ins, p + 2)
                            pc += 4 + (w * n + 1) // 2
                        continue
                    elif op not in (0x01, 0x02, 0x03, 0x07, 0x08, 0x09, 0x0D):  # other writes clobber vAA / vA
                        regs.pop(ins[p + 1], None)
                        regs.pop(ins[p + 1] & 0xF, None)
                    pc += _DOP_W[op]
                for b in built.values():
                    if b and sorted(b) == list(range(len(b))):
                        arrs.append([b[k] for k in range(len(b))])
        if sval and sval < len(d) and (arrs or ikeys):  # static final int/char/byte/String constants
            try:
                n, i = _uleb(d, sval)
                for _ in range(min(n, 4096)):
                    t = d[i]
                    i += 1
                    vt, arg = t & 0x1F, t >> 5
                    if vt in (0x00, 0x02, 0x03, 0x04):
                        ikeys.append(int.from_bytes(d[i:i + arg + 1], "little", signed=vt != 0x03))
                    elif vt == 0x17:
                        s = sget(int.from_bytes(d[i:i + arg + 1], "little"))
                        if s and len(s) <= 64:
                            skeys.append(s)
                    elif vt in (0x1C, 0x1D):
                        break
                    if vt not in (0x1E, 0x1F):
                        i += arg + 1
            except (IndexError, ValueError):
                pass
        if arrs or ikeys:
            out.append((arrs, ikeys, skeys))
    return out


def _dxa_try(vals, key):
    """ANS token from element list `vals` under one key (int, str or element list): xor (repeating), xor/add/sub with
    the key + index, then -- for byte-sized data -- decode_any's codec chains (base64-of-xor and friends)."""
    kl = [key] if isinstance(key, int) else ([ord(ch) for ch in key] if isinstance(key, str) else list(key))
    if not kl:
        return None
    n = len(kl)
    outs = [[v ^ kl[i % n] for i, v in enumerate(vals)]]
    if n == 1:
        k = kl[0]
        outs += [[v - k for v in vals], [v + k for v in vals], [v ^ ((k + i) & 0xFF) for i, v in enumerate(vals)],
                 [v ^ (k ^ i) & 0xFF for i, v in enumerate(vals)]]
    else:
        outs += [[v - kl[i % n] for i, v in enumerate(vals)]]
    for o in outs:
        if all(0 <= x < 0x110000 for x in o):
            m = ANS_RE_T.search("".join(map(chr, o)))
        else:
            m = ANS_RE_T.search(bytes(x & 0xFF for x in o).decode("latin-1"))
        if m:
            return m.group(0)
    return None


def dex_array_scan(apk):
    """ANS tokens hidden by a string-encryption helper: a byte/char/int array built in <clinit> (fill-array-data payload
    or new-array + aput constants) decoded with a constant key from the same class (const / xor-int/lit literal, static
    final value, const-string, or a short sibling array), else from any class. Tries the array as-is, xor / add / sub
    (plain, repeating, key+index), and decode_any for codec layers. Static only (no code runs); [] when absent; never
    raises; bounded to ~0.6 s."""
    hits = []
    deadline = time.time() + _DXA_BUDGET_S
    try:
        classes, budget = [], [_DXA_UNITS]
        with zipfile.ZipFile(apk) as z:
            for info in z.infolist():
                if info.file_size <= _DXA_MAX_DEX and re.fullmatch(r"classes\d*\.dex", Path(info.filename).name):
                    try:
                        classes += _dex_array_classes(z.read(info), budget, deadline)
                    except Exception:  # noqa: BLE001 - a malformed dex contributes nothing
                        continue
        glob_i, glob_s = [], []
        for _, ik, sk in classes:
            glob_i += ik
            glob_s += sk
        deep = [_DXA_DEEP]
        for arrs, ik, sk in classes:
            data = [a for a in arrs if len(a) >= 20][:_DXA_MAX_ARRS]
            if not data:
                continue
            short = [a for a in arrs if 0 < len(a) <= 32]
            keys = list(dict.fromkeys([0] + [k for k in ik if -0x10000 < k < 0x10000] + sk))
            keys += [a for a in short] + [k for k in dict.fromkeys(glob_i + glob_s)
                                          if k not in keys and (not isinstance(k, int) or -0x10000 < k < 0x10000)]
            keys = keys[:_DXA_MAX_KEYS + len(short)]
            for vals in data:
                for key in keys:
                    if time.time() > deadline:
                        return list(dict.fromkeys(hits))
                    t = _dxa_try(vals, key)
                    if t:
                        hits.append(t)
                        break
                else:
                    if all(0 <= v < 256 for v in vals):
                        raw = bytes(vals)
                        for key in [k for k in keys if not isinstance(k, list)][:8]:
                            if deep[0] <= 0 or time.time() > deadline:
                                break
                            deep[0] -= 1
                            t = decode_any(raw, key if key else None, depth=2, cap=400, chain=False)
                            m = t and ANS_RE_T.search(t)
                            if m:
                                hits.append(m.group(0))
                                break
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        pass
    return list(dict.fromkeys(hits))


# --- root / emulator / debugger / signature check in Java gating a constant (coverage atlas rows 47-49) ---------------
_DGB_MARK = re.compile(r"(?i)(?:^|/)su$|magisk|supersu|superuser|test-keys|rootbeer|busybox|goldfish|ranchu|ro\.kernel\.qemu"
                       r"|qemu_pipe|genymotion|sdk_gphone|frida|27042|xposed|tracerpid|/proc/self/(?:maps|status)"
                       r"|^(?:isDebuggerConnected|getPackageInfo|getInstallerPackageName|getInstallingPackageName"
                       r"|getApkContentsSigners|hasSigningCertificateHistory|signatures|signingInfo|TAGS|HARDWARE)$")
_DGB_PRE = re.compile(rb"(?i)magisk|test-keys|goldfish|ranchu|qemu|frida|xposed|tracerpid|/su\0|rootbeer|busybox"
                      rb"|isDebuggerConnected|getPackageInfo|getInstall\w*PackageName|signingInfo|getApkContentsSigners")
_DGB_PAYLOAD = re.compile(r"[\x21-\x7e]{12,4096}")
_DGB_MAX_DEX, _DGB_UNITS, _DGB_BUDGET_S, _DGB_PAYLOADS, _DGB_KEYS = 32 << 20, 1_000_000, 0.7, 48, 24


def _dgb_methods(d, budget, deadline):
    """Per-method facts of one dex whose pool holds an anti-root / anti-emulator / signature marker:
    {method_idx: (marked, [string idx], [int literal], {invoked method idx})}, plus the string reader. ({}, None) else."""
    if d[:4] != b"dex\n" or len(d) < 0x70 or not _DGB_PRE.search(d):
        return {}, None
    u32 = lambda o: struct.unpack_from("<I", d, o)[0]  # noqa: E731
    n_str, o_str, n_fld, o_fld, n_mth, o_mth, n_cls, o_cls = (u32(o) for o in (0x38, 0x3C, 0x50, 0x54, 0x58, 0x5C, 0x60, 0x64))
    if (n_str > 1 << 22 or n_cls > 1 << 20 or o_str + 4 * n_str > len(d) or o_cls + 32 * n_cls > len(d)
            or o_fld + 8 * n_fld > len(d) or o_mth + 8 * n_mth > len(d)):
        return {}, None

    @lru_cache(maxsize=None)
    def sget(si):
        if si >= n_str:
            return None
        _, j = _uleb(d, u32(o_str + 4 * si))
        e = d.find(b"\0", j, j + 4100)
        return d[j:e].decode("utf-8", "replace") if e >= j else None

    mark_s = {i for i in range(n_str) if _DGB_PRE.search(d, u32(o_str + 4 * i) + 1, u32(o_str + 4 * i) + 80)
              or (d[u32(o_str + 4 * i) + 1:u32(o_str + 4 * i) + 5] in (b"su\0", b"TAGS", b"HARD", b"sign"))}
    mark_s = {i for i in mark_s if _DGB_MARK.search(sget(i) or "")}
    mark_m = {i for i in range(n_mth) if u32(o_mth + 8 * i + 4) in mark_s}
    mark_f = {i for i in range(n_fld) if u32(o_fld + 8 * i + 4) in mark_s}
    out = {}
    for c in range(n_cls):
        cdata = u32(o_cls + 32 * c + 24)
        if not cdata:
            continue
        i = cdata
        sf, i = _uleb(d, i)
        inf, i = _uleb(d, i)
        dm, i = _uleb(d, i)
        vm, i = _uleb(d, i)
        for _ in range(2 * (sf + inf)):
            _, i = _uleb(d, i)
        for cnt in (dm, vm):
            midx = 0
            for _ in range(cnt):
                dlt, i = _uleb(d, i)
                midx += dlt
                _, i = _uleb(d, i)
                code, i = _uleb(d, i)
                if not code or code + 16 > len(d):
                    continue
                n_ins = u32(code + 12)
                budget[0] -= n_ins
                if budget[0] < 0 or time.time() > deadline:
                    return out, sget
                ins = d[code + 16:code + 16 + 2 * n_ins]
                marked, strs, ints, calls, pc = False, [], [], set(), 0
                while pc < n_ins and 2 * pc + 1 < len(ins):
                    p = 2 * pc
                    op = ins[p]
                    if op in (0x1A, 0x1B):
                        si = struct.unpack_from("<H" if op == 0x1A else "<I", ins, p + 2)[0]
                        strs.append(si)
                        marked |= si in mark_s
                    elif op == 0x12:
                        ints.append(((ins[p + 1] >> 4) ^ 8) - 8)
                    elif op in (0x13, 0x14) or 0xD0 <= op <= 0xD7:
                        ints.append(struct.unpack_from("<i", ins, p + 2)[0] if op == 0x14 else _s16(struct.unpack_from("<H", ins, p + 2)[0]))
                    elif 0xD8 <= op <= 0xE2:
                        ints.append((ins[p + 3] ^ 0x80) - 0x80)
                    elif 0x6E <= op <= 0x72 or 0x74 <= op <= 0x78:
                        mi = struct.unpack_from("<H", ins, p + 2)[0]
                        calls.add(mi)
                        marked |= mi in mark_m
                    elif 0x52 <= op <= 0x6D:  # iget*/iput*/sget*/sput* field@CCCC
                        marked |= struct.unpack_from("<H", ins, p + 2)[0] in mark_f
                    elif op == 0 and ins[p + 1] in (1, 2, 3):  # switch / fill-array payloads
                        if ins[p + 1] == 1:
                            pc += 4 + 2 * struct.unpack_from("<H", ins, p + 2)[0]
                        elif ins[p + 1] == 2:
                            pc += 2 + 4 * struct.unpack_from("<H", ins, p + 2)[0]
                        else:
                            w, n = struct.unpack_from("<HI", ins, p + 2)
                            pc += 4 + (w * n + 1) // 2
                        continue
                    pc += _DOP_W[op]
                out[midx] = (marked, strs, ints, calls)
    return out, sget


def dex_gated_branch_scan(apk):
    """ANS tokens behind a Java root / emulator / debugger / signature gate: methods that reference a check marker (su /
    magisk / test-keys / goldfish / ranchu / frida / TracerPid / /proc/self/maps / isDebuggerConnected / getPackageInfo
    signatures / installer ...), their callers (the method holding `if (isRooted()) ... else <secret>`) and those
    callers' callees (the decode helper). Their encoded const-strings are run through decode_any keyless, then with
    the small int literals and short strings of the same method set as keys (xor / add / sub, base64-of-xor ...).
    Static only; both branches are read and the ANS shape is the oracle. [] when absent; never raises; ~0.7 s bound."""
    hits = []
    deadline = time.time() + _DGB_BUDGET_S
    try:
        with zipfile.ZipFile(apk) as z:
            dexes = [i for i in z.infolist()
                     if i.file_size <= _DGB_MAX_DEX and re.fullmatch(r"classes\d*\.dex", Path(i.filename).name)]
            budget = [_DGB_UNITS]
            for info in dexes:
                meths, sget = _dgb_methods(z.read(info), budget, deadline)
                gated = {m for m, f in meths.items() if f[0]}
                if not gated:
                    continue
                callers = {m for m, f in meths.items() if f[3] & gated} - gated
                helpers = {c for m in callers for c in meths[m][3] if c in meths} - gated - callers
                payloads, keys = [], []
                for group in (callers, gated, helpers):
                    for m in sorted(group):
                        _, strs, ints, _ = meths[m]
                        for si in strs:
                            s = sget(si)
                            if not s:
                                continue
                            m_ans = ANS_RE_T.search(s)
                            if m_ans:
                                hits.append(m_ans.group(0))
                            elif _DGB_PAYLOAD.fullmatch(s) and not _DGB_MARK.search(s) and s not in payloads:
                                payloads.append(s)
                            elif 0 < len(s) <= 32 and s not in keys:
                                keys.append(s)
                        keys += [k for k in ints if 1 < abs(k) < 0x10000 and k not in keys and k not in (16, 0xFF)]
                payloads.sort(key=lambda s: -len(s))
                ikeys = [k for k in keys if isinstance(k, int)][:_DGB_KEYS]
                skeys = [k for k in keys if isinstance(k, str)][:_DGB_KEYS // 2]
                for s in payloads[:_DGB_PAYLOADS]:
                    for key in (None, *ikeys, *skeys):
                        if time.time() > deadline:
                            return list(dict.fromkeys(hits))
                        t = decode_any(s, key, depth=3 if key is None else 2, cap=600, chain=False)
                        m_ans = t and ANS_RE_T.search(t)
                        if m_ans:
                            hits.append(m_ans.group(0))
                            break
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        pass
    return list(dict.fromkeys(hits))


# --- JNI secret computed inside a .so export, not a literal (coverage atlas rows 37, 39, 40) --------------------------
_NSO_MAX_SO, _NSO_MAX_BYTES, _NSO_MAX_FUNCS, _NSO_FUNC_CAP = 8, 32 << 20, 48, 16384
_NSO_BUDGET_S, _NSO_DECODE_S, _NSO_FN_US, _NSO_FN_INSNS = 1.2, 0.3, 150_000, 2_000_000
_NSO_DATA = re.compile(r"\.(rodata|data)(\.|$)|\.data\.rel\.ro")
_NSO_JNI = {6: "FindClass", 167: "NewStringUTF", 169: "GetStringUTFChars", 215: "RegisterNatives"}
_NSO_ALLOC = {"malloc", "_Znwm", "_Znam", "_Znwj", "_Znaj", "calloc", "realloc", "strdup"}
# e_machine -> (unicorn arch/mode names, capstone arch/mode names, arg regs, return reg, ret insn, reloc types)
_NSO_ARCH = {
    "EM_X86_64": (("UC_ARCH_X86", "UC_MODE_64"), ("CS_ARCH_X86", "CS_MODE_64"),
                  ("RDI", "RSI", "RDX", "RCX", "R8", "R9"), "RAX", b"\xc3", {8: "rel", 6: "sym", 7: "sym", 1: "sym"}),
    "EM_AARCH64": (("UC_ARCH_ARM64", "UC_MODE_ARM"), ("CS_ARCH_ARM64", "CS_MODE_ARM"),
                   ("X0", "X1", "X2", "X3", "X4", "X5"), "X0", b"\xc0\x03\x5f\xd6",
                   {1027: "rel", 1025: "sym", 1026: "sym", 257: "sym"}),
    # 32-bit ABIs (row 40: armeabi-v7a Thumb / x86): REL relocations (addend in place); x86 passes args on the stack
    "EM_ARM": (("UC_ARCH_ARM", "UC_MODE_ARM"), ("CS_ARCH_ARM", "CS_MODE_ARM"),
               ("R0", "R1", "R2", "R3"), "R0", b"\x1e\xff\x2f\xe1", {23: "rel", 21: "sym", 22: "sym", 2: "abs"}),
    "EM_386": (("UC_ARCH_X86", "UC_MODE_32"), ("CS_ARCH_X86", "CS_MODE_32"),
               (), "EAX", b"\xc3", {8: "rel", 6: "sym", 7: "sym", 1: "abs"}),
}


class _NsoElf:
    """Struct-level ELF view: header + PT_LOAD via pyelftools, section headers / symbols / RELA / RELR unpacked with
    struct (pyelftools' per-symbol parsing costs ~1 s on a libc-sized .so)."""

    def __init__(self, b):
        from elftools.elf.elffile import ELFFile
        elf = ELFFile(io.BytesIO(b))
        h, self.b, self.arch = elf.header, b, elf["e_machine"]
        self.e, self.is64 = "<" if elf.little_endian else ">", elf.elfclass == 64
        self.segs = [(s["p_vaddr"], s["p_offset"], s["p_filesz"], s["p_memsz"]) for s in elf.iter_segments()
                     if s["p_type"] == "PT_LOAD"]
        shf = self.e + ("IIQQQQIIQQ" if self.is64 else "IIIIIIIIII")
        self.secs = []  # [name, type, addr, offset, size, link]
        for i in range(min(h["e_shnum"], 512)):
            name, typ, _, addr, off, size, link = struct.unpack_from(shf, b, h["e_shoff"] + i * h["e_shentsize"])[:7]
            self.secs.append([name, typ, addr, off, size, link])
        if h["e_shstrndx"] < len(self.secs):
            stro = self.secs[h["e_shstrndx"]][3]
            for sec in self.secs:
                sec[0] = self.cstr(stro + sec[0]).decode("latin-1")
        self.syms = {}  # symtab section index -> [(name, value, size, type, shndx)]
        for i, (_, typ, _, off, size, link) in enumerate(self.secs):
            if typ not in (2, 11) or link >= len(self.secs):  # SHT_SYMTAB, SHT_DYNSYM
                continue
            stro, out = self.secs[link][3], []
            for t in struct.iter_unpack(self.e + ("IBBHQQ" if self.is64 else "IIIBBH"),
                                        b[off:off + min(size, 60000 * (24 if self.is64 else 16))]):
                nm, val, sz, info, shndx = (t[0], t[4], t[5], t[1], t[3]) if self.is64 else (t[0], t[1], t[2], t[3], t[5])
                out.append((self.cstr(stro + nm).decode("latin-1") if nm else "", val, sz, info & 0xF, shndx))
            self.syms[i] = out

    def cstr(self, off, n=256):
        return self.b[off:off + n].split(b"\0")[0]

    def at(self, va, n):
        """File bytes at virtual address `va`, capped to its segment; b"" when not file-backed."""
        for v, o, fs, _ in self.segs:
            if v <= va < v + fs:
                return self.b[o + va - v:o + min(va - v + n, fs)]
        return b""

    def sections(self, data_only=False):
        for name, typ, addr, off, size, _ in self.secs:
            if typ != 8 and (not data_only or _NSO_DATA.match(name)):  # SHT_NOBITS has no bytes
                yield name, addr, self.b[off:off + size]


def _nso_exports(elf):
    """Defined FUNC symbols (dynsym, then symtab when not stripped): JNI_OnLoad, Java_*, huntress_*, then the rest."""
    seen = {}
    for i in sorted(elf.syms, key=lambda i: elf.secs[i][1] != 11):
        for name, val, size, typ, shndx in elf.syms[i]:
            if typ == 2 and shndx and name and val:  # STT_FUNC, defined
                seen.setdefault(name, (val, size, elf.secs[i][1] == 11))
    rank = lambda n: (0 if n == "JNI_OnLoad" else 1 if n.startswith("Java_") else 2 if "huntress" in n.lower()
                      else 3 if seen[n][2] else 4)
    return [(n, *seen[n][:2]) for n in sorted(seen, key=lambda n: (rank(n), seen[n][0]))
            if not n.startswith(("_init", "_fini", "__", "frame_dummy", "register_tm", "deregister_tm"))]


def _nso_xor_keys(elf, arch, funcs, deadline):
    """Byte constants feeding the exports' xor/eor (x86 `xor r, imm`; ARM `eor r, r, #imm` or `mov r, #imm` < 256),
    plus multi-byte xor immediates as repeating keys."""
    import capstone
    keys = []
    a, m = _NSO_ARCH[arch][1]
    for name, va, size in funcs[:_NSO_MAX_FUNCS]:
        if time.time() > deadline:
            break
        thumb = arch == "EM_ARM" and va & 1  # the Thumb bit is ARM-only; an x86 function may start at an odd address
        md = capstone.Cs(getattr(capstone, a), getattr(capstone, m) | (capstone.CS_MODE_THUMB if thumb else 0))
        va -= 1 if thumb else 0
        for ins in md.disasm(elf.at(va, min(size or 512, _NSO_FUNC_CAP)), va):
            mn, ops = ins.mnemonic, ins.op_str
            mi = re.search(r"#?(-?0x[0-9a-f]+|-?\d+)\s*$", ops)
            if not mi or not (mn.startswith(("xor", "eor")) or (arch in ("EM_ARM", "EM_AARCH64") and mn.startswith("mov"))):
                continue
            v = int(mi.group(1), 0)
            if mn.startswith("mov") and not 0 < v < 256:
                continue
            v &= 0xFFFFFFFF
            k = bytes([v]) if v < 256 else v.to_bytes(4, "little").rstrip(b"\0")
            if k and k != b"\0" and k not in keys:
                keys.append(k)
    return keys[:32]


def _nso_static(elf, keys, deadline):
    """xor each data section (whole, for a single-byte key) and each data blob (symbol object / NUL-delimited run,
    any key; plus decode_any over the object blobs) with the export's key constants."""
    hits, blobs = [], []
    for _, _, d in elf.sections(data_only=True):
        for k in keys:
            if len(k) == 1:
                hits += ANS_RE_B.findall(d.translate(bytes(x ^ k[0] for x in range(256))))
        blobs += [m.group(0) for m in re.finditer(rb"[^\0]{8,512}", d)][:400]
    for syms in elf.syms.values():
        for _, val, size, typ, shndx in syms:
            if typ == 1 and shndx and 8 <= size <= 512 and val:  # STT_OBJECT
                b = elf.at(val, size)
                if b and b not in blobs:
                    blobs.insert(0, b)
    multi = [k for k in keys if len(k) > 1]
    for b in blobs[:2000] if multi else ():
        for k in multi:
            hits += ANS_RE_B.findall(bytes(x ^ k[j % len(k)] for j, x in enumerate(b)))
    end = min(deadline, time.time() + _NSO_DECODE_S)  # decode_any (b64/hex/rot/add/sub/...) on the first blobs only
    for b in blobs[:16]:
        for k in keys[:8]:
            if not hits and time.time() < end:
                r = decode_any(b, key=k[0] if len(k) == 1 else k.decode("latin-1"), depth=2, cap=200, chain=False)
                hits += [h.encode() for h in ANS_RE_T.findall(r or "")]
    return [h.decode() for h in hits]


_NSO_REG_WORDS = 1 << 18
_NSO_REG_NAME = re.compile(rb"[A-Za-z_$][\w$]{0,127}")
_NSO_REG_SIG = re.compile(rb"\((?:\[*(?:[ZBCSIJFD]|L[^;()]+;))*\)\[*(?:[ZBCSIJFDV]|L[^;()]+;)")


def _nso_registered(elf, dex=b""):
    """RegisterNatives tables without running JNI_OnLoad (row 39): every pointer-aligned {char* name, char* sig,
    void* fn} triple in .data.rel.ro / .data (pointers from R_*_RELATIVE RELA / RELR relocations, else the in-place
    word) whose name is a Java identifier, sig a JNI method descriptor and fn inside .text. Names that are also dex
    strings (the `native` method's name) rank first. [(name, fn va)]; [] when none (x86_64 / arm64 LE only)."""
    if not elf.is64 or elf.e != "<" or elf.arch not in ("EM_X86_64", "EM_AARCH64"):
        return []
    rel_t = 8 if elf.arch == "EM_X86_64" else 1027
    ptr = {}
    for _, typ, _, off, ssz, _ in elf.secs:
        if typ == 4:  # SHT_RELA: R_*_RELATIVE -> addend
            for r_off, info, add in struct.iter_unpack("<QQq", elf.b[off:off + min(ssz, 24 * _NSO_REG_WORDS) // 24 * 24]):
                if info & 0xFFFFFFFF == rel_t:
                    ptr[r_off] = add
        elif typ == 19:  # SHT_RELR: the in-place word is the target
            where = 0
            for (e,) in struct.iter_unpack("<Q", elf.b[off:off + (min(ssz, 8 * _NSO_REG_WORDS) & ~7)]):
                for o in ([e] if not e & 1 else [where + 8 * j for j in range(63) if e >> (j + 1) & 1]):
                    ptr.setdefault(o, int.from_bytes(elf.at(o, 8).ljust(8, b"\0"), "little"))
                where = e + 8 if not e & 1 else where + 63 * 8
    text = [(addr, addr + len(d)) for name, addr, d in elf.sections() if name == ".text"]
    out, words = [], 0
    for name, addr, d in elf.sections():
        if name not in (".data.rel.ro", ".data", ".data.rel.ro.local", ".data.rel"):
            continue
        for i in range((-addr) % 8, len(d) - 23, 8):
            words += 1
            if words > _NSO_REG_WORDS:
                break
            va = addr + i
            p = [ptr.get(va + 8 * k) or int.from_bytes(d[i + 8 * k:i + 8 * k + 8], "little") for k in range(3)]
            if not all(p) or not any(lo <= p[2] < hi for lo, hi in text):
                continue
            nm, sig = elf.at(p[0], 130).split(b"\0")[0], elf.at(p[1], 512).split(b"\0")[0]
            if _NSO_REG_NAME.fullmatch(nm) and _NSO_REG_SIG.fullmatch(sig):
                out.append((nm.decode(), p[2]))
    rank = {n: bool(dex) and bytes([len(n)]) + n.encode() + b"\0" in dex for n, _ in out}
    return sorted(dict.fromkeys(out), key=lambda t: not rank[t[0]])


_NSO_REF_FUNCS, _NSO_REF_TARGETS, _NSO_REF_S = 24, 96, 0.35
_NSO_RIP = re.compile(r"\[rip ([+-]) (0x[0-9a-f]+|\d+)\]")
_NSO_IMM = re.compile(r"#?(0x[0-9a-f]+|\d+)$")


def _nso_refs(elf, arch, funcs, deadline, extra=()):
    """What a Java_* / huntress_* export can return (rows 37, 65 -- D16's gated nativeEvidence returned &arena_value
    only for len 65536, so emulating it with len 0 misses): disassemble each export (and the local functions it calls,
    one level) for its rip-relative lea/mov targets (x86_64) and adrp+add / adrp+ldr pairs (arm64), read the C string
    / sized object at each target in a data section, and match it raw, xor'd with the function's own immediates, and
    through decode_any. Tokens in export order; [] when none."""
    import capstone
    if arch not in ("EM_X86_64", "EM_AARCH64"):
        return []
    a, m = _NSO_ARCH[arch][1]
    md = capstone.Cs(getattr(capstone, a), getattr(capstone, m))
    text = [(addr, addr + len(d)) for name, addr, d in elf.sections() if name == ".text"]
    datas = [(addr, addr + len(d)) for name, addr, d in elf.sections(data_only=True)]
    objs = {val: size for syms in elf.syms.values() for _, val, size, typ, shndx in syms
            if typ == 1 and shndx and 0 < size <= 4096}
    sizes = {va: size for _, va, size in funcs}
    end = min(deadline, time.time() + _NSO_REF_S)
    queue = [va for n, va, _ in funcs if n.startswith("Java_") or "huntress" in n.lower()][:_NSO_REF_FUNCS]
    starts = sorted({va for _, va, _ in funcs} | {va for _, va in extra} | {hi for _, hi in text})
    extra_va = {va for _, va in extra}
    for _, va in extra:  # RegisterNatives targets (stripped, unsized): up to the next known start, past early rets
        if va not in sizes and any(lo <= va < hi for lo, hi in text):
            sizes[va] = min(next((s for s in starts if s > va), va + 0x400) - va, 0x400)
            queue.append(va)
    seen, hits = set(), []
    while queue and time.time() < end and len(seen) < _NSO_REF_FUNCS:
        va = queue.pop(0)
        if va in seen:
            continue
        seen.add(va)
        targets, keys, pages, callees, lens = [], [], {}, [], []
        for ins in md.disasm(elf.at(va, min(sizes.get(va) or 1024, _NSO_FUNC_CAP)), va):
            mn, ops = ins.mnemonic, ins.op_str
            if arch == "EM_X86_64":
                r = _NSO_RIP.search(ops)
                if r:
                    targets.append(ins.address + ins.size + int(r.group(2), 0) * (1 if r.group(1) == "+" else -1))
            elif mn == "adrp":
                reg, _, page = ops.partition(", ")
                pages[reg] = int(page.lstrip("#"), 0)
            elif mn in ("add", "ldr", "ldrb", "ldrsb") and ops.count(",") >= 1:
                p = [x.strip(" []!") for x in ops.split(",")]
                base = p[1] if len(p) > 1 else ""
                if base in pages:
                    off = int(p[2].lstrip("#"), 0) if len(p) > 2 and p[2].lstrip("#")[:1].isdigit() else 0
                    targets.append(pages[base] + off)
            if mn.startswith(("call", "bl", "jmp", "b")) and not mn.startswith(("blr", "br")):
                t = _NSO_IMM.search(ops)
                if t and any(lo <= int(t.group(1), 0) < hi for lo, hi in text):
                    callees.append(int(t.group(1), 0))
            mi = _NSO_IMM.search(ops)
            if mi and mn.startswith(("xor", "eor", "mov", "cmp", "sub", "add")):
                v = int(mi.group(1), 0) & 0xFFFFFFFF
                if mn.startswith("cmp") and 8 <= v <= 512 and va in extra_va:
                    lens.append(v)  # loop bound: the length of an unsized (stripped) blob whose xor holds a NUL
                k = bytes([v]) if 0 < v < 256 else v.to_bytes(4, "little").rstrip(b"\0") if mn.startswith(("xor", "eor")) else b""
                if k and k not in keys:
                    keys.append(k)
            if mn in ("ret", "retq") and not sizes.get(va):
                break
        queue += [c for c in callees if c not in seen]
        for t in list(dict.fromkeys(targets))[:_NSO_REF_TARGETS]:
            if not any(lo <= t < hi for lo, hi in datas) or time.time() > end:
                continue
            raw = elf.at(t, objs.get(t, 512))
            blobs = [raw[:objs[t]]] if t in objs else []
            blobs += [b for b in (raw.split(b"\0")[0],) if len(b) >= 8 and b not in blobs]
            blobs += [raw[:n] for n in dict.fromkeys(lens) if t not in objs and len(raw) >= n and raw[:n] not in blobs]
            for b in blobs:
                found = ANS_RE_B.findall(b)
                for k in keys[:16]:
                    found = found or ANS_RE_B.findall(bytes(x ^ k[j % len(k)] for j, x in enumerate(b)))
                for k in [None] + keys[:6]:
                    if found or time.time() > end:
                        break
                    r = decode_any(b, key=None if k is None else k[0] if len(k) == 1 else k.decode("latin-1"),
                                   depth=2, cap=300, chain=False)
                    found = [h.encode() for h in ANS_RE_T.findall(r or "")]
                hits += [h.decode() for h in found]
    return hits


_NSO_STK_FUNCS, _NSO_STK_S = 64, 0.3
_NSO_STK_X86 = re.compile(r"(byte|word|dword|qword) ptr \[(rbp|rsp|ebp|esp)(?: ([+-]) (0x[0-9a-f]+|\d+))?\], (\w+)$")
_NSO_STK_A64 = re.compile(r"([wx]\w+), (?:([wx]\w+), )?\[(sp|x29)(?:, #(-?0x[0-9a-f]+|-?\d+))?\]$")
_NSO_STK_W = {"byte": 1, "word": 2, "dword": 4, "qword": 8}
_NSO_STK_HEAD = b"ANS-"


def _nso_stack_runs(md, arch, code, va):
    """Immediate stores into one stack frame, ordered by offset: x86_64 `mov byte/word/dword/qword [rbp/rsp +- off],
    imm` and `movabs/mov reg, imm; mov [..], reg`; arm64 `mov/movz/movk/movn w|x, #imm` then `strb/strh/str/stur/stp
    reg, [sp|x29, #off]` (wzr/xzr = 0). Later stores to an offset win. Yields each contiguous byte run (>= 8)."""
    regs, mem = {}, {}

    def put(base, off, val, n):
        for j in range(n):
            mem[(base, off + j)] = (val >> (8 * j)) & 0xFF

    for ins in md.disasm(code, va):
        mn, ops = ins.mnemonic, ins.op_str
        if arch == "EM_X86_64":
            if mn in ("mov", "movabs"):
                r = _NSO_STK_X86.match(ops)
                if r:
                    src, n = r.group(5), _NSO_STK_W[r.group(1)]
                    v = int(src, 0) if src[:1].isdigit() else regs.get(src[-2:])
                    if v is not None:
                        off = int(r.group(4) or "0", 0) * (-1 if r.group(3) == "-" else 1)
                        put(r.group(2)[-2:], off, v, n)
                    continue
                d, _, s = ops.partition(", ")
                if s[:1].isdigit() and "[" not in d:
                    regs[d[-2:]] = int(s, 0)  # rax/eax/ax share the low bytes
                    continue
            if mn.startswith(("call", "j", "ret")):
                regs.clear()
            elif ops and "[" not in ops.split(",")[0]:
                regs.pop(ops.split(",")[0][-2:], None)
        else:
            p = [x.strip() for x in ops.split(",")]
            reg = lambda x: "x" + x[1:] if x[:1] in "wx" else x
            if mn in ("mov", "movz", "movk", "movn") and len(p) >= 2 and p[1].startswith("#"):
                try:
                    v = int(p[1][1:], 0)
                except ValueError:
                    continue
                sh = int(p[2].split("#")[-1], 0) if len(p) > 2 and "lsl" in p[2] else 0
                if mn == "movk":
                    old = regs.get(reg(p[0]), 0)
                    regs[reg(p[0])] = (old & ~(0xFFFF << sh)) | (v << sh)
                else:
                    v <<= sh
                    regs[reg(p[0])] = ~v if mn == "movn" else v
                continue
            r = _NSO_STK_A64.match(ops) if mn in ("str", "stur", "strb", "sturb", "strh", "sturh", "stp", "stnp") else None
            if r:
                n = 1 if mn.endswith("b") else 2 if mn.endswith("h") else 8 if r.group(1)[0] == "x" else 4
                off = int(r.group(4) or "0", 0)
                for j, src in enumerate((r.group(1), r.group(2)) if mn.startswith(("stp", "stnp")) else (r.group(1),)):
                    v = 0 if src and src[1:] == "zr" else regs.get(reg(src or ""))
                    if v is not None:
                        put(r.group(3), off + j * n, v, n)
                continue
            if mn.startswith(("bl", "ret", "b.", "cb", "tb")) or mn == "b":
                regs.clear()
            elif p and p[0][:1] in "wx":
                regs.pop(reg(p[0]), None)
    for base in {b for b, _ in mem}:
        offs = sorted(o for b, o in mem if b == base)
        run, prev = bytearray(), None
        for o in offs + [None]:
            if o is None or (prev is not None and o != prev + 1):
                if len(run) >= 8:
                    yield bytes(run)
                run = bytearray()
            if o is not None:
                run.append(mem[(base, o)])
                prev = o


def _nso_stack_decode(b, keys):
    """ANS tokens in a stack byte run: raw; known-plaintext anchored ("ANS-" at each start) xor / add / sub with an
    affine per-index key k + m*i, and a 4-byte repeating xor key; then decode_any with the function's imm8 keys."""
    hits = [h.decode() for h in ANS_RE_B.findall(b)]
    for s in (b, b[::-1]):
        for i in range(len(s) - 19):
            c = s[i:i + 20]
            for op, inv in ((lambda x, k: x ^ k, lambda x, p: x ^ p), (lambda x, k: x - k, lambda x, p: x - p),
                            (lambda x, k: x + k, lambda x, p: p - x)):
                k0, k1 = inv(c[0], 0x41) & 0xFF, inv(c[1], 0x4E) & 0xFF
                m = (k1 - k0) & 0xFF
                t = bytes(op(x, (k0 + m * j) & 0xFF) & 0xFF for j, x in enumerate(c))
                if t[:4] == _NSO_STK_HEAD and ANS_RE_B.fullmatch(t):
                    hits.append(t.decode())
            k = bytes(x ^ y for x, y in zip(c[:4], _NSO_STK_HEAD))
            t = bytes(x ^ k[j % 4] for j, x in enumerate(c))
            if ANS_RE_B.fullmatch(t):
                hits.append(t.decode())
    if not hits and len(b) >= 16:
        for k in [None] + keys[:4]:
            r = decode_any(b, key=k, depth=2, cap=150, chain=False)
            hits += ANS_RE_T.findall(r or "")
            if hits:
                break
    return hits


def _nso_stack(elf, arch, funcs, deadline):
    """Row 40 stack strings: the answer (encoded) is assembled on the stack by immediate stores in an export (or a
    local function it calls) and never sits in a data section -- strings / the section sweeps miss it, and a checker
    that compares enc(input) to it never materialises the plaintext for emulation. Each run of stores, ordered by
    stack offset, goes through _nso_stack_decode. x86_64 / arm64; tokens in function order; [] when none."""
    import capstone
    if arch not in ("EM_X86_64", "EM_AARCH64"):
        return []
    a, m = _NSO_ARCH[arch][1]
    md = capstone.Cs(getattr(capstone, a), getattr(capstone, m))
    text = [(addr, addr + len(d)) for name, addr, d in elf.sections() if name == ".text"]
    starts = sorted({va for _, va, _ in funcs} | {hi for _, hi in text})
    sizes = {va: size for _, va, size in funcs}
    queue = [va for _, va, _ in funcs[:_NSO_MAX_FUNCS]]
    end, seen, hits = min(deadline, time.time() + _NSO_STK_S), set(), []
    while queue and time.time() < end and len(seen) < _NSO_STK_FUNCS:
        va = queue.pop(0)
        if va in seen:
            continue
        seen.add(va)
        size = sizes.get(va) or min(next((s for s in starts if s > va), va + 0x800) - va, 0x800)
        code = elf.at(va, min(size, _NSO_FUNC_CAP))
        keys = []
        for ins in md.disasm(code, va):
            mn, ops = ins.mnemonic, ins.op_str
            t = _NSO_IMM.search(ops)
            if t and mn.startswith(("call", "bl", "jmp", "b")) and not mn.startswith(("blr", "br")):
                c = int(t.group(1), 0)
                if any(lo <= c < hi for lo, hi in text) and c not in seen:
                    queue.append(c)
            elif t and mn.startswith(("xor", "eor", "add", "sub")) and 0 < int(t.group(1), 0) < 256:
                k = int(t.group(1), 0)
                keys += [k] if k not in keys else []
        for run in _nso_stack_runs(md, arch, code, va):
            if time.time() > end:
                break
            hits += _nso_stack_decode(run, keys)
    return hits


def _nso_emulate(elf, arch, funcs, deadline, gate=None):
    """Run the exports in unicorn: JNI_OnLoad (fake JavaVM; RegisterNatives' fn pointers are queued), Java_* and the
    registered natives with a fake JNIEnv (NewStringUTF strings are captured), every other export with no args (its
    char* return is read). Imports: malloc/calloc/new bump-allocate, mem/str copies are done, the rest return 0.
    The memory touched (image, heap, stack) and every string handed to a stub is scanned for the token."""
    import unicorn as U
    spec = _NSO_ARCH[arch]
    if spec[0] is None:
        return []
    ua, um = spec[0]
    rc, pfx = {"EM_X86_64": (U.x86_const, "UC_X86_REG_"), "EM_386": (U.x86_const, "UC_X86_REG_"),
               "EM_AARCH64": (U.arm64_const, "UC_ARM64_REG_"), "EM_ARM": (U.arm_const, "UC_ARM_REG_")}[arch]
    argr = [getattr(rc, pfx + r) for r in spec[2]]
    retr = getattr(rc, pfx + spec[3])
    BASE, STUB, JNI, HEAP, STACK, TLS = 0x10000000, 0x60000000, 0x61000000, 0x62000000, 0x63000000, 0x64000000
    RET = STUB + 0xF000
    if elf.e != "<" or elf.is64 != (arch in ("EM_X86_64", "EM_AARCH64")):
        return []
    W = 8 if elf.is64 else 4  # pointer width: JNI tables, relocated words, JNINativeMethod entries (3 * W)
    MASK = (1 << 8 * W) - 1
    top = max(v + ms for v, _, _, ms in elf.segs)
    size = (top + 0xFFFF) & ~0xFFFF
    if size > 64 << 20:
        return []
    uc = U.Uc(getattr(U, ua), getattr(U, um))
    uc.mem_map(BASE, size)
    for v, o, fs, _ in elf.segs:
        uc.mem_write(BASE + v, elf.b[o:o + fs])
    for a, n in ((STUB, 0x10000), (JNI, 0x10000), (HEAP, 1 << 20), (STACK, 1 << 20), (TLS, 0x10000)):
        uc.mem_map(a, n)
    uc.mem_write(STUB, spec[4] * (0x10000 // len(spec[4])))
    uc.mem_write(JNI, (JNI + 0x100).to_bytes(W, "little"))
    uc.mem_write(JNI + 0x100, b"".join((STUB + 16 * i).to_bytes(W, "little") for i in range(300)))
    VM = JNI + 0x2000
    uc.mem_write(VM, (VM + 0x100).to_bytes(W, "little"))
    uc.mem_write(VM + 0x100, b"".join((STUB + 16 * (300 + i)).to_bytes(W, "little") for i in range(16)))
    uc.mem_write(TLS, (TLS + 0x8000).to_bytes(W, "little"))
    if arch == "EM_X86_64":
        uc.reg_write(rc.UC_X86_REG_FS_BASE, TLS)
    elif arch == "EM_AARCH64":
        uc.reg_write(rc.UC_ARM64_REG_TPIDR_EL0, TLS)
    elif arch == "EM_386":  # bionic's canary is %gs:0x14 with gs = 0 here: a zero page answers it
        uc.mem_map(0, 0x10000)
    else:
        try:  # VFP / NEON on (vectorised Thumb-2 loops), else the first vld1 faults
            uc.reg_write(rc.UC_ARM_REG_C1_C0_2, uc.reg_read(rc.UC_ARM_REG_C1_C0_2) | 0xF00000)
            uc.reg_write(rc.UC_ARM_REG_FPEXC, 0x40000000)
        except Exception:  # noqa: BLE001
            pass
    imports = {}  # import name -> stub slot

    def put(o, v):
        if BASE <= o <= BASE + size - W:
            uc.mem_write(o, (v & MASK).to_bytes(W, "little"))

    for _, typ, _, off, ssz, link in elf.secs:
        if typ == 19:  # SHT_RELR: even word = address, odd word = bitmap of the next 63 words
            where = 0
            for (e,) in struct.iter_unpack("<" + "IQ"[W // 8], elf.b[off:off + (min(ssz, W << 17) & -W)]):
                for o in ([e] if not e & 1 else [where + W * j for j in range(8 * W - 1) if e >> (j + 1) & 1]):
                    if o <= size - W:
                        put(BASE + o, BASE + int.from_bytes(uc.mem_read(BASE + o, W), "little"))
                where = e + W if not e & 1 else where + (8 * W - 1) * W
        if typ not in (4, 9):  # SHT_RELA, SHT_REL (32-bit ABIs: the addend is the word in place)
            continue
        syms = elf.syms.get(link, [])
        fmt = "<" + ("QQq" if W == 8 else "IIi" if typ == 4 else "II")
        n = struct.calcsize(fmt)
        for r in struct.iter_unpack(fmt, elf.b[off:off + min(ssz, n * 200_000) // n * n]):
            r_off, info = r[:2]
            inplace = int.from_bytes(elf.at(r_off, W).ljust(W, b"\0"), "little") if len(r) == 2 else 0
            add = r[2] if len(r) == 3 else inplace
            kind, si = (spec[5].get(info & 0xFFFFFFFF), info >> 32) if W == 8 else (spec[5].get(info & 0xFF), info >> 8)
            if kind == "rel":
                put(BASE + r_off, BASE + add)
            elif kind in ("sym", "abs") and si < len(syms):
                name, val, _, _, shndx = syms[si]
                add = add if kind == "abs" or len(r) == 3 else 0  # REL GLOB_DAT / JUMP_SLOT ignore the word in place
                if shndx and val:
                    put(BASE + r_off, BASE + val + add)
                else:
                    if name not in imports and len(imports) < 3000:
                        imports[name] = len(imports)
                    put(BASE + r_off, STUB + 16 * (400 + imports[name]) if name in imports else RET)
    slot_name = {v: k for k, v in imports.items()}
    strs, natives, heap = [], [], [HEAP + 0x100]

    def rd(p, n=256):
        try:
            return bytes(uc.mem_read(p, n))
        except U.UcError:
            try:
                return bytes(uc.mem_read(p, 16))
            except U.UcError:
                return b""

    def cstr(p):
        return rd(p).split(b"\0")[0] if p > 0x1000 else b""

    def alloc(n):
        p, heap[0] = heap[0], (heap[0] + max(16, min(n, 1 << 18)) + 15) & ~15
        if heap[0] >= HEAP + (1 << 20):
            heap[0] = HEAP + 0x100
        return p

    def hook(uc, addr, size, _):
        if addr == RET:
            uc.emu_stop()
            return
        if argr:
            a = [uc.reg_read(r) for r in argr] + [0] * (6 - len(argr))
        else:  # i386 cdecl: [esp] = return address, then the args
            a = list(struct.unpack("<6I", rd(uc.reg_read(rc.UC_X86_REG_ESP) + 4, 24).ljust(24, b"\0")))
        for x in a[:4]:
            s = cstr(x)
            if len(s) >= 4:
                strs.append(s)
        i, ret = (addr - STUB) // 16, 0
        if i < 300:
            if i == 6:
                ret = 1
            elif i == 167:
                ret = a[1]
            elif i == 169:
                ret = alloc(16)
            elif i == 215:
                for j in range(min(a[3], 64)):
                    e = rd(a[2] + 3 * W * j, 3 * W)
                    if len(e) == 3 * W:
                        natives.append(int.from_bytes(e[2 * W:], "little"))
        elif i < 316:
            if i - 300 in (4, 6, 7):
                uc.mem_write(a[1], JNI.to_bytes(W, "little"))
        elif i - 400 in slot_name:
            n = slot_name[i - 400]
            if n in _NSO_ALLOC:
                ret = alloc(a[0] * a[1] if n == "calloc" else len(cstr(a[0])) + 1 if n == "strdup" else a[1]
                            if n == "realloc" else a[0])
                if n in ("realloc", "strdup") and a[0]:
                    uc.mem_write(ret, rd(a[0], min(a[1], 1 << 16)) if n == "realloc" else cstr(a[0]))
            elif n == "strlen":
                ret = len(rd(a[0], 4096).split(b"\0")[0])
            elif n in ("memcpy", "memmove", "__memcpy_chk", "__memmove_chk"):
                uc.mem_write(a[0], rd(a[1], min(a[2], 1 << 16))[:a[2]])
                ret = a[0]
            elif n in ("memset", "__memset_chk"):
                uc.mem_write(a[0], bytes([a[1] & 0xFF]) * min(a[2], 1 << 16))
                ret = a[0]
            elif n in ("strcpy", "__strcpy_chk", "strcat", "__strcat_chk"):
                d = a[0] + (len(cstr(a[0])) if "cat" in n else 0)
                uc.mem_write(d, cstr(a[1]) + b"\0")
                ret = a[0]
            elif n in ("__stack_chk_fail", "abort", "exit", "_exit", "__cxa_throw"):
                uc.emu_stop()
        uc.reg_write(retr, ret & MASK)

    uc.hook_add(U.UC_HOOK_CODE, hook, begin=STUB, end=STUB + 0xFFFF)

    def call(va, args):
        if time.time() > deadline:
            return
        sp = STACK + (1 << 20) - 0x1000
        for r, v in zip(argr, list(args) + [0] * 6):
            uc.reg_write(r, v)
        if arch == "EM_X86_64":
            sp -= 8
            uc.mem_write(sp, RET.to_bytes(8, "little"))
            uc.reg_write(rc.UC_X86_REG_RSP, sp)
        elif arch == "EM_386":
            sp -= 28
            uc.mem_write(sp, struct.pack("<7I", RET, *[v & MASK for v in (list(args) + [0] * 6)[:6]]))
            uc.reg_write(rc.UC_X86_REG_ESP, sp)
        elif arch == "EM_ARM":  # a Thumb target keeps its odd address: unicorn starts it in Thumb state
            uc.reg_write(rc.UC_ARM_REG_SP, sp)
            uc.reg_write(rc.UC_ARM_REG_LR, RET)
        else:
            uc.reg_write(rc.UC_ARM64_REG_SP, sp)
            uc.reg_write(rc.UC_ARM64_REG_LR, RET)
        try:
            uc.emu_start(va, RET, timeout=_NSO_FN_US, count=_NSO_FN_INSNS)
        except Exception:  # noqa: BLE001 - a fault (or a hook error) ends this export's run only
            pass
        s = cstr(uc.reg_read(retr))
        if s:
            strs.append(s)

    if gate is not None:  # jni_gate_scan: the caller drives the probing through call()
        return gate(call, strs, lambda: uc.reg_read(retr), (BASE, JNI, VM), natives)
    hits = []
    for name, va, _ in funcs[:_NSO_MAX_FUNCS]:
        if name == "JNI_OnLoad":
            call(BASE + va, (VM, 0))
            for fn in list(dict.fromkeys(natives))[:32]:
                call(BASE + fn if fn < BASE else fn, (JNI, 0))
        else:
            call(BASE + va, (JNI, 0) if name.startswith("Java_") else ())
        hits += [m.decode() for s in strs for m in ANS_RE_B.findall(s)]
        strs.clear()
    for a, n in ((HEAP, heap[0] - HEAP), (STACK + (1 << 20) - 0x10000, 0x10000), (BASE, size)):
        hits += [m.decode() for m in ANS_RE_B.findall(rd(a, n))]
    return hits


# Anti-debug / root / instrumentation gates (rows 41, 47, 48, 66): the import's return value on a clean device
# (untraced, no su, no frida). fopen/open of a /proc path succeeds when clean (the gate then reads it).
_NGB_CLEAN = {"ptrace": 0, "fopen": 0, "fopen64": 0, "open": -1, "open64": -1, "openat": -1, "opendir": 0, "popen": 0,
              "access": -1, "faccessat": -1, "stat": -1, "lstat": -1, "stat64": -1, "lstat64": -1, "strstr": 0,
              "strcasestr": 0, "memmem": 0, "dlopen": 0, "__system_property_find": 0}
_NGB_PATH2 = {"openat", "faccessat"}  # path is the 2nd argument
_NGB_FUNCS, _NGB_INSNS, _NGB_S = 24, 6000, 0.25
_NGB_X86_JCC = {"je": "eq", "jz": "eq", "jne": "ne", "jnz": "ne", "js": "mi", "jns": "pl", "jl": "lt", "jge": "ge",
                "jle": "le", "jg": "gt", "jb": "lo", "jae": "hs", "jbe": "ls", "ja": "hi"}


def _ngb_reg(n):
    """Canonical 64-bit register name (eax/ax/al -> rax, r12d -> r12, w3 -> x3)."""
    m = re.fullmatch(r"(r\d+)[dwb]?", n) or re.fullmatch(r"e?([abcd])[xlh]", n) or re.fullmatch(r"[er]?(si|di|bp|sp)l?", n)
    if m:
        g = m.group(1)
        return g if g.startswith("r") else "r" + g + ("x" if len(g) == 1 else "")
    return "x" + n[1:] if re.fullmatch(r"w\d+", n) else n


def _ngb_cond(cc, a, b, w):
    """Does condition `cc` hold after `cmp a, b` (width w bits)? None when unknown."""
    m = (1 << w) - 1
    sa, sb = [((v & m) ^ (1 << w - 1)) - (1 << w - 1) for v in (a, b)]
    ua, ub = a & m, b & m
    r = {"eq": ua == ub, "ne": ua != ub, "lt": sa < sb, "ge": sa >= sb, "le": sa <= sb, "gt": sa > sb,
         "mi": (sa - sb) & m >> (w - 1) & 1 == 1, "pl": (sa - sb) & m >> (w - 1) & 1 == 0, "lo": ua < ub, "hs": ua >= ub,
         "ls": ua <= ub, "hi": ua > ub, "cc": ua < ub, "cs": ua >= ub}
    return r.get(cc)


def _ngb_imports(elf):
    """GOT slot va -> imported name (JUMP_SLOT / GLOB_DAT RELA entries against .dynsym)."""
    want = {"EM_X86_64": (7, 6), "EM_AARCH64": (1026, 1025)}.get(elf.arch, ())
    got = {}
    for _, typ, _, off, ssz, link in elf.secs:
        syms = elf.syms.get(link)
        if typ != 4 or not syms:
            continue
        for r_off, info, _ in struct.iter_unpack("<QQq", elf.b[off:off + min(ssz, 24 << 16) // 24 * 24]):
            if info & 0xFFFFFFFF in want and info >> 32 < len(syms):
                got[r_off] = syms[info >> 32][0].split("@")[0]
    return got


def _ngb_walk(elf, md, arch, va, size, got, ctx, depth):
    """Walk one function from `va`, following ONLY the clean side of every gate branch (a conditional branch on the
    register holding a gate import's result, evaluated with _NGB_CLEAN) and both sides of every other branch.
    Appends data refs / immediates seen to ctx['refs'] / ctx['keys']; ctx['gates'] counts resolved gate branches."""
    lo, hi = va, va + (size or 0x1000)
    work, seen, plt = [va], set(), ctx["plt"]
    while work and ctx["n"] < _NGB_INSNS and time.time() < ctx["end"]:
        a = work.pop(0)
        if a in seen or not lo <= a < hi:
            continue
        alias, flags, pages, argref, chain = set(), None, {}, {}, {}
        for ins in md.disasm(elf.at(a, hi - a), a):
            if ins.address in seen:
                break
            seen.add(ins.address)
            ctx["n"] += 1
            mn, ops = ins.mnemonic, ins.op_str
            p = [x.strip(" []!") for x in ops.split(",")] if ops else []
            dst = _ngb_reg(p[0].split()[-1]) if p and p[0] else ""
            tgt = None
            if arch == "EM_X86_64":
                r = _NSO_RIP.search(ops)
                if r:
                    tgt = ins.address + ins.size + int(r.group(2), 0) * (1 if r.group(1) == "+" else -1)
            elif mn == "adrp":
                pages[dst] = int(p[1].lstrip("#"), 0)
            elif mn in ("add", "ldr", "ldrb") and len(p) >= 2 and _ngb_reg(p[1]) in pages:
                off = int(p[2].lstrip("#"), 0) if len(p) > 2 and p[2].lstrip("#")[:1].isdigit() else 0
                tgt = pages[_ngb_reg(p[1])] + off
                if mn == "add":
                    pages[dst] = tgt
            if tgt is not None:
                if mn == "add" and _ngb_reg(p[1]) == dst and dst in chain:  # adrp; add #lo; add #field: one ref
                    ctx["refs"][chain[dst]] = tgt
                else:
                    ctx["refs"].append(tgt)
                chain.pop(dst, None)
                if mn == "add":
                    chain[dst] = len(ctx["refs"]) - 1
                if mn in ("lea", "add") or arch == "EM_X86_64" and mn == "mov" and "ptr" not in p[0]:
                    argref[dst] = tgt
            mi = _NSO_IMM.search(ops)
            if mi and mn.startswith(("xor", "eor", "mov")) and 0 < int(mi.group(1), 0) < 256:
                k = bytes([int(mi.group(1), 0)])
                if k not in ctx["keys"]:
                    ctx["keys"].append(k)
            t = _NSO_IMM.search(ops)
            t = int(t.group(1), 0) if t and mn.startswith(("call", "bl", "j", "b", "cb", "tb")) else None
            if mn in ("call", "bl"):
                slot = tgt if mn == "call" and "ptr" in ops else plt.get(t) if t is not None else None
                name = got.get(slot) if slot is not None else None
                if name in _NGB_CLEAN:
                    path = argref.get("rsi" if name in _NGB_PATH2 else "rdi") if arch == "EM_X86_64" else \
                        argref.get("x1" if name in _NGB_PATH2 else "x0")
                    s = b"" if path is None else elf.at(path, 64).split(b"\0")[0]
                    clean = 3 if name.startswith(("fopen", "open")) and s.startswith(b"/proc/") else _NGB_CLEAN[name]
                    alias, flags = {"rax" if arch == "EM_X86_64" else "x0"}, None
                    ctx["clean"] = clean
                    continue
                if t is not None and depth < 2 and ctx["text"][0] <= t < ctx["text"][1] and t not in plt:
                    ctx["callees"].append(t)
                alias, flags = set(), None
                argref.clear()
                continue
            if alias:
                c = ctx["clean"]
                taken = None
                if mn in ("test", "cmp", "cmn") and len(p) == 2:
                    r0 = _ngb_reg(p[0])
                    w = 32 if re.match(r"e|w|r\d+d", p[0]) else 64
                    if r0 in alias and mn == "test" and _ngb_reg(p[1]) == r0:
                        flags = (c, 0, w)
                    elif r0 in alias and _NSO_IMM.search(p[1]) and mn in ("cmp", "cmn"):
                        v = int(p[1].lstrip("#"), 0)
                        flags = (c, -v if mn == "cmn" else v, w)
                    else:
                        alias = set()
                    continue
                cc = _NGB_X86_JCC.get(mn) if arch == "EM_X86_64" else mn[2:] if mn.startswith("b.") else None
                if cc and flags and t is not None:
                    taken = _ngb_cond(cc, *flags)
                elif mn in ("cbz", "cbnz") and _ngb_reg(p[0]) in alias and t is not None:
                    taken = (c == 0) == (mn == "cbz")
                elif mn in ("tbz", "tbnz") and _ngb_reg(p[0]) in alias and t is not None:
                    bit = (c >> int(p[1].lstrip("#"), 0)) & 1
                    taken = bit == (mn == "tbnz")
                elif mn == "mov" and len(p) == 2 and _ngb_reg(p[1]) in alias:
                    alias.add(dst)
                    continue
                elif dst in alias and not mn.startswith(("j", "b", "st", "push")):
                    alias.discard(dst)
                if taken is not None:
                    ctx["gates"] += 1
                    alias, flags = set(), None
                    if taken:
                        work.append(t)
                        break
                    continue
            if mn.startswith(("ret", "hlt", "ud2", "br", "blr")) or mn == "jmp" and t is None:
                break
            if t is not None and (mn.startswith(("j", "cb", "tb")) or mn == "b" or mn.startswith("b.")):
                work.append(t)
                if mn in ("jmp", "b"):
                    break


def native_gate_branch_scan(apk):
    """ANS token on the clean ('not debugged / not rooted') path of a native anti-debug / root / emulator gate (rows
    41, 47, 48, 66), static only: in each Java_* / huntress_* export of the x86_64 / arm64 lib/*/*.so, calls to
    ptrace / fopen / open / access / stat / strstr / ... (PLT stub or -fno-plt GOT slot -> .rela.plt / .rela.dyn
    name) are followed by the first conditional branch on their result (test/cmp/cmn + jcc/b.cond, cbz/cbnz,
    tbz/tbnz); the branch is evaluated with the import's clean return value (_NGB_CLEAN) and only that side is walked
    (other branches: both), local callees one level down too. The data refs on the clean path are matched raw, xor'd
    with the path's byte immediates and through decode_any. Tokens only when >= 1 gate branch was resolved; [] when
    absent; never raises."""
    import capstone
    hits = []
    end = time.time() + _NGB_S
    try:
        with zipfile.ZipFile(apk) as z:
            sos = [i for i in z.infolist() if i.filename.startswith("lib/") and i.filename.endswith(".so")
                   and 0 < i.file_size <= _NSO_MAX_BYTES][:_NSO_MAX_SO]
            sos.sort(key=lambda i: ("x86_64" not in i.filename, "arm64" not in i.filename))
            for info in sos:
                if time.time() > end:
                    break
                try:
                    b = z.read(info)
                    if b[:4] != b"\x7fELF":
                        continue
                    elf = _NsoElf(b)
                    if elf.arch not in ("EM_X86_64", "EM_AARCH64") or not elf.is64 or elf.e != "<":
                        continue
                    hits += _ngb_elf(elf, capstone, end)
                except Exception:  # noqa: BLE001 - a malformed .so contributes nothing
                    continue
    except Exception:  # noqa: BLE001 - truncated / impostor APK
        pass
    return list(dict.fromkeys(hits))


def _ngb_elf(elf, capstone, end):
    arch = elf.arch
    a, m = _NSO_ARCH[arch][1]
    md = capstone.Cs(getattr(capstone, a), getattr(capstone, m))
    got = _ngb_imports(elf)
    if not any(n in _NGB_CLEAN for n in got.values()):
        return []
    plt = {}  # PLT stub va -> GOT slot va
    for name, addr, d in elf.sections():
        if not name.startswith(".plt"):
            continue
        page = {}
        for ins in md.disasm(d[:0x10000], addr):
            r = _NSO_RIP.search(ins.op_str) if arch == "EM_X86_64" else None
            if r and ins.mnemonic.endswith("jmp"):
                plt[addr + (ins.address - addr) // 16 * 16] = ins.address + ins.size + int(r.group(2), 0) * (
                    1 if r.group(1) == "+" else -1)
            elif ins.mnemonic == "adrp":
                page = {"at": ins.address, "v": int(ins.op_str.split("#")[-1], 0)}
            elif ins.mnemonic == "ldr" and page and "x16" in ins.op_str:
                o = re.search(r"#(0x[0-9a-f]+|\d+)\]", ins.op_str)
                plt[page["at"]] = page["v"] + (int(o.group(1), 0) if o else 0)
                page = {}
    text = next(((ad, ad + len(d)) for n, ad, d in elf.sections() if n == ".text"), (0, 0))
    datas = [(ad, ad + len(d)) for _, ad, d in elf.sections(data_only=True)]
    objs = {val: size for syms in elf.syms.values() for _, val, size, typ, shndx in syms
            if typ == 1 and shndx and 0 < size <= 4096}
    funcs = _nso_exports(elf)
    sizes = {va: size for _, va, size in funcs}
    hits = []
    for name, va, size in [f for f in funcs if f[0].startswith("Java_") or "huntress" in f[0].lower()][:_NGB_FUNCS]:
        if time.time() > end:
            break
        ctx = {"refs": [], "keys": [], "gates": 0, "callees": [], "plt": plt, "text": text, "n": 0, "end": end,
               "clean": 0}
        _ngb_walk(elf, md, arch, va, size, got, ctx, 0)
        if not ctx["gates"]:
            continue
        done = {va}
        while ctx["callees"]:
            c = ctx["callees"].pop(0)
            if c not in done and len(done) < 8:
                done.add(c)
                _ngb_walk(elf, md, arch, c, sizes.get(c) or 0x400, got, ctx, 1)
        for t in list(dict.fromkeys(ctx["refs"]))[:_NSO_REF_TARGETS]:
            if not any(lo <= t < hi for lo, hi in datas) or time.time() > end:
                continue
            raw = elf.at(t, objs.get(t, 512))
            blobs = [raw[:objs[t]]] if t in objs else []
            blobs += [x for x in (raw.split(b"\0")[0],) if len(x) >= 8 and x not in blobs]
            for x in blobs:
                found = ANS_RE_B.findall(x)
                for k in ctx["keys"][:16]:
                    found = found or ANS_RE_B.findall(x.translate(bytes(i ^ k[0] for i in range(256))))
                for k in [None] + ctx["keys"][:6]:
                    if found or time.time() > end:
                        break
                    r = decode_any(x, key=None if k is None else k[0], depth=2, cap=300, chain=False)
                    found = [h.encode() for h in ANS_RE_T.findall(r or "")]
                hits += [h.decode() for h in found]
    return hits


def native_export_scan(apk):
    """ANS tokens computed by native code (no literal in the .so): for each lib/*/*.so (pyelftools) the exported funcs
    (JNI_OnLoad, Java_*, huntress_*, the rest) are disassembled (capstone) for their xor/eor byte constants, and every
    .rodata/.data blob is xor'd / decode_any'd with them; when that finds nothing, the exports are emulated in unicorn
    (x86_64 / arm64 / armeabi-v7a ARM+Thumb / x86; fake JNIEnv/JavaVM, RegisterNatives followed). Multi-ABI (row 40):
    emulation goes on through the other lib/<abi>/ dirs until one token is confirmed by >= 2 ABIs; tokens rank by
    the number of ABIs that produced them, then by an assets/ entry quoting them. Bounded (~1.2 s total); [] when
    absent; never raises."""
    hits, abis = [], {}  # token -> {lib/<abi> dirs that produced it}

    def note(new, abi):
        hits.extend(new)
        for t in new:
            abis.setdefault(t, set()).add(abi)

    deadline = time.time() + _NSO_BUDGET_S
    try:
        with zipfile.ZipFile(apk) as z:
            sos = [i for i in z.infolist() if i.filename.startswith("lib/") and i.filename.endswith(".so")
                   and 0 < i.file_size <= _NSO_MAX_BYTES][:_NSO_MAX_SO]
            sos.sort(key=lambda i: ("x86_64" not in i.filename, "arm64" not in i.filename))
            if sos:  # cold imports (pyelftools / capstone / unicorn: ~0.7 s on a slow disk) are not the work budget
                import capstone  # noqa: F401
                import elftools.elf.elffile  # noqa: F401
                import unicorn  # noqa: F401
                deadline = time.time() + _NSO_BUDGET_S
            elves, dex = [], None
            for info in sos:
                abi = info.filename.rsplit("/", 2)[-2] if info.filename.count("/") >= 2 else ""
                try:
                    b = z.read(info)
                    if b[:4] != b"\x7fELF":
                        continue
                    elf = _NsoElf(b)
                    arch = elf.arch
                    if arch not in _NSO_ARCH:
                        continue
                    funcs = _nso_exports(elf)
                    reg = []
                    if not any(n.startswith("Java_") for n, _, _ in funcs):  # row 39: dynamic registration only
                        try:
                            if dex is None:
                                dex = b"".join(z.read(n) for n in z.namelist()
                                               if re.fullmatch(r"classes\d*\.dex", n))[:64 << 20]
                            reg = _nso_registered(elf, dex)
                        except Exception:  # noqa: BLE001
                            reg = []
                    try:  # the export-referenced candidates rank first; the section-wide sweep follows
                        note(_nso_refs(elf, arch, funcs, deadline, reg), abi)
                    except Exception:  # noqa: BLE001
                        pass
                    try:  # row 40: stack strings built by immediate stores
                        note(_nso_stack(elf, arch, funcs, deadline), abi)
                    except Exception:  # noqa: BLE001
                        pass
                    note(_nso_static(elf, _nso_xor_keys(elf, arch, funcs, deadline), deadline), abi)
                    elves.append((elf, arch, funcs, abi))
                except Exception:  # noqa: BLE001 - a malformed .so contributes nothing
                    continue
            for elf, arch, funcs, abi in elves:
                done = {a for v in abis.values() for a in v}
                if time.time() > deadline or (hits and (any(len(v) >= 2 for v in abis.values())
                                                        or all(e[3] in done for e in elves))):
                    break  # one ABI only (every day so far): the first hits end it, as before
                if abi in done:
                    continue
                try:
                    note(_nso_emulate(elf, arch, funcs, deadline), abi)
                except Exception:  # noqa: BLE001
                    continue
            hits = list(dict.fromkeys(hits))
            if len(hits) > 1:  # consensus across ABIs, then an asset quoting the token
                quoted = b"".join(z.read(i)[:1 << 20] for i in z.infolist()[:256]
                                  if i.filename.startswith("assets/") and 0 < i.file_size <= 4 << 20)
                hits.sort(key=lambda t: (-len(abis.get(t, ())), t.encode() not in quoted))
            if hits and sos:  # rows 41/47/48/66: a token on the clean side of an anti-debug / root gate ranks first
                gated = native_gate_branch_scan(apk)
                hits = gated + [t for t in hits if t not in gated]
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        pass
    return list(dict.fromkeys(hits))


_GATE_INPUTS = (0, 1, 0x7F, 0x80, 0xFF, 0x100, 0x7FFF, 0x8000, 0xFFFF, 0x10000, 0x10001, 0x7FFFFFFF, -1, -0x8000,
                -0x10000)
_GATE_MAX_FN = 0x400      # Java_* exports probed (an `int` gate sits in the export or a small helper it calls)
_GATE_MAX_CHECK = 0x100   # other exports: small int checkers only
_GATE_BUDGET_S = 1.0
_GATE_X86_R16 = re.compile(r"^(ax|bx|cx|dx|si|di|bp|r\d+w)$")
_GATE_X86_R8 = re.compile(r"^(al|bl|cl|dl|sil|dil|bpl|r\d+b)$")


def _gate_order(v):
    return (v < 0, abs(v))


def _gate_narrowing(elf, arch, va, size):
    """[u8/s8/u16/s16 found, strongest first] or ["u32"] from the gate's code (the export up to its first conditional
    branch + the helpers it calls directly): x86 movzx/movsx of
    a 16/8-bit register, cwde/cbw, 16-bit cmp/test, and/test with 0xffff/0xff/0x8000/0x80; arm64 uxth/sxth/uxtb/sxtb
    (also as operand extends), tst/and with #0xffff/#0xff/#0x8000/#0x80."""
    import capstone
    a, m = _NSO_ARCH[arch][1]
    md = capstone.Cs(getattr(capstone, a), getattr(capstone, m))
    seen, todo, tags = set(), [(va, min(size or _GATE_MAX_CHECK, _GATE_MAX_FN))], []
    while todo and len(seen) < 6:
        start, n = todo.pop(0)
        if start in seen:
            continue
        seen.add(start)
        for ins in md.disasm(elf.at(start, n), start):
            mn, ops = ins.mnemonic, [o.strip() for o in ins.op_str.split(",")]
            if mn in ("call", "bl") and ops[0].startswith(("0x", "#0x")):
                t = int(ops[0].lstrip("#"), 16)
                if elf.at(t, 1) and not any(t == s[2] for s in elf.secs if s[0] in (".plt", ".plt.sec")):
                    todo.append((t, _GATE_MAX_CHECK))
            if mn in ("ret", "retq") and start != va and ins.address > start:
                break
            imm = ops[-1].lstrip("#") if ops else ""
            if mn in ("uxth", "sxth", "uxtb", "sxtb"):
                tags.append({"uxth": "u16", "sxth": "s16", "uxtb": "u8", "sxtb": "s8"}[mn])
            elif arch == "EM_AARCH64" and any(x in ins.op_str for x in ("uxth", "sxth", "uxtb", "sxtb")):
                tags.append(next(t for x, t in (("uxth", "u16"), ("sxth", "s16"), ("uxtb", "u8"), ("sxtb", "s8"))
                                 if x in ins.op_str))
            elif mn in ("movzx", "movsx") and len(ops) == 2:
                w = "16" if _GATE_X86_R16.match(ops[1]) or ops[1].startswith("word") else \
                    "8" if _GATE_X86_R8.match(ops[1]) or ops[1].startswith("byte") else ""
                if w:
                    tags.append(("u" if mn == "movzx" else "s") + w)
            elif mn in ("cwde", "cwd", "cwtl"):
                tags.append("s16")
            elif mn in ("cbw",):
                tags.append("s8")
            elif mn in ("cmp", "test") and ops and _GATE_X86_R16.match(ops[0]):
                tags.append("u16")
            elif mn in ("and", "ands", "tst", "test") and imm in ("0xffff", "0xff", "0x8000", "0x80"):
                tags.append({"0xffff": "u16", "0xff": "u8", "0x8000": "s16", "0x80": "s8"}[imm])
            elif mn in ("shr", "sar") and ops and _GATE_X86_R16.match(ops[0]):  # shr $0xf, %dx: the int16 sign bit
                tags.append("s16" if imm == "0xf" else "u16")
            elif mn in ("tbz", "tbnz") and imm in ("0xf", "0x7", "15", "7"):
                tags.append("s16" if imm in ("0xf", "15") else "s8")
            elif mn in ("ubfx", "sbfx") and len(ops) == 4 and ops[2].lstrip("#") in ("0", "0x0") and \
                    ops[3].lstrip("#") in ("16", "0x10", "8", "0x8"):
                tags.append(mn[0] + ("16" if ops[3].lstrip("#") in ("16", "0x10") else "8"))
            if start == va and (mn.startswith(("b.", "cbz", "cbnz", "tbz", "tbnz")) or
                                (mn.startswith("j") and mn != "jmp")):
                break  # the export's gate ends at its first conditional branch (the payload after it is not the gate)
    return [t for t in ("s16", "u16", "s8", "u8") if t in tags] or ["u32"]


def jni_gate_scan(apk):
    """Bypass input of a JNI type/length-narrowing gate (row 65; D16 nativeEvidence(len) passed only for 65536): every
    Java_* export (<= 0x400 bytes), every RegisterNatives target and every small (< 0x100) other export of the x86_64 /
    arm64 lib/*/*.so is run in unicorn (fake JNIEnv, as native_export_scan) over the boundary ints _GATE_INPUTS, then,
    if none passes, over (a, b) pairs of them. The commonest outcome (NewStringUTF strings, else the int return) is
    the denial; every other outcome passes. Returns [{"export", "input", "arg2", "narrowing", "narrowings" (all the
    narrowing ops seen, for a two-arg gate), "returns", "answer"}],
    smallest passing input first per export (non-negative ascending, then negative); arg2 None when one int arg
    sufficed; `answer` = the ANS token in / decode_any of what it returned (None if none). [] when absent; never raises."""
    out = []
    deadline = time.time() + _GATE_BUDGET_S
    try:
        with zipfile.ZipFile(apk) as z:
            sos = [i for i in z.infolist() if i.filename.startswith("lib/") and i.filename.endswith(".so")
                   and 0 < i.file_size <= _NSO_MAX_BYTES][:_NSO_MAX_SO]
            sos.sort(key=lambda i: ("x86_64" not in i.filename, "arm64" not in i.filename))
            if sos:
                import capstone  # noqa: F401
                import elftools.elf.elffile  # noqa: F401
                import unicorn  # noqa: F401
                deadline = time.time() + _GATE_BUDGET_S
            done = set()
            for info in sos:
                if time.time() > deadline:
                    break
                try:
                    b = z.read(info)
                    if b[:4] != b"\x7fELF":
                        continue
                    elf = _NsoElf(b)
                    if elf.arch not in ("EM_X86_64", "EM_AARCH64"):
                        continue
                    funcs = _nso_exports(elf)
                    for r in _nso_emulate(elf, elf.arch, funcs, deadline, gate=_gate_probe(elf, funcs, deadline)):
                        if r["export"] not in done:  # one ABI's answer per export
                            out.append(r)
                    done.update(r["export"] for r in out)
                except Exception:  # noqa: BLE001 - a malformed .so contributes nothing
                    continue
    except Exception:  # noqa: BLE001 - truncated / impostor APK
        pass
    return out


def _gate_probe(elf, funcs, deadline):
    def probe(call, strs, ret, bases, natives):
        BASE, JNI, VM = bases
        targets = []
        for name, va, size in funcs[:_NSO_MAX_FUNCS]:
            if name == "JNI_OnLoad":
                call(BASE + va, (VM, 0))
                strs.clear()
                targets += [(f"native@{(fn - BASE if fn >= BASE else fn):#x}", fn - BASE if fn >= BASE else fn, 0, True)
                            for fn in list(dict.fromkeys(natives))[:16]]
            elif name.startswith("Java_") and 0 < size <= _GATE_MAX_FN:
                targets.append((name, va, size, True))
            elif 0 < size < _GATE_MAX_CHECK:
                targets.append((name, va, size, False))
        res = []
        for name, va, size, jni in targets[:24]:
            def run(a, b):
                strs.clear()
                call(BASE + va, ((JNI, 0) if jni else ()) + (a & 0xFFFFFFFF, b & 0xFFFFFFFF))
                r = ret()
                o = tuple(strs) if strs else r & 0xFFFFFFFF
                strs.clear()
                return o
            for pairs in ([(a, 0) for a in _GATE_INPUTS],
                          [(a, b) for a in _GATE_INPUTS for b in _GATE_INPUTS if b]):
                if time.time() > deadline:
                    return res
                outs = {p: run(*p) for p in pairs}
                if len(pairs) > len(_GATE_INPUTS):
                    outs.update({(a, 0): o for (a, b), o in one.items()})
                vals = list(outs.values())
                deny = max(vals, key=lambda o: (vals.count(o), o == outs[(0, 0)]))
                if 2 * vals.count(deny) <= len(vals):  # a lookup (notes[i % n]), not a gate
                    break
                ok = sorted((p for p, o in outs.items() if o != deny),
                            key=lambda p: (_gate_order(p[0]), _gate_order(p[1])))
                if ok and len(ok) < len(outs):
                    a, b = ok[0]
                    o = outs[ok[0]]
                    txt = "\n".join(dict.fromkeys(t.decode("latin-1") for t in o if t.isascii() and bytes(
                        t).decode().isprintable())) if isinstance(o, tuple) else str(o)
                    m = ANS_RE_T.search(txt)
                    if not m:
                        for s in (o if isinstance(o, tuple) else ()):
                            m = ANS_RE_T.search(str(decode_any(s, depth=2, chain=False) or ""))
                            if m:
                                break
                    ans = m.group(0) if m else None
                    nw = _gate_narrowing(elf, elf.arch, va, size)
                    res.append({"export": name, "input": a, "arg2": b if len(pairs) > len(_GATE_INPUTS) else None,
                                "narrowing": nw[0], "narrowings": nw, "returns": txt[:200],
                                "answer": ans})
                    break
                one = outs
        return res
    return probe


# --- Java side of the JNI boundary: dex `native` methods and the constants each call site passes (row 65) ------------
_DNC_MAX_DEX = 32 << 20
_DNC_MAX_UNITS = 2_000_000  # code units decoded across all methods
_DNC_BUDGET_S = 1.0
_DNC_NOWRITE = frozenset([0x00, 0x0E, 0x0F, 0x10, 0x11, 0x1D, 0x1E, 0x1F, 0x26, 0x27, 0x28, 0x29, 0x2A, 0x2B, 0x2C]
                         + list(range(0x32, 0x3E)) + list(range(0x4B, 0x52)) + list(range(0x59, 0x60))
                         + list(range(0x67, 0x79)) + [0xFA, 0xFB, 0xFC, 0xFD])
_DNC_NIBDST = frozenset([0x01, 0x04, 0x07, 0x12, 0x20, 0x21, 0x23] + list(range(0x52, 0x59)) + list(range(0x7B, 0x90))
                        + list(range(0xB0, 0xD8)))
_DNC_IFOP = {0x32: "==", 0x33: "!=", 0x34: "<", 0x35: ">=", 0x36: ">", 0x37: "<="}
_DNC_NEG = {"==": "!=", "!=": "==", "<": ">=", ">=": "<", ">": "<=", "<=": ">"}
_DNC_SWAP = {"==": "==", "!=": "!=", "<": ">", ">=": "<=", ">": "<", "<=": ">="}


def _dnc_tables(d):
    """(sget, tdesc, mref) for one dex: string by idx, type descriptor by idx, method_id idx -> (class, name, params, ret)."""
    u32 = lambda o: struct.unpack_from("<I", d, o)[0]  # noqa: E731
    n_str, o_str, n_typ, o_typ = u32(0x38), u32(0x3C), u32(0x40), u32(0x44)
    n_pro, o_pro, n_met, o_met = u32(0x48), u32(0x4C), u32(0x58), u32(0x5C)
    if (n_str > 1 << 22 or o_str + 4 * n_str > len(d) or o_typ + 4 * n_typ > len(d) or o_pro + 12 * n_pro > len(d)
            or o_met + 8 * n_met > len(d)):
        return None

    @lru_cache(maxsize=None)
    def sget(si):
        if si >= n_str:
            return None
        n, j = _uleb(d, u32(o_str + 4 * si))
        e = d.find(b"\0", j, j + 4 * n + 1)
        return d[j:e].decode("utf-8", "replace") if e >= j else None

    def tdesc(ti):
        return sget(u32(o_typ + 4 * ti)) if ti < n_typ else None

    @lru_cache(maxsize=None)
    def mref(mi):
        if mi >= n_met:
            return None
        ci, pi, ni = struct.unpack_from("<HHI", d, o_met + 8 * mi)
        if pi >= n_pro:
            return None
        _, rt, poff = struct.unpack_from("<III", d, o_pro + 12 * pi)
        ps = []
        if poff and poff + 4 <= len(d):
            ps = [tdesc(struct.unpack_from("<H", d, poff + 4 + 2 * k)[0]) for k in range(min(u32(poff), 255))]
        return tdesc(ci), sget(ni), tuple(ps), tdesc(rt)
    return sget, tdesc, mref


def _dnc_methods(d):
    """[(method_idx, access_flags, code_off)] of every encoded method in one dex's class_data."""
    u32 = lambda o: struct.unpack_from("<I", d, o)[0]  # noqa: E731
    n_cls, o_cls = u32(0x60), u32(0x64)
    if n_cls > 1 << 20 or o_cls + 32 * n_cls > len(d):
        return []
    out = []
    for c in range(n_cls):
        cdata = u32(o_cls + 32 * c + 24)
        if not cdata or cdata >= len(d):
            continue
        try:
            i = cdata
            sf, i = _uleb(d, i)
            inf, i = _uleb(d, i)
            dm, i = _uleb(d, i)
            vm, i = _uleb(d, i)
            for _ in range(2 * (sf + inf)):
                _, i = _uleb(d, i)
            for n in (dm, vm):
                mi = 0
                for _ in range(n):
                    diff, i = _uleb(d, i)
                    fl, i = _uleb(d, i)
                    code, i = _uleb(d, i)
                    mi += diff
                    out.append((mi, fl, code))
        except (IndexError, ValueError):
            continue
    return out


def _dnc_val(v):
    if v is None:
        return None
    k, x = v[0], v[1]
    if k == "int":
        return x
    if k == "str":
        return x
    if k == "bytes":
        return {"bytes_of": x, "length": len(x.encode())}
    if k == "len":
        return {"length_of": x[0], "value": x[1]}
    return None


def _dnc_walk(ins, n_ins, sget, mref, natives):
    """Linear register walk of one method: [(native key, args, static, length checks seen before the call)]."""
    regs, pend, checks, calls, pc = {}, None, [], [], 0
    while pc < n_ins:
        p = 2 * pc
        op = ins[p]
        a8 = ins[p + 1]
        if op == 0 and a8 in (1, 2, 3):  # switch / fill-array payloads
            if a8 == 1:
                pc += 4 + 2 * struct.unpack_from("<H", ins, p + 2)[0]
            elif a8 == 2:
                pc += 2 + 4 * struct.unpack_from("<H", ins, p + 2)[0]
            else:
                w, n = struct.unpack_from("<HI", ins, p + 2)
                pc += 4 + (w * n + 1) // 2
            continue
        if p + 2 * _DOP_W[op] > len(ins):
            break
        res = None
        if op == 0x12:  # const/4
            regs[a8 & 0xF] = ("int", ((a8 >> 4) ^ 8) - 8)
        elif op in (0x13, 0x15, 0x16, 0x19):  # const/16, const/high16, const-wide/16, const-wide/high16
            v = _s16(struct.unpack_from("<H", ins, p + 2)[0])
            regs[a8] = ("int", v << 16 if op == 0x15 else v << 48 if op == 0x19 else v)
        elif op in (0x14, 0x17):  # const, const-wide/32
            regs[a8] = ("int", struct.unpack_from("<i", ins, p + 2)[0])
        elif op == 0x18:  # const-wide
            regs[a8] = ("int", struct.unpack_from("<q", ins, p + 2)[0])
        elif op in (0x1A, 0x1B):  # const-string(/jumbo)
            s = sget(struct.unpack_from("<H" if op == 0x1A else "<I", ins, p + 2)[0])
            regs[a8] = ("str", s) if s is not None else None
        elif op in (0x01, 0x04, 0x07):  # move vA, vB
            regs[a8 & 0xF] = regs.get(a8 >> 4)
        elif op in (0x02, 0x05, 0x08):  # move/from16 vAA, vBBBB
            regs[a8] = regs.get(struct.unpack_from("<H", ins, p + 2)[0])
        elif op in (0x0A, 0x0B, 0x0C):  # move-result*
            regs[a8] = pend
        elif op == 0x21:  # array-length vA, vB
            src = regs.get(a8 >> 4)
            regs[a8 & 0xF] = ("len", (src[1], len(src[1].encode()))) if src and src[0] == "bytes" else None
        elif op in _DNC_IFOP or 0x38 <= op <= 0x3D:  # length checks: if-cmp vA, vB / if-cmpz vAA
            if op in _DNC_IFOP:
                x, y, cmp = regs.get(a8 & 0xF), regs.get(a8 >> 4), _DNC_IFOP[op]
            else:
                x, y, cmp = regs.get(a8), ("int", 0), _DNC_IFOP[op - 6]
            if y and y[0] == "len":
                x, y, cmp = y, x, _DNC_SWAP[cmp]
            if x and x[0] == "len" and y and y[0] == "int":
                # the branch skips the call when `cmp` holds: the fall-through (the call) needs the negation
                checks.append({"length_of": x[1][0], "branch_if": f"len {cmp} {y[1]}", "requires": f"len {_DNC_NEG[cmp]} {y[1]}",
                               "value": y[1]})
        elif 0x6E <= op <= 0x78 and op != 0x73:  # invoke-kind 35c / 3rc
            mi = struct.unpack_from("<H", ins, p + 2)[0]
            if op <= 0x72:
                cnt, g = a8 >> 4, a8 & 0xF
                fe = struct.unpack_from("<H", ins, p + 4)[0]
                rl = [fe & 0xF, (fe >> 4) & 0xF, (fe >> 8) & 0xF, (fe >> 12) & 0xF, g][:cnt]
            else:
                c0 = struct.unpack_from("<H", ins, p + 4)[0]
                rl = list(range(c0, c0 + a8))
            m = mref(mi)
            static = op in (0x71, 0x77)
            if m:
                cls, name, params, _ = m
                r0 = regs.get(rl[0]) if rl else None
                if cls == "Ljava/lang/String;" and r0 and r0[0] == "str":
                    if name == "length" and not params:
                        res = ("len", (r0[1], len(r0[1])))
                    elif name == "getBytes":
                        res = ("bytes", r0[1])
                    elif name in ("trim", "toString", "intern"):
                        res = r0
                key = (cls, name, params)
                if key in natives:
                    k, args = (0 if static else 1), []
                    for t in params:
                        args.append(_dnc_val(regs.get(rl[k])) if k < len(rl) else None)
                        k += 2 if t in ("J", "D") else 1
                    calls.append((key, args, static, list(checks)))
        elif op in _DNC_NIBDST:
            regs.pop(a8 & 0xF, None)
        elif op not in _DNC_NOWRITE:
            regs.pop(a8, None)
        if op in (0x16, 0x17, 0x18, 0x19, 0x0B, 0x04, 0x05):
            regs.pop((a8 & 0xF if op == 0x04 else a8) + 1, None)
        pend = res
        pc += _DOP_W[op]
    return calls


def dex_native_calls(apk):
    """Java side of the JNI boundary (coverage atlas row 65): every `native` method declared in the classes*.dex
    (class, name, param descriptors, return, static) and, for each invoke of it, the constants the caller loads into the
    argument registers (const/const-wide ints, const-string, "s".getBytes() -> {bytes_of, length}, "s".length()) plus the
    String.length()/byte[].length checks seen before the call in that method. [] when none; never raises.
    Answers 'which length/type crosses the boundary' and feeds call-site ints to jni_gate_scan-style bypass questions."""
    out, deadline, budget = {}, time.time() + _DNC_BUDGET_S, [_DNC_MAX_UNITS]
    try:
        z = zipfile.ZipFile(apk)
        dexes = [n for n in z.namelist() if re.fullmatch(r"classes\d*\.dex", Path(n).name)
                 and z.getinfo(n).file_size <= _DNC_MAX_DEX]
        loaded = []
        for n in dexes:
            d = z.read(n)
            if d[:4] != b"dex\n" or len(d) < 0x70:
                continue
            tabs = _dnc_tables(d)
            if not tabs:
                continue
            meths = _dnc_methods(d)
            loaded.append((d, tabs, meths))
            for mi, fl, _ in meths:
                if fl & 0x100:  # ACC_NATIVE
                    m = tabs[2](mi)
                    if m and m[1]:
                        out.setdefault((m[0], m[1], m[2]), {
                            "method": f"{m[0]}->{m[1]}({''.join(m[2])}){m[3]}", "class": m[0], "name": m[1],
                            "params": list(m[2]), "returns": m[3], "static": bool(fl & 0x8), "calls": []})
        if not out:
            return []
        names = {k[1] for k in out}
        for d, (sget, _, mref), meths in loaded:
            n_met, o_met = struct.unpack_from("<II", d, 0x58)
            hot = [struct.pack("<H", mi) for mi, (_, _, ni) in enumerate(struct.iter_unpack("<HHI", d[o_met:o_met + 8 * n_met]))
                   if sget(ni) in names and (mref(mi) or ())[:3] in out]
            for mi, fl, code in meths if hot else ():
                if not code or code + 16 > len(d) or time.time() > deadline:
                    continue
                n_ins = struct.unpack_from("<I", d, code + 12)[0]
                budget[0] -= n_ins
                if budget[0] < 0:
                    break
                ins = d[code + 16:code + 16 + 2 * n_ins]
                if not any(h in ins for h in hot):
                    continue
                try:
                    calls = _dnc_walk(ins, n_ins, sget, mref, out)
                except (IndexError, ValueError, struct.error):
                    continue
                if calls:
                    m = mref(mi)
                    caller = f"{m[0]}->{m[1]}({''.join(m[2])}){m[3]}" if m else str(mi)
                    for key, args, static, checks in calls:
                        out[key]["calls"].append({"caller": caller, "args": args, "length_checks": checks})
    except Exception:  # noqa: BLE001 -- decoy / truncated input: report what was parsed
        pass
    return sorted(out.values(), key=lambda r: r["method"])


_NEST_MAGICS = (b"PK\x03\x04", b"dex\n")
_NEST_MAX_ENTRY = 32 << 20


def _unwrap_nested(b):
    """An entry's bytes as an inner container: a zip/jar/apk or a dex, as-is or under a single-byte xor key (an asset
    dex for DexClassLoader is often xor'd). Returns (kind, bytes) with kind 'zip'/'dex', or None."""
    if len(b) < 8:
        return None
    for magic, kind in zip(_NEST_MAGICS, ("zip", "dex")):
        k = b[0] ^ magic[0]
        if bytes(x ^ k for x in b[:4]) == magic:
            return kind, (b if not k else bytes(x ^ k for x in b))
    return None


def nested_scan(apk, depth=3, _top=True):
    """ANS tokens from containers nested inside the APK (XAPK/APKS base.apk + splits, an asset .jar/.apk/.zip, an asset
    dex for DexClassLoader, plain or single-byte-xor'd), recursing up to `depth` levels. Inside each inner zip it runs
    puzzle_candidates -> raw_entry_scan -> dex_strings (so an inner huntress_puzzle.json codec is decoded); an inner
    dex is scanned for the token directly. The outer APK's own classes*.dex are skipped (dex_strings covers them).
    [] when nothing nested yields a token; never raises."""
    hits = []
    if depth <= 0:
        return hits
    try:
        with zipfile.ZipFile(apk) as z:
            for info in z.infolist():
                if info.is_dir() or info.file_size > _NEST_MAX_ENTRY:
                    continue
                if _top and re.fullmatch(r"classes\d*\.dex", info.filename):
                    continue
                try:
                    with z.open(info) as f:
                        head = f.read(8)
                    got = _unwrap_nested(head)
                    if not got:
                        continue
                    got = _unwrap_nested(z.read(info))
                except (OSError, RuntimeError, zipfile.BadZipFile, EOFError, ValueError):
                    continue
                if not got:
                    continue
                kind, inner = got
                if kind == "dex":
                    hits += [m.decode() for m in ANS_RE_B.findall(inner)]
                    continue
                bio = io.BytesIO(inner)
                hits += [m.group(0) for c in puzzle_candidates(bio) for m in ANS_RE_T.finditer(c)]
                hits += raw_entry_scan(bio) + dex_strings(bio) + nested_scan(bio, depth - 1, False)
    except Exception:  # noqa: BLE001 - truncated / impostor container: no answer here, never raise
        pass
    return list(dict.fromkeys(hits))


# --- local app stores shipped in the APK: SQLite db / shared_prefs xml / adb backup .ab (coverage atlas rows 16-18) ---
_LS_SQLITE = b"SQLite format 3\x00"
_LS_AB = b"ANDROID BACKUP\n"
_LS_MAX_ENTRY = 32 << 20
_LS_MAX_ROWS, _LS_MAX_CELLS, _LS_DECODE_BUDGET = 2000, 20_000, 300
_LS_KEYCOL = re.compile(r"^(key|xor_?key|secret|pass(word)?|seed)$", re.I)


def _ls_sqlite_rows(b, deadline):
    """Every table's rows of an in-memory SQLite image as [{column: value}] (WAL header flags reset so deserialize
    reads it; a progress handler stops the query at `deadline`)."""
    import sqlite3
    b = bytearray(b)
    if b[18:20] == b"\x02\x02":  # WAL mode: an in-memory image has no -wal/-shm, read it as a rollback-journal db
        b[18:20] = b"\x01\x01"
    con = sqlite3.connect(":memory:")
    rows = []
    try:
        con.deserialize(bytes(b))
        con.set_progress_handler(lambda: 1 if time.time() > deadline else 0, 2000)
        tabs = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        for t in tabs:
            if len(rows) >= _LS_MAX_ROWS:
                break
            try:
                cur = con.execute('SELECT * FROM "%s" LIMIT %d' % (t.replace('"', '""'), _LS_MAX_ROWS - len(rows)))
                cols = [d[0] for d in cur.description or ()]
                rows += [dict(zip(cols, r)) for r in cur]
            except sqlite3.Error:
                continue
    except Exception:  # noqa: BLE001 - not a readable db image
        pass
    finally:
        con.close()
    return rows


def _ls_prefs(b):
    """A SharedPreferences xml (<map><string name=..>v</string><int name=.. value=../>...) as one {name: value} row."""
    try:
        root = ET.fromstring(b)
    except (ET.ParseError, ValueError):
        return []
    if root.tag != "map":
        return []
    row = {}
    for el in root:
        v = el.text if el.tag == "string" else el.get("value")
        if el.tag == "set":
            v = " ".join(s.text or "" for s in el)
        if el.get("name") is not None and v is not None:
            row[el.get("name")] = v
    return [row] if row else []


def _ls_ab_members(b):
    """(name, bytes) of every file in an unencrypted adb backup: 'ANDROID BACKUP' / version / compressed / 'none'
    header lines, then a (zlib-deflated) tar. Encrypted backups (AES-256 + password) yield nothing."""
    import tarfile
    parts = b.split(b"\n", 4)
    if len(parts) < 5 or parts[3].strip() != b"none":
        return []
    body = parts[4]
    if parts[2].strip() == b"1":
        d = zlib.decompressobj()
        body = d.decompress(body, _LS_MAX_ENTRY)
    out = []
    try:
        with tarfile.open(fileobj=io.BytesIO(body), mode="r:") as tf:
            for m in tf:
                if m.isfile() and m.size <= _LS_MAX_ENTRY:
                    f = tf.extractfile(m)
                    if f is not None:
                        out.append((m.name, f.read()))
    except Exception:  # noqa: BLE001 - truncated tar: keep the members read so far
        pass
    return out


def _ls_rows(name, b, deadline, depth=2):
    """Rows ({column: value}) found in one entry: a SQLite db, a shared_prefs map, or (recursively) a .ab's members;
    any other .ab member contributes its text as a single-cell row."""
    if b.startswith(_LS_SQLITE):
        return _ls_sqlite_rows(b, deadline)
    if b.startswith(_LS_AB):
        rows = []
        if depth > 0:
            for n, mb in _ls_ab_members(b):
                rows += _ls_rows(n, mb, deadline, depth - 1) or ([{n: mb}] if len(mb) <= _CHAIN_MAX_IN else [])
        return rows
    if b"<map" in b[:512] and (b.lstrip().startswith(b"<?xml") or b.lstrip().startswith(b"<map")):
        return _ls_prefs(b)
    return []


def local_store_scan(apk):
    """ANS tokens stored the way an app keeps local data, shipped inside the APK (or handed out alone): a SQLite db
    (`SQLite format 3\\0` magic, any entry name; every table's cells), a SharedPreferences xml (<string>/value= of a
    <map>), an unencrypted adb backup `.ab` (zlib -> tar -> those again). Each cell is read directly, then through
    decode_payload when its row looks like a puzzle record ({codec, data|payload, key}), then decode_any with the
    row's key-ish column as the key. [] when absent; never raises."""
    hits, rows = [], []
    deadline = time.time() + 1.0
    try:
        try:
            with zipfile.ZipFile(apk) as z:
                for info in z.infolist():
                    if info.is_dir() or info.file_size > _LS_MAX_ENTRY or time.time() > deadline:
                        continue
                    try:
                        with z.open(info) as f:
                            head = f.read(16)
                        if not (head.startswith((_LS_SQLITE, _LS_AB)) or head.lstrip().startswith((b"<?xml", b"<map"))):
                            continue
                        rows += _ls_rows(info.filename, z.read(info), deadline)
                    except (OSError, RuntimeError, zipfile.BadZipFile, EOFError, ValueError):
                        continue
        except zipfile.BadZipFile:  # a bare .db / .ab / prefs xml delivered on its own
            if hasattr(apk, "seek"):
                apk.seek(0)
                b = apk.read(_LS_MAX_ENTRY)
            else:
                with Path(apk).open("rb") as f:
                    b = f.read(_LS_MAX_ENTRY)
            rows += _ls_rows("", b, deadline)
        budget, cells = _LS_DECODE_BUDGET, 0
        for row in rows:
            lk = {str(k).lower(): v for k, v in row.items()}
            key = next((v for k, v in row.items() if _LS_KEYCOL.match(str(k)) and v not in (None, "")), None)
            data = lk.get("data", lk.get("payload"))
            if isinstance(data, str) and "codec" in lk:
                d = decode_payload(lk.get("codec"), data, key)
                if d and ANS_RE_T.search(d):
                    hits += ANS_RE_T.findall(d)
                    continue
            for v in row.values():
                cells += 1
                if cells > _LS_MAX_CELLS or time.time() > deadline:
                    break
                if isinstance(v, (bytes, bytearray, memoryview)):
                    v = bytes(v).decode("utf-8", "replace")
                if not isinstance(v, str):
                    continue
                m = ANS_RE_T.findall(v)
                if m:
                    hits += m
                    continue
                s = v.strip()
                if budget > 0 and 16 <= len(s) <= _CHAIN_MAX_IN:
                    budget -= 1
                    d = decode_any(s, key, chain=True, chain_s=0.05)
                    if d:
                        hits += ANS_RE_T.findall(d)
    except Exception:  # noqa: BLE001 - truncated / impostor store: no answer here
        pass
    return list(dict.fromkeys(hits))


# --- Unity IL2CPP global-metadata.dat string literals (coverage atlas row 56) ------------------------------------------
_IL2_MAGIC = b"\xaf\x1b\xb1\xfa"  # 0xFAB11BAF little-endian
_IL2_MAX_ENTRY = 64 << 20
_IL2_MAX_LITS, _IL2_DECODE_BUDGET = 200_000, 400
_IL2_RUN = re.compile(rb"[\x20-\x7e]{16,4096}")


def _il2_unxor(b):
    """The metadata bytes, plain or under a single-byte xor (a cheap 'encrypted metadata' trick), or None."""
    if len(b) < 32:
        return None
    k = b[0] ^ _IL2_MAGIC[0]
    if bytes(x ^ k for x in b[:4]) != _IL2_MAGIC:
        return None
    return b if not k else bytes(x ^ k for x in b)


def il2cpp_literals(b):
    """C# string literals (`ldstr` constants) of a Unity IL2CPP global-metadata.dat: header magic 0xFAB11BAF + version,
    then the stringLiteral table ({uint32 length, int32 dataIndex}, or dataIndex only) indexing stringLiteralData.
    Header layout v16-v31 = (offset, size) pairs at 8 / 16; v38+ = (offset, size, count) sections at 8 / 20. When
    neither layout validates (unknown version), printable runs of the file stand in. [] when not IL2CPP metadata."""
    b = _il2_unxor(b)
    if b is None:
        return []
    n = len(b)
    ver = struct.unpack_from("<i", b, 4)[0]
    if not 16 <= ver <= 64:
        return []
    for step in ((12, 8) if ver >= 38 else (8, 12)):
        if 8 + 2 * step > n:
            continue
        lo, ls = struct.unpack_from("<ii", b, 8)
        do, ds = struct.unpack_from("<ii", b, 8 + step)
        cnt = struct.unpack_from("<i", b, 16)[0] if step == 12 else 0
        if not (0 < lo and 0 <= ls and lo + ls <= n and 0 < do and 0 <= ds and do + ds <= n):
            continue
        es = ls // cnt if cnt > 0 and ls % cnt == 0 else 8
        if es not in (4, 8) or ls % es or ls // es > _IL2_MAX_LITS:
            continue
        rows = [struct.unpack_from("<Ii" if es == 8 else "<i", b, lo + i * es) for i in range(ls // es)]
        if es == 4:  # dataIndex only: each literal runs to the next one's start
            idx = [r[0] for r in rows] + [ds]
            rows = [(idx[i + 1] - idx[i], idx[i]) for i in range(len(rows))]
        if not all(0 <= di and 0 <= ln and di + ln <= ds for ln, di in rows):
            continue
        return [b[do + di:do + di + ln].decode("utf-8", "replace") for ln, di in rows]
    return [m.group(0).decode("latin-1") for m in _IL2_RUN.finditer(b[:_IL2_MAX_ENTRY])]


def il2cpp_literal_scan(apk):
    """ANS tokens among the C# string literals of a Unity IL2CPP build (any entry starting with the global-metadata.dat
    magic, usually assets/bin/Data/Managed/Metadata/global-metadata.dat; a bare metadata file works too). Each literal
    is read directly, as a huntress_puzzle-style json ({codec, data|payload, key}), then through decode_any -- unkeyed,
    then keyed by a short neighbouring literal (a `const string key` sits next to its ciphertext in source order).
    [] when absent; never raises."""
    hits, lits = [], []
    deadline = time.time() + 1.0
    try:
        try:
            with zipfile.ZipFile(apk) as z:
                for info in z.infolist():
                    if info.is_dir() or info.file_size > _IL2_MAX_ENTRY or time.time() > deadline:
                        continue
                    try:
                        with z.open(info) as f:
                            if _il2_unxor(f.read(32)) is None:
                                continue
                        lits += il2cpp_literals(z.read(info))
                    except (OSError, RuntimeError, zipfile.BadZipFile, EOFError, ValueError):
                        continue
        except zipfile.BadZipFile:  # a bare global-metadata.dat handed out on its own
            if hasattr(apk, "seek"):
                apk.seek(0)
                b = apk.read(_IL2_MAX_ENTRY)
            else:
                with Path(apk).open("rb") as f:
                    b = f.read(_IL2_MAX_ENTRY)
            lits = il2cpp_literals(b)
        for s in lits:
            hits += ANS_RE_T.findall(s)
        if hits:
            return list(dict.fromkeys(hits))
        budget = _IL2_DECODE_BUDGET
        for i, s in enumerate(lits):
            t = s.strip()
            if budget <= 0 or time.time() > deadline:
                break
            if t.startswith("{") and "codec" in t:
                try:
                    p = json.loads(t)
                    d = decode_payload(p.get("codec"), p.get("data", p.get("payload", "")), p.get("key"))
                    if d and ANS_RE_T.search(d):
                        hits += ANS_RE_T.findall(d)
                        continue
                except (ValueError, AttributeError, TypeError):
                    pass
            if not 16 <= len(t) <= _CHAIN_MAX_IN:
                continue
            budget -= 1
            d = decode_any(t, chain=True, chain_s=0.03)
            for j in (i - 1, i + 1):
                if d or not 0 <= j < len(lits) or not 1 <= len(lits[j].strip()) <= 32 or time.time() > deadline:
                    continue
                budget -= 1
                d = decode_any(t, lits[j].strip(), chain=True, chain_s=0.03)
            if d:
                hits += ANS_RE_T.findall(d)
    except Exception:  # noqa: BLE001 - truncated / impostor metadata: no answer here
        pass
    return list(dict.fromkeys(hits))


# --- WebView / hybrid-app assets: html / js / json under assets/ (coverage atlas rows 13, 14, 57) ----------------------
_WV_EXT = re.compile(r"(?i)^assets/.*\.(?:html?|m?js|json|xhtml)$")
_WV_MAX_ENTRY = 4 << 20
_WV_MAX_TOTAL = 24 << 20
_WV_DECODE_BUDGET = 300
_WV_LIT = re.compile(r"""(["'`])((?:[^"'`\\\n]|\\.|(?!\1)["'`]){1,16384}?)\1""", re.S)
_WV_CONCAT = re.compile(r"""(?:(["'])(?:[^"'\\\n]|\\.)*?\1\s*\+\s*)+(["'])(?:[^"'\\\n]|\\.)*?\2""")
_WV_NUM = r"(?:0[xX][0-9a-fA-F]+|\d+)"
_WV_FCC = re.compile(r"fromCharCode\s*(?:\.apply\s*\(\s*\w*\s*,|\(\s*\.\.\.|\()\s*\[?\s*(" + _WV_NUM + r"(?:\s*,\s*" + _WV_NUM + r")*)")
_WV_ARR = re.compile(r"\[\s*(" + _WV_NUM + r"(?:\s*,\s*" + _WV_NUM + r"){7,4095})\s*,?\s*\]")
_WV_XKEY = re.compile(r"\^\s*(?:(" + _WV_NUM + r")\b|(?:\w+\.)?(\w+)\s*(?:\.charCodeAt|\[))")
_WV_ESC = re.compile(r"\\(?:x([0-9a-fA-F]{2})|u\{([0-9a-fA-F]{1,6})\}|u([0-9a-fA-F]{4})|([0-7]{1,3})|(.))", re.S)
_WV_SIMPLE = {"n": "\n", "t": "\t", "r": "\r", "b": "\b", "f": "\f", "v": "\v", "0": "\0"}


def _wv_unescape(s):
    def sub(m):
        h = m.group(1) or m.group(2) or m.group(3)
        if h:
            return chr(min(int(h, 16), 0x10FFFF))
        if m.group(4):
            return chr(int(m.group(4), 8) & 0xFF)
        c = m.group(5)
        return "" if c == "\n" else _WV_SIMPLE.get(c, c)
    return _WV_ESC.sub(sub, s)


def _wv_nums(s):
    return [int(t, 0) for t in re.findall(_WV_NUM, s)]


def _wv_candidates(text):
    """(strings, keys) from one html/js/json asset: unescaped string literals (adjacent `"a" + "b"` concatenations
    joined), String.fromCharCode lists, numeric/hex byte arrays; keys = short literals and `^ <int>` / `^ name[...]`
    xor operands (a named key resolves to that variable's literal)."""
    lits, cands, keys = [], [], []
    for m in _WV_CONCAT.finditer(text):
        parts = [_wv_unescape(p.group(2)) for p in _WV_LIT.finditer(m.group(0))]
        cands.append("".join(parts))
    for m in _WV_LIT.finditer(text):
        if m.group(1) == "`" and "${" in m.group(2):
            continue
        lits.append(_wv_unescape(m.group(2)))
    for m in _WV_FCC.finditer(text):
        try:
            cands.append("".join(chr(n) for n in _wv_nums(m.group(1))))
        except (ValueError, OverflowError):
            pass
    for m in _WV_ARR.finditer(text):
        ns = _wv_nums(m.group(1))
        if all(n < 256 for n in ns):
            cands.append(bytes(ns))
        elif all(n < 0x110000 for n in ns):
            cands.append("".join(chr(n) for n in ns))
    named = {}
    for m in re.finditer(r"""\b(\w+)\s*[:=]\s*(["'`])((?:[^"'`\\\n]|\\.){1,64}?)\2""", text):
        named[m.group(1)] = _wv_unescape(m.group(3))
    for m in _WV_XKEY.finditer(text):
        k = int(m.group(1), 0) if m.group(1) else named.get(m.group(2))
        if k is not None and k not in keys:
            keys.append(k)
    keys += [s for s in lits if 1 <= len(s) <= 32 and s.strip() == s and s not in keys][:24]
    cands = cands + [s for s in lits if len(s) >= 16]
    return lits + cands, cands, keys


def webview_asset_scan(apk):
    """ANS tokens hidden in a WebView / Cordova / Capacitor / Flutter app's web assets (assets/**/*.html|js|json,
    incl. assets/www, assets/public, flutter_assets). Pure regex, no JS engine: each asset's string literals (JS
    escapes \\xHH / \\uHHHH / \\u{..} / octal undone, `"a"+"b"` joined), String.fromCharCode lists and numeric/hex byte
    arrays are scanned for a literal token, then run through decode_any -- unkeyed, then keyed by the file's `^ <int>`
    / `^ key[...]` xor operands and short literals. huntress_puzzle.json is puzzle_candidates' job and skipped.
    [] when absent; never raises."""
    hits, files = [], []
    deadline = time.time() + 0.9
    try:
        with zipfile.ZipFile(apk) as z:
            total = 0
            for info in z.infolist():
                n = info.filename
                if (info.is_dir() or not _WV_EXT.match(n) or n.endswith("huntress_puzzle.json")
                        or info.file_size > _WV_MAX_ENTRY or total + info.file_size > _WV_MAX_TOTAL):
                    continue
                try:
                    files.append(z.read(info).decode("utf-8", "replace"))
                    total += info.file_size
                except (OSError, RuntimeError, zipfile.BadZipFile, EOFError, ValueError, NotImplementedError):
                    continue
        parsed = []
        for t in files:
            if time.time() > deadline:
                break
            strs, cands, keys = _wv_candidates(t)
            for s in strs:
                if isinstance(s, str):
                    hits += ANS_RE_T.findall(s)
            parsed.append((cands, keys))
        if hits:
            return list(dict.fromkeys(hits))
        budget = _WV_DECODE_BUDGET
        for cands, keys in parsed:
            for c in cands:
                if budget <= 0 or time.time() > deadline:
                    break
                b = c.encode("utf-8", "surrogatepass") if isinstance(c, str) else c
                if not 8 <= len(b) <= _CHAIN_MAX_IN:
                    continue
                budget -= 1
                d = decode_any(b, chain=True, chain_s=0.03)
                for k in keys:
                    if d or budget <= 0 or time.time() > deadline:
                        break
                    if k == c:
                        continue
                    budget -= 1
                    d = decode_any(b, k, depth=2, chain=False)
                if d:
                    hits += ANS_RE_T.findall(d)
    except Exception:  # noqa: BLE001 - not a zip / malformed asset: no answer here
        pass
    return list(dict.fromkeys(hits))


# --- static-key AES/DES/3DES (coverage atlas row 33: SecretKeySpec + const key, ciphertext in an asset / the json) -----
_SKC_KEYISH = re.compile(r"key|secret|pass|pwd|seed", re.I)
_SKC_IVISH = re.compile(r"\biv\b|^iv|nonce|vector|^iv_|_iv$", re.I)
_SKC_MAX_STRS, _SKC_MAX_CTS, _SKC_MAX_IVS, _SKC_CT_CAP, _SKC_MAX_POOL = 32, 8, 8, 4096, 20_000
_SKC_BAD = re.compile(r"[\s/;()<>\[\]]|^L.*;$|^\W*$")


def _skc_blobs(s):
    """Bytes a text field can stand for: base64 / urlsafe / hex (the raw text never; it is not ciphertext)."""
    b = s.encode("latin-1", "replace") if isinstance(s, str) else s
    out = []
    for fn in (_b64ish, lambda x: _b64ish(x, True),
               lambda x: binascii.unhexlify(x.strip()) if re.fullmatch(rb"(?:[0-9a-fA-F]{2})+", x.strip()) else None):
        try:
            r = fn(b)
        except Exception:  # noqa: BLE001 - not this encoding
            r = None
        if r and r not in out:
            out.append(r)
    return out


def _skc_keys(s):
    """Key bytes a constant string can stand for: raw / hex / base64 of a valid length, sha256 (16/32), md5, sha1[:16],
    and Arrays.copyOf(s.getBytes(), 16)."""
    import hashlib
    sb = s.encode("utf-8", "replace")
    out = [sb] + [r for r in _skc_blobs(sb) if len(r) in (8, 16, 24, 32)]
    h = hashlib.sha256(sb).digest()
    out += [h[:16], h, hashlib.md5(sb).digest(), hashlib.sha1(sb).digest()[:16]]
    if len(sb) not in (8, 16, 24, 32) and 4 <= len(sb) < 32:
        out.append(sb[:16].ljust(16, b"\0"))
    return [k for k in dict.fromkeys(out) if len(k) in (8, 16, 24, 32)]


_SKC_POOL = re.compile(rb"([\x04-\x40])([\x21-\x7e]{4,64})\0")
_SKC_HEXK = re.compile(r"[0-9a-fA-F]{32}|[0-9a-fA-F]{48}|[0-9a-fA-F]{64}")
_SKC_MIX = re.compile(r"\d.*[A-Za-z]|[A-Za-z].*\d")
_SKC_PUNCT = re.compile(r"[^A-Za-z0-9_$]")
_SKC_WORD = re.compile(r"[a-z][A-Za-z]*|[A-Z][A-Za-z]*|[A-Z_]+|[a-z_]+|<.*>|\$.*|[\w$]+(?:\.[\w$]+)+")


def _skc_dex_strs(d):
    """Printable string-pool entries of one dex that could be a key constant (4-64 chars, not a type/path/message): one
    C-speed regex over the dex for `uleb len, chars, NUL` records whose length byte matches (a stray hit is only one more
    candidate key)."""
    if d[:4] != b"dex\n" or len(d) < 0x70:
        return []
    out = []
    for m in _SKC_POOL.finditer(d, 0x70):
        if m.group(1)[0] == len(m.group(2)):
            t = m.group(2).decode()
            if not _SKC_BAD.search(t) and (len(t) in (8, 16, 24, 32, 48, 64) or not _SKC_WORD.fullmatch(t)):
                out.append(t)
                if len(out) >= _SKC_MAX_POOL:
                    break
    return out


def _skc_rank(t):
    n = len(t)
    sc = 2 * (n in (8, 16, 24, 32)) + 3 * (n in (32, 48, 64) and bool(_SKC_HEXK.fullmatch(t)))
    sc += bool(_SKC_MIX.search(t)) + bool(_SKC_PUNCT.search(t)) - 3 * bool(_SKC_WORD.fullmatch(t))
    return -sc


def _xor_int(a, b):
    n = min(len(a), len(b))
    return (int.from_bytes(a[:n], "big") ^ int.from_bytes(b[:n], "big")).to_bytes(n, "big")


def static_key_cipher_scan(apk, seeds=None):
    """ANS tokens from a payload encrypted with a hardcoded key: ciphertext = a base64/hex field of any asset json
    (`data` / `payload` / ... first) or an asset file (base64/hex text or raw bytes) or a long base64/hex dex string;
    keys = json key-ish fields, then dex string-pool constants ranked key-like (<= 32 strings), each as raw / hex / b64 /
    sha256 / md5 / sha1 bytes. Tries AES (16/24/32), DES (8), 3DES (16/24) in ECB, CBC (IV zero / json iv / key /
    ct prefix), CTR and GCM (tag ignored; nonce json / zero / ct prefix). The answer regex is the oracle. [] when absent;
    never raises. `seeds` (identity_key_scan): try only these key strings instead of the json / dex constants."""
    from Crypto.Cipher import AES, DES, DES3
    hits, cts, jkeys, ivs, dstrs = [], [], [], [], []
    try:
        with zipfile.ZipFile(apk) as z:
            for info in z.infolist():
                n = info.filename
                if info.is_dir() or info.file_size > _NEST_MAX_ENTRY:
                    continue
                if re.fullmatch(r"classes\d*\.dex", n):
                    dstrs += _skc_dex_strs(z.read(info))
                    continue
                if not n.startswith(("assets/", "res/raw/")) or info.file_size > 1 << 20:
                    continue
                b = z.read(info)
                if n.endswith(".json"):
                    try:
                        stack, pri, rest = [(None, json.loads(b))], [], []
                    except ValueError:
                        stack, pri, rest = [], [], []
                    while stack:
                        k, v = stack.pop()
                        if isinstance(v, dict):
                            stack += list(v.items())[::-1]
                        elif isinstance(v, list):
                            stack += [(k, x) for x in v[::-1]]
                        elif isinstance(v, str) and v:
                            k = str(k or "")
                            if _SKC_IVISH.search(k):
                                ivs += [v.encode()] + _skc_blobs(v)
                            elif _SKC_KEYISH.search(k):
                                jkeys.append(v)
                            elif len(v) >= 12:
                                (pri if re.search(r"data|payload|cipher|ct|enc|blob|value", k, re.I) else rest).append(v)
                    cts += [r for v in pri + rest for r in _skc_blobs(v) if len(r) >= 8]
                elif b and info.file_size <= 64 << 10:
                    cts += _skc_blobs(b) or ([b] if len(b) >= 16 else [])
        cts += [r for t in dstrs if len(t) >= 24 for r in _skc_blobs(t) if len(r) >= 16]
        cts = [c[:_SKC_CT_CAP] for c in dict.fromkeys(cts)][:_SKC_MAX_CTS]
        if not cts:
            return []
        strs = list(dict.fromkeys(jkeys + sorted(dict.fromkeys(dstrs), key=_skc_rank)))[:_SKC_MAX_STRS] if seeds is None else list(seeds)
        keys = list(dict.fromkeys(k for s in strs for k in _skc_keys(s)))
        jivs = list(dict.fromkeys(v for v in ivs if len(v) >= 12))[:4]  # CTR / GCM: json IVs only (a cipher each)
        ivs = list(dict.fromkeys(ivs + [k for k in keys if len(k) in (8, 12, 16)]))[:_SKC_MAX_IVS]

        def hit(p):
            for m in ANS_RE_B.findall(p):
                t = m.decode()
                if t not in hits:
                    hits.append(t)

        for k in keys:
            ciphers = []
            if len(k) in (16, 24, 32):
                ciphers.append((AES, 16))
            if len(k) == 8:
                ciphers.append((DES, 8))
            if len(k) in (16, 24):
                try:
                    DES3.adjust_key_parity(k)
                    ciphers.append((DES3, 8))
                except ValueError:
                    pass
            for mod, bs in ciphers:
                ecb = mod.new(k, mod.MODE_ECB)
                for ct in cts:
                    body = ct[:len(ct) - len(ct) % bs]
                    if len(body) >= bs:
                        d = ecb.decrypt(body)
                        hit(d)  # ECB
                        tail = _xor_int(d[bs:], body[:-bs])
                        hit(tail)  # CBC from block 2 on (any IV); also IV = the ct prefix
                        for iv in [bytes(bs)] + [v[:bs] for v in ivs if len(v) >= bs]:
                            hit(_xor_int(d[:bs], iv) + tail)
                    if mod is not AES:
                        continue
                    ct = ct[:1024]
                    for iv, c in [(bytes(16), ct), (ct[:16], ct[16:])] + [(v[:16], ct) for v in jivs if len(v) >= 16]:
                        if c:
                            hit(AES.new(k, AES.MODE_CTR, nonce=b"", initial_value=iv).decrypt(c))
                    for nc, c in [(bytes(12), ct), (ct[:12], ct[12:])] + [(v[:12], ct) for v in jivs]:
                        if c:  # GCM keystream = CTR from nonce || 2 (96-bit nonce); tag left unverified
                            hit(AES.new(k, AES.MODE_CTR, nonce=b"", initial_value=nc + b"\0\0\0\2").decrypt(c))
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        pass
    return hits


# --- identity-derived keys (coverage atlas rows 32, 33): key = client secret / case ref / package / day, raw or hashed --
_IDK_DEX = re.compile(rb"SECRET-[0-9A-Za-z_\-]{6,64}|MOB-\d{1,3}-[0-9A-Fa-f]{6,16}|[a-z]\w*(?:\.\w+){2,8}\.v[0-9a-f]{12}")
_IDK_PKG = re.compile(r"[a-z]\w*(?:\.[A-Za-z_]\w*){2,8}")
_IDK_SYS = ("android.", "androidx.", "com.android.", "com.google.", "java.", "kotlin.")
_IDK_MAX_SEEDS, _IDK_MAX_PAYLOADS, _IDK_BUDGET_S = 12, 6, 0.8


def _idk_seeds(z):
    """Identity strings an app could derive its key from, most specific first: client secret (SECRET-...), case ref
    (MOB-NN-<hex>), package name (dex / manifest string pool) with its v<12hex> suffix, then the day number (puzzle json
    `day`, package dNN, case ref NN) -- plus the payload strings of the asset jsons."""
    found, pkgs, days, payloads = [], [], [], []
    for info in z.infolist():
        n = info.filename
        if info.is_dir() or info.file_size > _NEST_MAX_ENTRY:
            continue
        if re.fullmatch(r"classes\d*\.dex", n):
            found += [m.decode() for m in _IDK_DEX.findall(z.read(info))]
        elif n == "AndroidManifest.xml":
            b = z.read(info)
            if b[:2] == b"\x03\x00":
                pkgs += [t for t in _pool_strings(b)[:400] if _IDK_PKG.fullmatch(t) and not t.startswith(_IDK_SYS)][:2]
        elif n.startswith("assets/") and n.endswith(".json") and info.file_size <= 1 << 20:
            try:
                stack = [(None, json.loads(z.read(info)))]
            except ValueError:
                continue
            while stack:
                k, v = stack.pop()
                if isinstance(v, dict):
                    stack += list(v.items())[::-1]
                elif isinstance(v, list):
                    stack += [(k, x) for x in v[::-1]]
                elif str(k).lower() == "day" and isinstance(v, (int, str)) and str(v).isdigit():
                    days.append(int(v))
                elif isinstance(v, str) and len(v) >= 12:
                    payloads.append(v)
    seeds = [s for s in found if s.startswith("SECRET-")] + [s for s in found if s.startswith("MOB-")]
    for p in [s for s in found if "." in s] + pkgs:
        seeds += [p, p.rsplit(".", 1)[-1]] + ([p[-12:]] if re.search(r"\.v[0-9a-f]{12}$", p) else [])
        m = re.search(r"\.d(\d{1,2})\.", p)
        days += [int(m.group(1))] if m else []
    days += [int(s.split("-")[1]) for s in found if s.startswith("MOB-")]
    seeds = list(dict.fromkeys(seeds))[:_IDK_MAX_SEEDS]
    seeds += list(dict.fromkeys(x for d in days for x in (str(d), "%02d" % d)))[:2]
    return seeds, list(dict.fromkeys(payloads))[:_IDK_MAX_PAYLOADS]


def identity_key_scan(apk):
    """ANS tokens from a payload keyed by the app's own identity (rows 32-33: "predictable crypto"): each seed of
    _idk_seeds() raw, and its md5 / sha1 / sha256 as digest bytes and as hex text, as the decode_any key (xor / add / shift
    after base64 / hex ...) of every asset-json payload, then as AES/DES keys via static_key_cipher_scan(seeds=...). [] when
    absent; never raises."""
    import hashlib
    hits = []
    try:
        with zipfile.ZipFile(apk) as z:
            seeds, payloads = _idk_seeds(z)
        if not seeds:
            return []
        keys, texts = [], []
        for s in seeds:
            sb = s.encode()
            keys.append(s)
            for h in (hashlib.md5(sb), hashlib.sha1(sb), hashlib.sha256(sb)):
                keys += [h.digest(), h.hexdigest()]
                texts += [h.hexdigest()[:32], h.hexdigest()[:16]]
        end = time.time() + _IDK_BUDGET_S
        for data in payloads:
            for k in keys:
                if time.time() > end:
                    break
                d = decode_any(data, key=k, depth=2, cap=300, chain=False)
                if d:
                    hits += [t for t in ANS_RE_T.findall(d) if t not in hits]
            if hits:
                return hits
        hits += static_key_cipher_scan(apk, seeds=list(dict.fromkeys(seeds + texts)))
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        pass
    return list(dict.fromkeys(hits))


# --- signing certificate facts (coverage atlas rows 9 / 49 / 59: app-links fingerprint, integrity check, cert fields) ---
_SIG_V1 = re.compile(r"META-INF/[^/]+\.(RSA|DSA|EC)$", re.I)
_SIG_BLOCK_IDS = {0x7109871A: "v2", 0xF05368C0: "v3", 0x1B93AD61: "v3.1"}
_SIG_MAX_CERTS, _SIG_BUDGET_S = 8, 0.8
_SIG_DN_SHORT = {"common_name": "CN", "organization_name": "O", "organizational_unit_name": "OU", "country_name": "C",
                 "locality_name": "L", "state_or_province_name": "ST", "email_address": "EMAILADDRESS",
                 "street_address": "STREET", "domain_component": "DC", "serial_number": "SERIALNUMBER"}


def _sig_lp(b, i):
    """One uint32-length-prefixed item of the APK Signing Block at b[i:] -> (item, next offset); raises on overrun."""
    n = struct.unpack_from("<I", b, i)[0]
    if i + 4 + n > len(b):
        raise ValueError("lp overrun")
    return b[i + 4:i + 4 + n], i + 4 + n


def _sig_block_certs(z):
    """DER certificates of the v2 / v3 / v3.1 signers in the APK Signing Block ("APK Sig Block 42" just before the
    central directory), read through the ZipFile's own file handle. [(scheme, der)]; raises on a malformed block."""
    fp, cd = z.fp, z.start_dir
    if cd < 32:
        return []
    fp.seek(cd - 24)
    tail = fp.read(24)
    if tail[8:] != b"APK Sig Block 42":
        return []
    size = struct.unpack_from("<Q", tail)[0]
    if not 24 <= size <= min(cd - 8, 8 << 20):
        return []
    fp.seek(cd - size - 8)
    blk = fp.read(size + 8)
    out, i, end = [], 8, len(blk) - 24
    while i + 12 <= end:
        n, pid = struct.unpack_from("<QI", blk, i)
        if n < 4 or i + 8 + n > end:
            break
        scheme = _SIG_BLOCK_IDS.get(pid)
        if scheme:
            seq, _ = _sig_lp(blk[i + 12:i + 8 + n], 0)
            j = 0
            while j < len(seq) and len(out) < _SIG_MAX_CERTS:
                signer, j = _sig_lp(seq, j)
                sd, _ = _sig_lp(signer, 0)
                _digests, k = _sig_lp(sd, 0)
                certs, _ = _sig_lp(sd, k)
                c = 0
                while c < len(certs) and len(out) < _SIG_MAX_CERTS:
                    der, c = _sig_lp(certs, c)
                    out.append((scheme, der))
        i += 8 + n
    return out


def signing_certs(apk):
    """Signer certificates of an APK, v1 (META-INF/*.RSA|DSA|EC PKCS#7) and v2/v3 (APK Signing Block), deduplicated:
    [{"scheme", "subject", "issuer" ("C=US, O=..., CN=..." as apksigner prints them), "subject_fields" / "issuer_fields"
    ({attr: value}), "serial" (hex), "not_before", "not_after", "sha256" / "sha1" / "md5" (lower hex of the DER),
    "sha256_colon" (assetlinks.json / apksigner style "AB:CD:..."), "der" (bytes)}]. [] when absent; never raises."""
    import hashlib
    from asn1crypto import cms, x509
    ders = []
    try:
        with zipfile.ZipFile(apk) as z:
            try:
                ders += _sig_block_certs(z)
            except (ValueError, struct.error, OSError):
                pass
            for info in z.infolist():
                if _SIG_V1.match(info.filename) and info.file_size <= 1 << 20 and len(ders) < 2 * _SIG_MAX_CERTS:
                    try:
                        sd = cms.ContentInfo.load(z.read(info))["content"]
                        ders += [("v1", c.chosen.dump()) for c in (sd["certificates"] or [])
                                 if c.name == "certificate"][:_SIG_MAX_CERTS]
                    except Exception:  # noqa: BLE001 - impostor / truncated PKCS#7
                        continue
    except Exception:  # noqa: BLE001 - not a zip
        return []
    out, seen = [], {}
    for scheme, der in ders:
        if der in seen:
            seen[der]["scheme"] += "+" + scheme if scheme not in seen[der]["scheme"].split("+") else ""
            continue
        try:
            c = x509.Certificate.load(der)
            tbs = c["tbs_certificate"]

            def dn(name):
                fields = {}
                for rdn in name.chosen:
                    for atv in rdn:
                        v, t = atv["value"].native, str(atv["type"].native)
                        fields[_SIG_DN_SHORT.get(t, t)] = v if isinstance(v, str) else str(v)
                return fields
            subj, iss = dn(tbs["subject"]), dn(tbs["issuer"])
            h = hashlib.sha256(der).hexdigest()
            rec = {"scheme": scheme, "subject": ", ".join(f"{k}={v}" for k, v in list(subj.items())[::-1]),
                   "issuer": ", ".join(f"{k}={v}" for k, v in list(iss.items())[::-1]), "subject_fields": subj,
                   "issuer_fields": iss, "serial": "%x" % tbs["serial_number"].native,
                   "not_before": str(tbs["validity"]["not_before"].native),
                   "not_after": str(tbs["validity"]["not_after"].native),
                   "sha256": h, "sha1": hashlib.sha1(der).hexdigest(), "md5": hashlib.md5(der).hexdigest(),
                   "sha256_colon": ":".join(h[i:i + 2] for i in range(0, 64, 2)).upper(), "der": der}
        except Exception:  # noqa: BLE001 - not a certificate
            continue
        seen[der] = rec
        out.append(rec)
    return out


def signing_cert_scan(apk):
    """ANS tokens hidden in / keyed by the APK's signing certificate (rows 9 / 49 / 59): every subject / issuer DN value
    and the serial (hex / decimal) of each v1 / v2 / v3 signer cert, plain or through decode_any; then each asset-json
    payload decoded with the cert digest (sha256 / sha1 / md5 as bytes, lower / upper / colon hex) as the decode_any key,
    and those digest strings as AES/DES key seeds (static_key_cipher_scan). [] when absent; never raises."""
    hits = []
    try:
        certs = signing_certs(apk)
        if not certs:
            return []
        end = time.time() + _SIG_BUDGET_S
        for c in certs:
            vals = list(c["subject_fields"].values()) + list(c["issuer_fields"].values())
            vals += [c["serial"], str(int(c["serial"], 16))]
            for v in dict.fromkeys(vals):
                if time.time() > end:
                    break
                hits += [t for t in ANS_RE_T.findall(v) if t not in hits]
                if not hits and len(v) >= 12:
                    d = decode_any(v, depth=2, cap=600, chain=False)
                    hits += [t for t in ANS_RE_T.findall(d or "") if t not in hits]
        if hits:
            return hits
        with zipfile.ZipFile(apk) as z:
            payloads = _idk_seeds(z)[1]
        keys, seeds = [], []
        for c in certs:
            for h in ("sha256", "sha1", "md5"):
                keys += [bytes.fromhex(c[h]), c[h], c[h].upper()]
            keys.append(c["sha256_colon"])
            seeds += [c["sha256"], c["sha256"].upper(), c["sha256_colon"], c["sha1"], c["md5"]]
        for data in payloads:
            if ANS_RE_T.search(decode_any(data, depth=2, cap=300, chain=False) or ""):
                continue    # keyless reading already answers: the puzzle path's, not a cert-keyed payload
            for k in keys:
                if time.time() > end:
                    break
                d = decode_any(data, key=k, depth=2, cap=300, chain=False)
                hits += [t for t in ANS_RE_T.findall(d or "") if t not in hits]
            if hits:
                return hits
        if payloads:
            hits += static_key_cipher_scan(apk, seeds=list(dict.fromkeys(seeds)))
    except Exception:  # noqa: BLE001 - truncated / impostor APK: no answer here
        pass
    return list(dict.fromkeys(hits))


def _run(cmd, timeout=90):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.SubprocessError):
        return None


@lru_cache(maxsize=16)
def jadx_sources_text(apk, timeout=120):
    """Decompile with jadx and return all decompiled source text (cached). Empty string if jadx fails."""
    out = Path(apk).resolve().parent / (".android-work/" + Path(apk).stem + "-jadx")
    out.mkdir(parents=True, exist_ok=True)
    if not any(out.rglob("*.java")):
        _run(["jadx", "-d", str(out), "--no-res", str(apk)], timeout=timeout)
    buf = []
    for j in out.rglob("*.java"):
        try:
            buf.append(j.read_text(errors="replace"))
        except OSError:
            continue
    return "\n".join(buf)


@lru_cache(maxsize=16)
def apktool_dir(apk, timeout=120):
    """Decode with apktool (manifest + resources + smali) and return the output dir, or None."""
    out = Path(apk).resolve().parent / (".android-work/" + Path(apk).stem + "-apktool")
    if not (out / "AndroidManifest.xml").exists():
        r = _run(["apktool", "d", "-f", "-o", str(out), str(apk)], timeout=timeout)
        if r is None or not (out / "AndroidManifest.xml").exists():
            return None
    return out


# --- certificate pinning: OkHttp `sha256/<b64>` pins in dex + NSC <pin-set> (coverage atlas rows 27, 28) ---------------
_PIN_DEX = re.compile(rb"(sha(?:256|1))/([A-Za-z0-9+/]{27,86}={0,2})")
_PIN_POOL = re.compile(rb"([\x04-\x7f])([\x21-\x7e]{4,127})\0")
_PIN_HOST = re.compile(r"(?:\*{1,2}\.)?[a-z0-9](?:[a-z0-9-]{0,62}\.)+[a-z][a-z0-9-]{1,62}", re.I)
_PIN_URL = re.compile(r"https?://([^/:?#\s]+)")
_PIN_NOTHOST = frozenset(("com", "org", "net", "io", "android", "androidx", "java", "javax", "kotlin", "kotlinx",
                          "okhttp3", "okio", "dalvik", "retrofit2", "sun", "libcore", "junit", "me", "de", "ch"))
_PIN_MAX_ENTRY = 32 << 20


def _pin_b64(v):
    """Raw digest bytes of a pin's base64 (std or url-safe, padding optional); None when not base64."""
    v = v.strip()
    try:
        return base64.b64decode(v + "=" * (-len(v) % 4), altchars=b"-_" if ("-" in v or "_" in v) else None,
                                validate=True)
    except (binascii.Error, ValueError):
        return None


def _pin_rec(algo, b64, source, hosts=()):
    raw = _pin_b64(b64)
    return {"pin": f"{algo.lower().replace('-', '')}/{b64}", "algo": algo.lower().replace("-", ""), "b64": b64,
            "hex": raw.hex() if raw is not None else None, "len": len(raw) if raw is not None else None,
            "source": source, "hosts": list(hosts)}


def _axml_events(b):
    """(kind, name, attrs, text) events of a binary AXML: ("start", tag, {attr: value}, None), ("end", tag, None, None),
    ("text", None, None, cdata). Attribute values are the raw string (or the typed int as str / "true"/"false")."""
    pool = None
    i = 8 if b[:2] == b"\x03\x00" else len(b)
    while i + 8 <= len(b):
        typ, hsz, size = struct.unpack_from("<HHI", b, i)
        if size < 8 or i + size > len(b):
            break
        if typ == 0x0001 and pool is None:
            pool = _pool_strings(b[i:i + size])
        elif pool is not None and typ in (0x0102, 0x0103, 0x0104):
            s = lambda k: pool[k] if 0 <= k < len(pool) else None  # noqa: E731
            e = i + hsz
            if typ == 0x0102:
                _ns, name, astart, asize, acount = struct.unpack_from("<IIHHH", b, e)
                attrs = {}
                for k in range(min(acount, 256)):
                    a = e + astart + k * max(asize, 20)
                    _ans, an, raw, _sz, _r0, dtype, data = struct.unpack_from("<IIIHBBI", b, a)
                    if raw != 0xFFFFFFFF:
                        v = s(raw)
                    elif dtype == 0x12:
                        v = "true" if data else "false"
                    elif dtype == 0x03:
                        v = s(data)
                    else:
                        v = str(data)
                    attrs[s(an) or str(an)] = v
                yield "start", s(name), attrs, None
            elif typ == 0x0103:
                yield "end", s(struct.unpack_from("<II", b, e)[1]), None, None
            else:
                yield "text", None, None, s(struct.unpack_from("<I", b, e)[0])
        i += size


def _xml_events(b):
    """Same events from a plaintext (uncompiled) XML file."""
    def walk(el):
        yield "start", el.tag.split("}")[-1], {k.split("}")[-1]: v for k, v in el.attrib.items()}, None
        if (el.text or "").strip():
            yield "text", None, None, el.text
        for c in el:
            yield from walk(c)
        yield "end", el.tag.split("}")[-1], None, None
    yield from walk(ET.fromstring(b))


def _nsc_parse(name, b):
    """Network-security-config facts of one res/xml file: [{"file", "kind" (domain-config / base-config /
    debug-overrides), "domains" [{"host", "includeSubdomains"}], "pins", "expiration", "cleartextTrafficPermitted",
    "trust_anchors"}]; [] when the file is not an NSC."""
    ev = _axml_events(b) if b[:2] == b"\x03\x00" else _xml_events(b) if b.lstrip()[:1] == b"<" else ()
    out, stack, cur, last = [], [], [], None
    for kind, tag, attrs, text in ev:
        if kind == "start":
            stack.append(tag)
            last = (tag, attrs)
            if tag in ("domain-config", "base-config", "debug-overrides"):
                cur.append({"file": name, "kind": tag, "domains": [], "pins": [], "expiration": None,
                            "cleartextTrafficPermitted": attrs.get("cleartextTrafficPermitted"), "trust_anchors": []})
                out.append(cur[-1])
            elif cur and tag == "pin-set":
                cur[-1]["expiration"] = attrs.get("expiration")
            elif cur and tag == "certificates":
                cur[-1]["trust_anchors"].append(attrs.get("src"))
        elif kind == "end":
            if stack:
                stack.pop()
            if tag in ("domain-config", "base-config", "debug-overrides") and cur:
                cur.pop()
            last = None
        elif kind == "text" and cur and last and (text or "").strip():
            tag, attrs = last
            if tag == "domain":
                cur[-1]["domains"].append({"host": text.strip(), "includeSubdomains": attrs.get("includeSubdomains")})
            elif tag == "pin":
                cur[-1]["pins"].append(_pin_rec(attrs.get("digest") or "SHA-256", text.strip(), name,
                                                [d["host"] for d in cur[-1]["domains"]]))
    return out


def cert_pins(apk):
    """Certificate-pinning facts of an APK (rows 27, 28): {"pins": [{"pin" ("sha256/<b64>"), "algo", "b64", "hex" (digest
    bytes, lower hex), "len", "source" (dex / res/xml file), "hosts"}], "hosts": pinned / referenced hostnames,
    "nsc": per-<domain-config> records of every res/xml network-security-config (domains, includeSubdomains, pins,
    pin-set expiration, cleartextTrafficPermitted, trust anchors)}. Dex pins come from OkHttp CertificatePinner-style
    `sha256/<b64>` / `sha1/<b64>` constants; dex hosts are string-pool hostnames / URL hosts of a dex that holds a pin.
    Empty lists when absent; never raises."""
    facts = {"pins": [], "hosts": [], "nsc": []}
    try:
        with zipfile.ZipFile(apk) as z:
            for info in z.infolist():
                n = info.filename
                if info.is_dir() or info.file_size > _PIN_MAX_ENTRY:
                    continue
                is_dex = bool(re.fullmatch(r"classes\d*\.dex", Path(n).name))
                if not (is_dex or (n.startswith("res/") and n.endswith(".xml"))):
                    continue
                try:
                    b = z.read(info)
                except (OSError, RuntimeError, zipfile.BadZipFile, EOFError, ValueError):
                    continue
                if is_dex:
                    pins = list(dict.fromkeys((m.group(1).decode(), m.group(2).decode()) for m in _PIN_DEX.finditer(b)))
                    if not pins:
                        continue
                    hosts = []
                    for m in _PIN_POOL.finditer(b, 0x70):
                        if m.group(1)[0] != len(m.group(2)):
                            continue
                        t = m.group(2).decode()
                        u = _PIN_URL.match(t)
                        h = u.group(1) if u else t
                        if _PIN_HOST.fullmatch(h) and h.lstrip("*.").split(".")[0].lower() not in _PIN_NOTHOST:
                            hosts.append(h)
                    hosts = list(dict.fromkeys(hosts))
                    facts["pins"] += [_pin_rec(a, v, n, hosts) for a, v in pins]
                    facts["hosts"] += hosts
                elif b"pin" in b or b"domain" in b or b[:2] == b"\x03\x00":
                    try:
                        recs = _nsc_parse(n, b)
                    except Exception:  # noqa: BLE001 - malformed AXML: skip the file
                        continue
                    facts["nsc"] += recs
                    for r in recs:
                        facts["pins"] += r["pins"]
                        facts["hosts"] += [d["host"] for d in r["domains"]]
    except Exception:  # noqa: BLE001 - not a zip
        pass
    facts["hosts"] = list(dict.fromkeys(facts["hosts"]))
    return facts


def cert_pin_scan(apk):
    """ANS tokens encoded as a certificate pin (rows 27, 28): each dex `sha256/<b64>` / NSC <pin> value's digest bytes
    scanned for a literal token, then the b64 text through decode_any; pinned hostnames scanned too. [] when absent."""
    hits = []
    try:
        f = cert_pins(apk)
        for p in f["pins"]:
            raw = _pin_b64(p["b64"]) or b""
            hits += [t.decode() for t in ANS_RE_B.findall(raw)]
            if not hits:
                d = decode_any(p["b64"], depth=2, cap=300, chain=False)
                hits += ANS_RE_T.findall(d or "")
        for h in f["hosts"]:
            hits += ANS_RE_T.findall(h)
    except Exception:  # noqa: BLE001
        pass
    return list(dict.fromkeys(hits))


def decompiled_scan(apk):
    """ANS tokens from apktool resources/smali and jadx sources (for an answer that lives in code)."""
    hits = []
    d = apktool_dir(apk)
    if d:
        for f in list(d.rglob("*.xml")) + list(d.rglob("*.smali")):
            try:
                hits += ANS_RE_T.findall(f.read_text(errors="replace"))
            except OSError:
                continue
    hits += ANS_RE_T.findall(jadx_sources_text(apk))
    return hits


def extract_answer(apk):
    """Robust answer recovery for a mobile challenge. Tries fast paths first, escalating to decompilation:
    puzzle json -> raw zip-entry scan -> dex strings -> nested containers -> static-key AES/DES -> apktool/jadx decompiled scan. Returns the first
    ANS-<16 hex> found (via the decoders + a direct token scan), or None. Order favours speed; the later
    stages cover an answer that was moved into the dex/resources/code (even with renaming)."""
    for cand in puzzle_candidates(apk):
        m = ANS_RE_T.search(cand)
        if m:
            return m.group(0)
    for stage in (raw_entry_scan, dex_strings, nested_scan, static_key_cipher_scan, identity_key_scan,
                  signing_cert_scan, decompiled_scan):
        hits = stage(apk)
        if hits:
            return hits[0]
    return None


# --- manifest facts (for exported-component / deep-link / allowBackup style questions) ------------
def manifest_facts(apk):
    """Parse AndroidManifest.xml via apktool's decoded (text) manifest. Returns a dict with package,
    allowBackup, debuggable, permissions, and per-component exported/intent-filter/deep-link data.
    Empty dict if apktool is unavailable."""
    d = apktool_dir(apk)
    if not d:
        return {}
    try:
        root = ET.parse(d / "AndroidManifest.xml").getroot()
    except (OSError, ET.ParseError):
        return {}
    app = root.find("application")
    facts = {
        "package": root.get("package"),
        "permissions": sorted(e.get(_ANDROID_NS + "name") for e in root.findall("uses-permission")
                              if e.get(_ANDROID_NS + "name")),
        "allowBackup": (app.get(_ANDROID_NS + "allowBackup") if app is not None else None),
        "debuggable": (app.get(_ANDROID_NS + "debuggable") if app is not None else None),
        "components": [],
    }
    for tag in ("activity", "activity-alias", "service", "receiver", "provider"):
        for c in (app.findall(tag) if app is not None else []):
            filters = c.findall("intent-filter")
            schemes = sorted({dd.get(_ANDROID_NS + "scheme") for f in filters for dd in f.findall("data")
                              if dd.get(_ANDROID_NS + "scheme")})
            exported = c.get(_ANDROID_NS + "exported")
            facts["components"].append({
                "type": tag,
                "name": c.get(_ANDROID_NS + "name"),
                # Android default: exported=true when an intent-filter is present and not set explicitly.
                "exported": (exported == "true") if exported is not None else bool(filters),
                "exported_explicit": exported,
                "intent_filters": len(filters),
                "deep_link_schemes": schemes,
            })
    return facts
