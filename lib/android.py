"""Android/APK analysis helpers for the mobile lane.

Before this, each mobile solver was a copy-pasted *JSON reader*: it pulled assets/huntress_puzzle.json and
regex'd the answer, never touching the dex/manifest/resources — so it broke the instant the answer moved,
with zero obfuscation. This module is the robust fallback chain:

    extract_answer(apk):  puzzle-json decode  ->  raw scan of every zip entry  ->  dex strings  ->
                          apktool (manifest/resources/smali)  ->  jadx (decompiled sources)

plus manifest_facts() for the exported-component / deep-link / allowBackup questions the lane actually asks.
Tools (apktool, jadx) are on PATH via bin/env.sh; each stage is best-effort with a timeout and degrades
gracefully if a tool is missing. Static only — we never install/run the APK.
"""
import base64
import binascii
import codecs
import json
import re
import subprocess
import xml.etree.ElementTree as ET
import zipfile
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
    s = str(key)
    if re.fullmatch(r"\d+", s):
        return bytes([int(s) & 0xFF])
    return s.encode("utf-8") or b"\x00"


def decode_payload(codec, data, key=None):
    """Decode a huntress_puzzle.json payload by its declared codec: plain/split, xor (base64 + repeating key), base64,
    base32, hex, rot13, reverse, caesar (every char's code point shifted by key). Unknown codec -> data unchanged."""
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
    out = []
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
    return [c for c in out if c]


# --- fallback scans (dex / resources / decompiled code) ------------------------------------------
def raw_entry_scan(apk):
    """Every zip entry's bytes, scanned for a literal ANS token (plaintext-anywhere fallback)."""
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
    return hits


def dex_strings(apk):
    """ANS tokens from the UTF-8 string pool of every classes*.dex (handles multidex, renamed code)."""
    hits = []
    try:
        with zipfile.ZipFile(apk) as z:
            for n in z.namelist():
                if re.fullmatch(r"classes\d*\.dex", Path(n).name):
                    hits += [m.decode() for m in ANS_RE_B.findall(z.read(n))]
    except (OSError, zipfile.BadZipFile):
        pass
    return hits


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
    puzzle json -> raw zip-entry scan -> dex strings -> apktool/jadx decompiled scan. Returns the first
    ANS-<16 hex> found (via the decoders + a direct token scan), or None. Order favours speed; the later
    stages cover an answer that was moved into the dex/resources/code (even with renaming)."""
    for cand in puzzle_candidates(apk):
        m = ANS_RE_T.search(cand)
        if m:
            return m.group(0)
    for stage in (raw_entry_scan, dex_strings, decompiled_scan):
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
