"""Toolchain check: what built each artifact, which standard tool handles that best, and is it installed?

Day 8 binary was a Swift ELF (`swift5_*` sections, `$s...` symbols) and we had no Swift demangler: the worker probed
`swift-demangle --version`, found nothing and fell back to nm/strings. Policy (user, 2026-10-08): when the PREFERRED
tool is missing, install it -- spending the time beats a weaker fallback. Triage calls check() on the extracted
members: present tools are named for the worker, missing ones with a recipe (setup/tools/<tool>.sh) are installed in
the BACKGROUND right away (the worker is told; `hctf tool-wait <tool>` blocks until it lands), missing ones without a
recipe are flagged. Every finding goes to .run/tool-gaps.jsonl; `hctf tool-gaps` is the post-run review (appended to
.run/dayNN.log by bin/day.sh) so anything that could not be installed gets a recipe before the next drop.
"""
import fcntl
import json
import os
import re
import shutil
import subprocess
import threading
import time
import zipfile
from pathlib import Path

from . import paths

ROOT = paths.ROOT
RECIPES = ROOT / "setup" / "tools"
STATE = ROOT / ".run" / "tool-installs"
GAPS = ROOT / ".run" / "tool-gaps.jsonl"
SCAN_BYTES = 96 << 20     # markers are searched in the first 96 MB of a member (the D8 Swift ELF is 67 MB)
_SEARCH_PATH = None


def _path():
    global _SEARCH_PATH
    if _SEARCH_PATH is None:
        _SEARCH_PATH = os.pathsep.join([str(ROOT / "bin"), str(ROOT / ".venv" / "bin"), str(ROOT / "tools" / "node" / "bin"),
                                        str(Path.home() / ".local" / "bin"), os.environ.get("PATH", "")])
    return _SEARCH_PATH


def have(tool):
    return shutil.which(tool, path=_path()) is not None


# (id, label, detector, preferred tools in order, what they give the worker). Detectors get (name, data, zip_names).
def _re(pat):
    rx = re.compile(pat)
    return lambda n, d, z: bool(rx.search(d))


def _bytes(*markers):
    return lambda n, d, z: any(m in d for m in markers)


def _member(*pats):
    rxs = [re.compile(p) for p in pats]
    return lambda n, d, z: any(r.search(x) for r in rxs for x in z)


TOOLCHAINS = [
    ("swift", "Swift", _bytes(b"swift5_protocols", b"__swift5_", b"swift5_typeref", b"libswiftCore"),
     ["swift-demangle"], "demangle `$s...`/`_T0...` symbols: `nm X | swift-demangle` or `swift-demangle '<sym>'`"),
    ("rust", "Rust", _re(rb"/rustc/[0-9a-f]{40}|_ZN[0-9A-Za-z_$.]+17h[0-9a-f]{16}E|_RNvCs[0-9A-Za-z_]{4,}"),
     ["rustfilt"], "demangle Rust symbols: `nm X | rustfilt`"),
    ("go", "Go", _bytes(b"\xff Go buildinf:", b"Go build ID:", b"runtime.gopanic"),
     ["GoReSym"], "recover Go symbols/types/build info: `GoReSym -t -d -p X`"),
    ("dotnet", ".NET", lambda n, d, z: d[:2] == b"MZ" and b"BSJB" in d,
     ["ilspycmd"], "decompile: `ilspycmd X` (or `ilspycmd -p -o out X`)"),
    ("jvm", "JVM bytecode (Java/Kotlin)", lambda n, d, z: d[:4] == b"\xca\xfe\xba\xbe" or n.endswith((".jar", ".class"))
     or any(x.endswith(".class") for x in z), ["jadx", "javap"], "decompile: `jadx -d out X`; constants: `javap -v -p`"),
    ("android", "Android APK/DEX", lambda n, d, z: d[:4] == b"dex\n" or "AndroidManifest.xml" in z or "classes.dex" in z,
     ["jadx", "apktool", "aapt"], "`jadx -d out X.apk`; manifest/resources: `apktool d X.apk`, `aapt dump badging`"),
    ("pyinstaller", "PyInstaller bundle", _bytes(b"MEI\x0c\x0b\x0a\x0b\x0e", b"pyi-runtime-tmpdir", b"_MEIPASS"),
     ["pyinstxtractor", "pycdc"], "unpack: `pyinstxtractor X`, then decompile the .pyc: `pycdc file.pyc`"),
    ("pyc", "Python bytecode", lambda n, d, z: n.endswith(".pyc") or (len(d) > 16 and d[2:4] == b"\r\n" and d[0] in range(0x40, 0x100)
     and n.endswith((".pyc", ".pyo"))), ["pycdc"], "`pycdc file.pyc` (any Python 3.x); `pycdas` for raw disassembly"),
    ("hermes", "React Native Hermes bytecode", lambda n, d, z: d[:4] == b"\xc6\x1f\xbc\x03" or
     "assets/index.android.bundle" in z, ["hbc-decompiler"], "`hbc-decompiler index.android.bundle out.js`"),
    ("flutter", "Flutter (Dart AOT)", _member(r"lib/[^/]+/libapp\.so$", r"libflutter\.so$"),
     ["blutter"], "Dart AOT snapshot in libapp.so: blutter recovers Dart symbols"),
    ("il2cpp", "Unity IL2CPP", _member(r"global-metadata\.dat$", r"libil2cpp\.so$"),
     ["Il2CppDumper"], "Il2CppDumper (libil2cpp.so + global-metadata.dat) -> class/method names"),
    ("electron", "Electron app.asar", lambda n, d, z: n.endswith(".asar") or any(x.endswith(".asar") for x in z),
     ["asar"], "`asar extract app.asar out/`"),
    ("autoit", "Compiled AutoIt", _bytes(b"AU3!EA06", b"AU3!EA05"), ["autoit-ripper"], "`autoit-ripper X out/`"),
    ("upx", "UPX-packed", _bytes(b"UPX!"), ["upx"], "unpack first: `upx -d -o unpacked X`"),
    ("nim", "Nim", _bytes(b"NimMain", b"nimFrame", b"@m..@s"), ["nim-demangle"], "Nim mangling: `name__<module>_<n>`"),
    ("delphi", "Delphi/Borland", _bytes(b"Embarcadero Delphi", b"Borland Delphi", b"FastMM Borland"),
     ["idr"], "Delphi RTTI/forms: IDR / DelphiHelper"),
    ("ole", "OLE/Office with macros", lambda n, d, z: d[:8] == b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" or "word/vbaProject.bin" in z
     or "xl/vbaProject.bin" in z, ["olevba"], "`olevba X` (macros, IOCs, deobfuscation)"),
    ("pdf", "PDF", lambda n, d, z: d[:5] == b"%PDF-", ["pdf-parser", "pdfid", "qpdf"],
     "`pdfid X`; objects/streams: `pdf-parser -a X`, `qpdf --qdf X out.pdf`"),
]


