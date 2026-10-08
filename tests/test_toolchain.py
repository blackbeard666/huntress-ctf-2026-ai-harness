"""Toolchain check (hctf/toolchain.py): detection, runtime install of a missing preferred tool, gap log + review.
Offline: the install path runs a stub recipe into a temp dir (never touches bin/ or the network).

Run:  source bin/env.sh && python3 tests/test_toolchain.py      (exit 0 = all pass)
"""
import io
import json
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from hctf import toolchain as tc  # noqa: E402

d = Path(tempfile.mkdtemp())
(d / "app.elf").write_bytes(b"\x7fELF" + b"\0" * 64 + b"__swift5_protocols" + b"\0" * 32 + b"$s13HuntressDay08")
(d / "rusty.elf").write_bytes(b"\x7fELF" + b"\0" * 64 + b"/rustc/" + b"a" * 40 + b"/library/core")
(d / "frozen.exe").write_bytes(b"MZ" + b"\0" * 100 + b"MEI\x0c\x0b\x0a\x0b\x0e" + b"\0" * 20)
(d / "bundle.hbc").write_bytes(b"\xc6\x1f\xbc\x03" + b"\0" * 60)
buf = io.BytesIO()
with zipfile.ZipFile(buf, "w") as z:
    z.writestr("AndroidManifest.xml", b"x")
    z.writestr("classes.dex", b"dex\n035\0")
    z.writestr("lib/arm64-v8a/libapp.so", b"x")
(d / "flutter.apk").write_bytes(buf.getvalue())
(d / "plain.txt").write_text("hello world, nothing compiled here\n")
found = tc.detect(sorted(d.iterdir()))
assert found.get("swift") == ["app.elf"], found
assert found.get("rust") == ["rusty.elf"] and "rust" not in [k for k, v in found.items() if "app.elf" in v and k == "rust"]
assert found.get("pyinstaller") == ["frozen.exe"] and found.get("hermes") == ["bundle.hbc"]
assert "flutter.apk" in found.get("flutter", []) and "flutter.apk" in found.get("android", [])
assert not any("plain.txt" in v for v in found.values())
print("ok  detect: Swift / Rust / PyInstaller / Hermes / Flutter+Android, nothing on plain text")

# scan order: a binary at the top level is scanned even when an extracted jar holds thousands of classes
ex = Path(tempfile.mkdtemp()) / "extracted"
(ex / "evidence" / "d07--variant-000.jar.extracted" / "kotlin").mkdir(parents=True)
for i in range(600):
    (ex / "evidence" / "d07--variant-000.jar.extracted" / "kotlin" / f"C{i:04d}.class").write_bytes(b"\xca\xfe\xba\xbe")
(ex / "evidence" / "d08--variant-000.elf").write_bytes((d / "app.elf").read_bytes())
order = tc.scan_order(ex)
assert len(order) == 400 and order[0].name == "d08--variant-000.elf", order[:2]
assert "swift" in tc.detect(order)
print("ok  scan_order: shallow binaries before thousands of extracted .class files (D8 Swift ELF was #3146)")

# runtime install of a missing preferred tool via a stub recipe (temp recipe dir, temp bin on the search path)
tmp = Path(tempfile.mkdtemp())
rec, binp = tmp / "recipes", tmp / "bin"
rec.mkdir()
binp.mkdir()
(rec / "swift-demangle.sh").write_text(f"#!/usr/bin/env bash\nsleep 1\nprintf '#!/bin/sh\\necho demangled\\n' > {binp}/swift-demangle\n"
                                       f"chmod +x {binp}/swift-demangle\n")
