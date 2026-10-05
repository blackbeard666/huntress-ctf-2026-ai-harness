"""Compiled-Python recovery for the script-analysis lane (armored/packed Python).

Days 1-5 scripting was inert fixtures, but a real day may ship a PyInstaller/frozen app or bare .pyc. This
recovers source: PyInstaller extraction (pyinstxtractor-ng) -> pyc decompilation (decompyle3) with a stdlib
`dis` disassembly fallback that ALWAYS works (so even modern-version bytecode that decompyle3 can't lift is
still readable). Static only — never runs the sample. For pyarmor with real bytecode encryption, decompilation
won't suffice (needs dynamic unpacking); flagged in reference/HARDENING.md.
"""
import dis
import importlib.util
import marshal
import subprocess
import sys
from pathlib import Path


def extract_pyinstaller(path, outdir=None):
    """Extract a PyInstaller executable with pyinstxtractor-ng. Returns the output dir, or None."""
    import shutil
    exe = shutil.which("pyinstxtractor-ng") or shutil.which("pyinstxtractor")
    if not exe:
        return None
    outdir = Path(outdir or (str(path) + "_extracted"))
    outdir.mkdir(parents=True, exist_ok=True)
    r = subprocess.run([exe, "-o", str(outdir), str(path)], capture_output=True, text=True, timeout=120,
                       cwd=str(outdir))
    # pyinstxtractor variants write to CWD or -o; return whichever has content
    for d in (outdir, Path(str(path) + "_extracted")):
        if d.exists() and any(d.rglob("*.pyc")):
            return str(d)
    return str(outdir) if r.returncode == 0 else None


def _load_code(pyc_path):
    """Load the code object from a .pyc, skipping the version-dependent header."""
    data = Path(pyc_path).read_bytes()
    for hdr in (16, 12, 8):  # 3.7+ = 16, older = 12/8
        try:
            return marshal.loads(data[hdr:])
        except Exception:  # noqa: BLE001
            continue
    return None


def decompile_pyc(pyc_path):
    """Return decompiled Python source for a .pyc via decompyle3; on failure, a stdlib `dis` disassembly
    (always available). Prefixed with the method used."""
    try:
        import decompyle3
        import io
        buf = io.StringIO()
        decompyle3.decompile_file(str(pyc_path), buf)
        src = buf.getvalue()
        if src.strip():
            return "# via decompyle3\n" + src
    except Exception:  # noqa: BLE001 - version unsupported / armored: fall back to disassembly
        pass
    code = _load_code(pyc_path)
    if code is None:
        return ""
    buf = []

    def _dis(c, depth=0):
        buf.append("%s# code: %s" % ("  " * depth, getattr(c, "co_name", "?")))
        try:
            buf.append(dis.Bytecode(c).dis())
        except Exception:  # noqa: BLE001
            pass
        for const in getattr(c, "co_consts", ()):
            if hasattr(const, "co_code"):
                _dis(const, depth + 1)
    _dis(code)
    return "# via dis (decompyle3 unavailable for this bytecode version)\n" + "\n".join(buf)


def recover_python(path):
    """Best-effort source recovery from a frozen app or a bare .pyc. Returns concatenated source/disasm text.
    PyInstaller -> extract then decompile the app's .pyc; a .pyc -> decompile directly."""
    p = Path(path)
    data = p.read_bytes()[:4]
    out = []
    if b"MZ" in data or b"\x7fELF" in data:  # a frozen executable
        d = extract_pyinstaller(path)
        if d:
            for pyc in Path(d).rglob("*.pyc"):
                if pyc.stat().st_size > 0:
                    out.append("### %s\n%s" % (pyc.name, decompile_pyc(pyc)))
    elif p.suffix == ".pyc" or data[:2] in (b"\x42\x0d", b"\x61\x0d") or importlib.util.MAGIC_NUMBER[:2] == data[:2]:
        out.append(decompile_pyc(path))
    return "\n\n".join(out)