def _scan(path):
    try:
        with open(path, "rb") as f:
            data = f.read(SCAN_BYTES)
    except OSError:
        return b"", []
    names = []
    if data[:2] == b"PK":
        try:
            with zipfile.ZipFile(path) as z:
                names = z.namelist()[:20000]
        except (zipfile.BadZipFile, OSError, ValueError, RuntimeError):
            pass
    return data, names


def scan_order(root, cap=400):
    """Files under root worth scanning, shallow first and bytecode classes last, capped. A fat jar unpacks into
    thousands of .class files that sorted ahead of `d08--variant-000.elf`: replay d8tc1 scanned the first 400 paths
    and never saw the Swift binary."""
    root = Path(root)
    if not root.exists():
        return []
    return sorted((p for p in root.rglob("*") if p.is_file()),
                  key=lambda p: (p.suffix == ".class", len(p.relative_to(root).parts), str(p)))[:cap]


def detect(files):
    """{toolchain id: [file names]} for the given extracted members."""
    found = {}
    for p in files:
        p = Path(p)
        if not p.is_file() or p.stat().st_size < 16:
            continue
        data, names = _scan(p)
        for tid, _label, det, _tools, _hint in TOOLCHAINS:
            try:
                hit = det(p.name.lower(), data, names)
            except Exception:  # noqa: BLE001 - a detector must never break triage
                hit = False
            if hit:
                found.setdefault(tid, []).append(p.name)
    return found


# ------------------------------------------------------------------------------------------------- installs

def recipe(tool):
    r = RECIPES / f"{tool}.sh"
    return r if r.exists() else None


def _state_file(tool):
    return STATE / f"{tool}.json"


def status(tool):
    try:
        return json.loads(_state_file(tool).read_text())
    except (OSError, ValueError):
        return {}


def install(tool, background=True, log=print):
    """Run setup/tools/<tool>.sh once (file lock: one install per tool across processes). background=True returns at
    once; status(tool)["state"] goes installing -> installed | failed. Returns the state now."""
    if have(tool):
        return "present"
    r = recipe(tool)
    if not r:
        return "no_recipe"
    STATE.mkdir(parents=True, exist_ok=True)

    def run():
        lockf = open(STATE / f"{tool}.lock", "w")
        try:
            fcntl.flock(lockf, fcntl.LOCK_EX)
            if have(tool):
                _write(tool, state="installed", finished=time.time(), note="installed by another process")
                return
            t0 = time.time()
            _write(tool, state="installing", started=t0)
            p = subprocess.run(["bash", str(r)], cwd=ROOT, capture_output=True, text=True, timeout=900)
            global _SEARCH_PATH
            _SEARCH_PATH = None
            ok = p.returncode == 0 and have(tool)
            _write(tool, state="installed" if ok else "failed", started=t0, finished=time.time(),
                   seconds=round(time.time() - t0, 1), rc=p.returncode, tail=(p.stdout + p.stderr)[-600:])
            log(f"[toolchain] {tool}: {'installed' if ok else 'INSTALL FAILED'} in {time.time() - t0:.0f}s")
        except Exception as e:  # noqa: BLE001
            _write(tool, state="failed", finished=time.time(), tail=str(e)[-600:])
        finally:
            lockf.close()
    _write(tool, state="installing", started=time.time())
    if background:
        threading.Thread(target=run, daemon=True).start()
        return "installing"
    run()
    return status(tool).get("state", "failed")


