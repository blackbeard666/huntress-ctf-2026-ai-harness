"""Deterministic, no-LLM triage of a challenge's downloaded artifacts -> <mode dir>/triage.md.

Grounds the worker in real file facts (types, sizes, hashes, embedded structure, encoding guesses) and
routes to the right lane skill, so the agent doesn't burn turns rediscovering what `file`/exiftool already know.
"""
import hashlib
import json
import re
import shutil
import subprocess
import zipfile
from pathlib import Path

from . import cli, paths

TEXT_EXrE = re.compile(rb"[^\x09\x0a\x0d\x20-\x7e]")


def _run(cmd, **kw):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=60, **kw).stdout.strip()
    except Exception:
        return ""


def _sig(data):
    """Cheap signature guesses from the first bytes / content."""
    s = []
    head = data[:64]
    checks = [
        (b"\x7fELF", "ELF binary -> $binary-re"),
        (b"MZ", "PE/DOS (Windows exe/dll) -> $binary-re"),
        (b"\xca\xfe\xba\xbe", "Mach-O/Java-class -> $binary-re"),
        (b"PK\x03\x04", "ZIP/APK/JAR/OOXML container"),
        (b"dex\n", "Android DEX -> $mobile-android"),
        (b"\x1f\x8b", "gzip"),
        (b"BZh", "bzip2"),
        (b"\xfd7zXZ", "xz"),
        (b"%PDF", "PDF -> $metadata-forensics"),
        (b"\x89PNG", "PNG image -> $metadata-forensics"),
        (b"\xff\xd8\xff", "JPEG image -> $metadata-forensics"),
        (b"\xd0\xcf\x11\xe0", "OLE/Office doc -> $metadata-forensics"),
        (b"Rar!", "RAR archive"),
        (b"7z\xbc\xaf", "7z archive"),
    ]
    for magic, label in checks:
        if head.startswith(magic):
            s.append(label)
    if b".NET" in data[:4096] or b"mscoree" in data[:8192].lower():
        s.append(".NET assembly -> $binary-re (ilspycmd)")
    if b"<manifest" in data[:8192] or b"AndroidManifest" in data[:8192]:
        s.append("AndroidManifest -> $mobile-android")
    return s


def _text_signals(text):
    """Script/obfuscation/encoding markers in text content."""
    out = []
    low = text.lower()
    marks = {
        "powershell / .ps1 -> $script-analysis": ("invoke-expression", "frombase64string", "-encodedcommand", "[system.", "new-object"),
        "javascript -> $script-analysis": ("function(", "eval(", "=>", "require(", "document."),
        "vbscript/wsh -> $script-analysis": ("createobject", "wscript.", "execute "),
        "batch -> $script-analysis": ("@echo off", "%comspec%", "setlocal"),
    }
    for label, needles in marks.items():
        if sum(n in low for n in needles) >= 2:
            out.append(label)
    # encodings (warmups-ish)
    compact = re.sub(r"\s+", "", text)
    if compact:
        if re.fullmatch(r"[A-Za-z0-9+/=]+", compact) and len(compact) % 4 == 0 and len(compact) > 16:
            out.append("looks base64 -> $warmups")
        elif re.fullmatch(r"[A-Z2-7=]+", compact) and len(compact) > 16:
            out.append("looks base32 -> $warmups")
        elif re.fullmatch(r"(?:[0-9a-fA-F]{2})+", compact) and len(compact) > 16:
            out.append("looks hex -> $warmups")
    for ioc, rx in (("URLs", r"https?://[^\s'\"<>]+"), ("IPs", r"\b\d{1,3}(?:\.\d{1,3}){3}\b"),
                    ("ATT&CK IDs", r"\bT\d{4}(?:\.\d{3})?\b"), ("flags", r"flag\{[0-9a-f]{32}\}")):
        hits = re.findall(rx, text)
        if hits:
            out.append(f"{ioc}: {sorted(set(hits))[:5]}")
    return out


