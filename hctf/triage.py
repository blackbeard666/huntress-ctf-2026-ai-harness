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


_LANG_PREFIXES = {"python", "py", "jscript", "js", "javascript", "batch", "bat", "cmd", "vbscript", "vbs", "bash", "sh",
                  "powershell", "ps", "ps1", "perl", "ruby", "php", "lua", "go", "applescript", "autoit", "hta", "wsf"}


def _family_table(contract, conf):
    """One row per answer-id family (e.g. `bash-chain`, `d04_analysis`): field suffixes, count, a sample question,
    format kinds -- instead of 399 one-line questions."""
    import re as _re
    fams = {}
    for aid, q in zip(contract.get("answer_ids", []), contract.get("questions", [])):
        m = _re.match(r"((?:set\d+\.)?d\d+_[a-z]+)_(.*)", aid)          # binary: d04_analysis_machine
        if m:
            fam, field = m.group(1), m.group(2)
        elif "-" in aid:
            # script: <language>-<fixture>-<field...> (bash-chain-stage-count) or Day-1 <scenario>-<field> (resource-url)
            toks = aid.split("-")
            n = 2 if toks[0].split(".")[-1] in _LANG_PREFIXES and len(toks) > 2 else 1
            fam, field = "-".join(toks[:n]), "-".join(toks[n:])
        else:
            fam, field = aid, ""
        f = fams.setdefault(fam, {"fields": [], "kinds": set(), "q": q.get("question", ""), "left": 0})
        f["fields"].append(field)
        f["kinds"].add((q.get("answer_format") or {}).get("kind") or "?")
        f["left"] += aid not in conf
    rows = [f"**{len(contract.get('answer_ids', []))} answers in {len(fams)} families** (family | fields | open | kinds | sample question):", ""]
    for fam, f in fams.items():
        rows.append(f"- `{fam}` | {', '.join(dict.fromkeys(f['fields']))[:120]} | {f['left']} open | "
                    f"{'/'.join(sorted(f['kinds']))} | {f['q'][:110]}")
    return rows + ["", "_(full questions + answer_format per id: `jq '.questions[]' contract.json`)_", ""]


def _sh(args, timeout=8):
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
        return (r.stdout or "").strip()
    except Exception:  # noqa: BLE001
        return ""


def _recon(cid, root):
    """Standard-tool recon of the extracted members, per lane (recon, never answers): what each file is and where the
    interesting bytes sit, so the worker's first turn starts from tool output instead of orientation turns."""
    import re as _re
    import shutil as _shutil
    if not root.exists():
        return []
    files = sorted(p for p in root.rglob("*") if p.is_file())[:80]
    lines = []
    if cid.startswith("script-analysis"):
        lang = {".ps1": "PowerShell", ".js": "JScript", ".jse": "JScript", ".bat": "Batch", ".cmd": "Batch",
                ".vbs": "VBScript", ".vbe": "VBScript", ".py": "Python", ".pyc": "Python bytecode", ".sh": "Bash"}
        for f in files:
            l = lang.get(f.suffix.lower())
            if not l:
                continue
            hits = _sh(["grep", "-n", "-a", "-E", "-m", "4", "(Codec|CODEC|Material|MATERIAL)", str(f)])
            hits = " ; ".join(h.strip()[:150] for h in hits.splitlines()[:4])
            lines.append(f"- `{f.relative_to(root)}` [{l}, {f.stat().st_size} B] {hits}")
    elif cid.startswith("binary-reverse-engineering"):
        for f in files:
            ft = _sh(["file", "-b", str(f)])[:110]
            sha = _sh(["sha256sum", str(f)]).split(" ")[0]
            row = [f"- `{f.relative_to(root)}` {f.stat().st_size} B | {ft} | sha256 {sha}"]
            if ft.startswith("ELF"):
                hdr = _sh(["readelf", "-hW", str(f)])
                keep = [l.split(":", 1)[1].strip() for l in hdr.splitlines() if l.strip().split(":")[0] in ("Class", "Data", "Type", "Machine")]
                row.append(f"    readelf: {' | '.join(keep)}")
                if "Go BuildID" in ft or _sh(["go", "version", "-m", str(f)]).count("path"):
                    row.append("    go: " + " | ".join(_sh(["go", "version", "-m", str(f)]).splitlines()[:2])[:160])
            elif ft.startswith("PE32") and _shutil.which("rabin2"):
                info = _sh(["rabin2", "-I", str(f)])
                row.append("    rabin2: " + " | ".join(l.strip() for l in info.splitlines() if l.split()[:1] and l.split()[0] in ("arch", "bits", "class", "lang", "machine"))[:200])
            elif f.suffix == ".class" and _shutil.which("javap"):
                cp = _sh(["javap", "-v", "-p", str(f)])
                strs = [m.group(1) for m in _re.finditer(r"= Utf8\s+(\S{24,})", cp)][:4]
                row.append(f"    javap: {len(cp.splitlines())} lines; long Utf8 constants: {[x[:60] for x in strs]}")
            offs = _sh(["grep", "-boa", "HCFG", str(f)]).splitlines()[:3]
            for o in offs:
                off = o.split(":")[0]
                row.append(f"    HCFG @ {off}: " + _sh(["xxd", "-s", off, "-l", "16", str(f)])[:80])
            lines += row
    return (["", "## Recon (standard tools, pre-run for you -- facts, not answers)", ""] + lines) if lines else []