def _write(tool, **kw):
    STATE.mkdir(parents=True, exist_ok=True)
    p = _state_file(tool)
    tmp = p.with_suffix(f".{os.getpid()}.tmp")
    tmp.write_text(json.dumps({"tool": tool, **kw}))
    tmp.replace(p)


def wait(tool, timeout=600):
    """Block until `tool` is on PATH or its install finished/failed. Returns the final state."""
    end = time.time() + timeout
    while time.time() < end:
        global _SEARCH_PATH
        _SEARCH_PATH = None
        if have(tool):
            return "installed"
        st = status(tool).get("state")
        if st in ("failed", None) and not recipe(tool):
            return "no_recipe"
        if st == "failed":
            return "failed"
        time.sleep(1)
    return "timeout"


def _gap(cid, tid, tool, state, files):
    GAPS.parent.mkdir(parents=True, exist_ok=True)
    m = re.search(r"day-?(\d+)", cid or "")
    with open(GAPS, "a") as f:
        f.write(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "day": int(m.group(1)) if m else None, "cid": cid,
                            "toolchain": tid, "tool": tool, "state": state, "files": files[:5]}) + "\n")


def check(files, cid="", install_missing=True, log=print):
    """Triage entry point: detect toolchains, make sure their preferred tools are there (start installs for missing
    ones), log every finding. Returns markdown lines for the triage summary ([] when nothing notable)."""
    found = detect(files)
    if not found:
        return []
    lines = ["", "## Toolchain check (what built these files -> the preferred standard tool)", ""]
    for tid, label, _det, tools, hint in TOOLCHAINS:
        if tid not in found:
            continue
        states = []
        for tool in tools:
            st = "present" if have(tool) else (install(tool, log=log) if install_missing else
                                               ("no_recipe" if not recipe(tool) else "missing"))
            if st != "present":
                _gap(cid, tid, tool, st, found[tid])
            states.append((tool, st))
        shown = ", ".join(f"`{t}`" + ("" if s == "present" else
                                      " (INSTALLING now -- run `hctf tool-wait " + t + "` before using it)" if s == "installing"
                                      else " (NOT available: no install recipe -- flagged for the post-run review)"
                                      if s == "no_recipe" else f" ({s})") for t, s in states)
        lines.append(f"- **{label}** in {', '.join(f'`{x}`' for x in found[tid][:4])}: use {shown} -- {hint}")
    lines.append("- Prefer the toolchain's own tool over a generic fallback; if one is installing, do other recon first "
                 "and `hctf tool-wait <tool>` when you need it (it returns as soon as the install lands).")
    return lines


def report(day=None):
    """Post-run review: every toolchain gap logged (for one day or all), latest state per tool."""
    rows = []
    try:
        for ln in GAPS.read_text().splitlines():
            r = json.loads(ln)
            if day is None or r.get("day") == day:
                rows.append(r)
    except (OSError, ValueError):
        pass
    if not rows:
        return "tool gaps: none logged" + (f" for day {day}" if day else "")
    latest = {}
    for r in rows:
        latest[r["tool"]] = r
    out = [f"tool gaps{f' (day {day})' if day else ''}: {len(latest)} tool(s)"]
    for tool, r in sorted(latest.items()):
        now = "present now" if have(tool) else (status(tool).get("state") or r["state"])
        need = "" if have(tool) else ("  -> ADD setup/tools/%s.sh and install before the next drop" % tool
                                      if not recipe(tool) else "  -> re-run setup/tools/%s.sh" % tool)
        out.append(f"  - {tool} ({r['toolchain']}, {r['cid']}): logged {r['state']}, {now}{need}")
    return "\n".join(out)


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("wait")
    w.add_argument("tool")
    w.add_argument("--timeout", type=int, default=600)
    r = sub.add_parser("report")
    r.add_argument("--day", type=int)
    c = sub.add_parser("check")
    c.add_argument("files", nargs="+")
    c.add_argument("--no-install", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd == "wait":
        st = wait(a.tool, a.timeout)
        print(f"{a.tool}: {st}")
        return 0 if st in ("installed", "present") else 1
    if a.cmd == "report":
        print(report(a.day))
        return 0
    print("\n".join(check(a.files, install_missing=not a.no_install)) or "no toolchain markers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