def _describe(path, depth=0, maxdepth=2):
    lines = []
    data = path.read_bytes()
    ind = "  " * depth
    ftype = _run(["file", "-b", str(path)])
    sha = hashlib.sha256(data).hexdigest()
    lines.append(f"{ind}- **{path.name}** ({len(data)} bytes) sha256 `{sha[:16]}…`")
    lines.append(f"{ind}  - file: {ftype}")
    for s in _sig(data):
        lines.append(f"{ind}  - signature: {s}")
    # text sample
    sample = data[:4096]
    if sample and len(TEXT_EXrE.findall(sample)) < len(sample) * 0.1:
        text = data.decode("utf-8", "replace")
        for sig in _text_signals(text):
            lines.append(f"{ind}  - {sig}")
        lines.append(f"{ind}  - preview: `{text[:160].strip()[:160]}`")
    # exiftool for media/office/pdf
    if any(path.suffix.lower() == e for e in (".pdf", ".png", ".jpg", ".jpeg", ".docx", ".xlsx", ".doc", ".tiff")):
        meta = _run(["exiftool", "-s", "-G", str(path)])
        if meta:
            lines.append(f"{ind}  - exiftool:\n" + "\n".join(f"{ind}      {l}" for l in meta.splitlines()[:25]))
    # recurse into zip/apk
    if zipfile.is_zipfile(path) and depth < maxdepth:
        try:
            with zipfile.ZipFile(path) as z:
                names = z.namelist()
                lines.append(f"{ind}  - archive with {len(names)} entries: {names[:12]}")
                is_apk = any(n == "AndroidManifest.xml" for n in names)
                if is_apk:
                    lines.append(f"{ind}  - **APK** -> $mobile-android (droidasc getmanifest / findrefs / getclass)")
                extract = [n for n in names if not n.endswith("/")][:8]
                tmp = paths.TMP / f"triage-{path.stem}-{depth}"
                if tmp.exists():
                    shutil.rmtree(tmp)
                tmp.mkdir(parents=True)
                for n in extract:
                    try:
                        dst = tmp / Path(n).name
                        dst.write_bytes(z.read(n))
                        if not is_apk:  # don't recurse the whole APK; the skill drives that
                            lines += _describe(dst, depth + 1, maxdepth)
                    except Exception:
                        pass
        except Exception as e:
            lines.append(f"{ind}  - (zip read error: {e})")
    return lines


def triage(cid):
    """Write <mode dir>/triage.md from the latest downloaded artifacts. Returns the path or None."""
    mdir = cli.cdir(cid)
    latest = mdir / "artifacts" / "latest"
    if not latest.exists():
        return None
    files = sorted(p for p in latest.iterdir() if p.is_file() and p.name != "manifest.json")
    contract = cli.load(cid, "start.json") or cli.load(cid, "contract.json") or {}
    out = [f"# Triage: {cid}", ""]
    if contract.get("prompt"):
        out += [f"**Prompt:** {contract['prompt']}", ""]
    qn = len(contract.get("answer_ids", []))
    if qn:
        out.append(f"**{qn} answer(s) expected.** Formats:")
        for aid, q in zip(contract.get("answer_ids", []), contract.get("questions", [])):
            fmt = q.get("answer_format", {})
            syn = fmt.get("syntax") or (f"one of {fmt.get('accepted_values')}" if fmt.get("accepted_values") else "")
            out.append(f"- `{aid}`: {q.get('question', '')[:110]}  _(fmt: {str(syn)[:80]}; norm: {q.get('normalization')})_")
        out.append("")
    out += ["## Artifacts", ""]
    for f in files:
        out += _describe(f)
    out += ["", "_Deterministic triage (no LLM). Verify against the bytes; see the routed lane skill._"]
    (mdir / "triage.md").write_text("\n".join(out), encoding="utf-8")
    return mdir / "triage.md"