def _extract_all(files, dest, depth=2):
    """Unpack every zip artifact (password-protected and nested too) into `dest` so the worker starts on the members
    instead of spending turns on unzip / 7z password prompts (seen in 3 workers). Returns markdown lines."""
    import shutil
    import zipfile
    from lib.common import ZIP_PASSWORDS
    lines, todo = [], [(f, dest / f.stem, 0) for f in files if zipfile.is_zipfile(f)]
    while todo:
        z, out, lvl = todo.pop(0)
        out.mkdir(parents=True, exist_ok=True)
        ok, used = False, None
        for pw in [None, *ZIP_PASSWORDS]:
            args = ["7z", "x", "-y", f"-o{out}", f"-p{(pw or b'').decode()}", str(z)]
            if shutil.which("7z") and subprocess.run(args, capture_output=True, stdin=subprocess.DEVNULL,
                                                     timeout=60).returncode == 0:
                ok, used = True, pw
                break
        if not ok:
            lines.append(f"- could not extract `{z.name}` (unknown password?)")
            continue
        members = sorted(p for p in out.rglob("*") if p.is_file())
        pwtxt = f" (password `{used.decode()}`)" if used else ""
        lines.append(f"- `{z.name}`{pwtxt} -> `{out}`: {len(members)} file(s)")
        for m in members[:40]:
            lines.append(f"    - `{m.relative_to(out)}` ({m.stat().st_size} B)")
        if lvl + 1 < depth:
            todo += [(m, m.parent / (m.stem + "_x"), lvl + 1) for m in members if zipfile.is_zipfile(m)]
    return (["", "## Extracted (pre-unpacked for you -- read these instead of unzipping again)", ""] + lines) if lines else []


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
    if contract.get("guidance"):
        # Event-wide GM guidance: names the sanctioned transport (it CHANGED mid-event, proxy -> direct bearer) and
        # carries the untrusted-data / work-from-downloaded-bytes / exact-answer_ids / no-cross-identity-flags rules.
        out += ["**GM guidance (event-wide — note the sanctioned transport and the untrusted-data rule):**",
                f"> {str(contract['guidance']).strip()}", ""]
    qn = len(contract.get("answer_ids", []))
    conf = cli.confirmed_answers(cid) if qn else {}
    if qn:
        # STATUS first: workers spent 1-11 jq calls (some failing on the schema) working out what is left to do.
        left = [a for a in contract.get("answer_ids", []) if a not in conf]
        out += [f"## STATUS: {len(conf)}/{qn} answers already accepted by the GM (see confirmed.json) -- "
                f"{len(left)} REMAINING", ""]
        if conf and left:
            out += ["Work ONLY on these answer_ids:", "", "`" + "`, `".join(left[:200]) + "`" + (" ..." if len(left) > 200 else ""), ""]
    if qn > 60:
        out += _family_table(contract, conf)
    elif qn:
        out.append(f"**{qn} answer(s) expected.** Formats (remaining fields only):" if conf else
                   f"**{qn} answer(s) expected.** Formats:")
        for aid, q in zip(contract.get("answer_ids", []), contract.get("questions", [])):
            if aid in conf:
                continue
            fmt = q.get("answer_format", {})
            syn = fmt.get("syntax") or (f"one of {fmt.get('accepted_values')}" if fmt.get("accepted_values") else "")
            out.append(f"- `{aid}`: {q.get('question', '')[:110]}  _(fmt: {str(syn)[:80]}; norm: {q.get('normalization')})_")
        out.append("")
    out += ["## Artifacts", ""]
    for f in files:
        out += _describe(f)
    out += _extract_all(files, mdir / "work" / "extracted")
    try:
        out += _recon(cid, mdir / "work" / "extracted")
    except Exception as e:  # noqa: BLE001 - recon is best-effort
        out += ["", f"_recon skipped: {e}_"]
    out += ["", "_Deterministic triage (no LLM). Verify against the bytes; see the routed lane skill._"]
    (mdir / "triage.md").write_text("\n".join(out), encoding="utf-8")
    return mdir / "triage.md"