saved = (tc.RECIPES, tc.STATE, tc.GAPS, tc._path)
tc.RECIPES, tc.STATE, tc.GAPS = rec, tmp / "state", tmp / "gaps.jsonl"
tc._path = lambda: f"{binp}:/usr/bin:/bin"          # nothing else on the path: swift-demangle is MISSING
try:
    lines = tc.check([d / "app.elf"], cid="binary-reverse-engineering-day-09-x", log=lambda *a: None)
    text = "\n".join(lines)
    assert "Swift" in text and "INSTALLING now" in text and "hctf tool-wait swift-demangle" in text, text
    assert tc.status("swift-demangle")["state"] == "installing"
    assert tc.wait("swift-demangle", timeout=30) == "installed"
    assert tc.status("swift-demangle")["state"] == "installed" and tc.have("swift-demangle")
    # second check: present now, nothing new logged for it
    n_before = len(tc.GAPS.read_text().splitlines())
    assert "INSTALLING" not in "\n".join(tc.check([d / "app.elf"], cid="x", log=lambda *a: None))
    assert len(tc.GAPS.read_text().splitlines()) == n_before
    # a toolchain whose tool has NO recipe is flagged (not silently skipped) and reported for the post-run review
    text = "\n".join(tc.check([d / "flutter.apk"], cid="mobile-android-day-09-y", install_missing=True, log=lambda *a: None))
    assert "blutter" in text and "no install recipe" in text, text
    gaps = [json.loads(x) for x in tc.GAPS.read_text().splitlines()]
    assert {g["tool"] for g in gaps} >= {"swift-demangle", "blutter"} and all(g["day"] == 9 for g in gaps), gaps
    rep = tc.report(day=9)
    assert "swift-demangle" in rep and "present now" in rep and "blutter" in rep and "ADD setup/tools/blutter.sh" in rep, rep
finally:
    tc.RECIPES, tc.STATE, tc.GAPS, tc._path = saved
print("ok  missing preferred tool: installed in the background, worker told to tool-wait; no-recipe gap flagged + reviewed")

# description hints: toolchains named in the text, lane-scoped cues, no "intent" -> Android noise in script prompts
tt = tc.text_toolchains
assert "swift" in tt("Swift binaries speak in protocols") and "msvc_cpp" in tt("C++ on Windows. RTTI is your Rosetta Stone")
assert "go" in tt("Go binaries are chatty") and "go" not in tt("go fish them out and go home")
assert "android" not in tt("Classify each script's intent") and "android" in tt("an exported deep-link Activity")
assert "pyinstaller" in tt("bytecode, wheels, zipapps, frozen executables")
cs = tc.cues
assert any("base64" in i for i in cs("I hear sixty-four is a good base.", "warmups-day-01"))
assert not any("riddle" in i for i in cs("Six Bash behavior graphs ... eight", "script-analysis-day-06-x"))
assert any("network IOCs" in i for i in cs("see where this one phones home", "binary-x"))
assert any("static analysis only" in i for i in cs("none of which will ever run", "script-analysis-x"))
assert any("EARLIER days" in i for i in cs("Carry your PowerShell findings forward", "script-analysis-x"))
# cross-check: description + bytes agree / description only (packed?) / cues section; prefetch installs from text alone
tmp2 = Path(tempfile.mkdtemp())
(tmp2 / "recipes").mkdir()
(tmp2 / "bin").mkdir()
(tmp2 / "recipes" / "swift-demangle.sh").write_text(f"#!/usr/bin/env bash\nprintf '#!/bin/sh\\n' > {tmp2}/bin/swift-demangle\n"
                                                    f"chmod +x {tmp2}/bin/swift-demangle\n")
saved = (tc.RECIPES, tc.STATE, tc.GAPS, tc._path)
tc.RECIPES, tc.STATE, tc.GAPS = tmp2 / "recipes", tmp2 / "state", tmp2 / "gaps.jsonl"
tc._path = lambda: f"{tmp2}/bin:/usr/bin:/bin"
try:
    got = tc.prefetch("Swift Justice", cid="binary-reverse-engineering-day-09-z", log=lambda *a: None)
    assert got["swift"][0][1] in ("installing", "installed") and tc.wait("swift-demangle", 30) == "installed"
    text = "\n".join(tc.check([d / "app.elf"], cid="binary-x", text="Swift binaries; see where it phones home",
                               log=lambda *a: None))
    assert "description (swift) + bytes confirm" in text and "network IOCs" in text, text
    text = "\n".join(tc.check([d / "plain.txt"], cid="binary-x", text="Rust leaves fingerprints", log=lambda *a: None))
    assert "NO byte markers" in text and "Rust" in text, text
finally:
    tc.RECIPES, tc.STATE, tc.GAPS, tc._path = saved
print("ok  description hints: toolchains + lane-scoped cues; prefetch installs from the name alone; bytes cross-check")

# every shipped recipe is named after a tool some toolchain prefers (so triage can actually trigger it)
wanted = {t for _i, _l, _d, tools, _h in tc.TOOLCHAINS for t in tools}
for r in (ROOT / "setup" / "tools").glob("*.sh"):
    if r.stem != "_lib":
        assert r.stem in wanted, f"recipe {r.name} is not a preferred tool of any toolchain"
print("ok  recipes map to toolchain tools")
print("ALL PASS")
