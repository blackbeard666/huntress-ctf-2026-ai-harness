"""Advanced binary-RE helpers — the hardening layer on top of lib/elf.py's header/symbol reads.

Covers what the audit flagged as missing: packer detection + UPX unpacking, stripped-Go function-name
recovery from .gopclntab (names survive stripping there), Mach-O facts (lief), robust constant recovery via
capstone disassembly (replacing the fragile `b8..c3` byte regex), and a Ghidra headless decompile helper
(now that JDK 21 is wired). Everything is static. Pure-stdlib + capstone/lief/pyelftools from the venv.
"""
import io
import math
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

GHIDRA_SCRIPT = Path(__file__).resolve().parent / "ghidra_scripts" / "DecompileDump.java"


# --- packing -------------------------------------------------------------------------------------
def entropy(data):
    """Shannon entropy (bits/byte, 0-8). Packed/encrypted payloads sit ~7.8+; normal code ~5-6.5."""
    if not data:
        return 0.0
    freq = [0] * 256
    for b in data:
        freq[b] += 1
    n = len(data)
    return -sum((c / n) * math.log2(c / n) for c in freq if c)


def packer_info(data):
    """Detect packing. Returns {packer, entropy, packed(bool)}. Catches UPX by magic and anything else by
    high whole-file entropy (a gate before analysis — a packed binary's symbols/sections are meaningless)."""
    e = round(entropy(data), 2)
    packer = None
    if b"UPX!" in data[:4096] or b"UPX0" in data or b"UPX1" in data:
        packer = "upx"
    elif b"PEtite" in data[:4096]:
        packer = "petite"
    elif b"ASPack" in data[:4096]:
        packer = "aspack"
    packed = bool(packer) or e >= 7.2
    return {"packer": packer, "entropy": e, "packed": packed}


def unpack_upx(path):
    """Unpack a UPX binary to a sibling file, return its path (or the original if upx is absent/fails)."""
    if not shutil.which("upx"):
        return str(path)
    out = str(path) + ".unpacked"
    shutil.copy(path, out)
    r = subprocess.run(["upx", "-d", "-q", out], capture_output=True, timeout=120)
    return out if r.returncode == 0 else str(path)


# --- Go / Rust symbol recovery -------------------------------------------------------------------
def go_buildinfo(data):
    """Go version string from the `\\xff Go buildinf:` blob (present even when stripped), or None."""
    m = re.search(rb"go1\.\d+(\.\d+)?", data)
    return m.group(0).decode() if m else None


def go_pclntab_funcs(data, limit=4000):
    """Recover Go function names from .gopclntab — they survive symbol stripping. Version-agnostic: pulls
    the section (or scans for the pclntab magic) and extracts Go-symbol-shaped null-terminated strings
    (package-qualified: main.*, runtime.*, path/pkg.*). Returns a sorted de-duped list."""
    from elftools.elf.elffile import ELFFile
    blob = b""
    try:
        elf = ELFFile(io.BytesIO(data))
        for sname in (".gopclntab", ".data.rel.ro.gopclntab", ".data.rel.ro"):
            s = elf.get_section_by_name(sname)
            if s:
                blob += s.data()
    except Exception:  # noqa: BLE001 - not an ELF / no sections: fall back to a raw magic scan
        pass
    if not blob:
        for magic in (b"\xf0\xff\xff\xff", b"\xf1\xff\xff\xff", b"\xfa\xff\xff\xff", b"\xfb\xff\xff\xff"):
            i = data.find(magic)
            if i >= 0:
                blob = data[i:i + 4_000_000]
                break
    names = set()
    # Go symbol names: package-path-qualified, ASCII, contain a '.', may carry * ( ) [ ] / and digits.
    for m in re.finditer(rb"[A-Za-z_][\w./*()\[\]<>,;$-]{2,120}", blob):
        s = m.group(0)
        try:
            t = s.decode("ascii")
        except UnicodeDecodeError:
            continue
        if "." in t and ("/" in t or t.split(".")[0] in ("main", "runtime", "fmt", "os", "net", "sync",
                                                          "internal", "crypto", "encoding", "reflect")
                         or re.match(r"^[a-z][\w]*\.[A-Za-z]", t)):
            names.add(t)
    return sorted(names)[:limit]


def rustfilt(symbol):
    """Demangle a Rust v0/legacy symbol if `rustfilt` is on PATH, else return it unchanged."""
    if not shutil.which("rustfilt"):
        return symbol
    r = subprocess.run(["rustfilt"], input=symbol, capture_output=True, text=True, timeout=10)
    return r.stdout.strip() or symbol


# --- Mach-O --------------------------------------------------------------------------------------
def macho_facts(data):
    """Header facts for a Mach-O (fat or thin) via lief: cpu type, file type, flags, dylibs, entry. {} if
    not a Mach-O or lief missing. Closes the lane's Mach-O gap (previously facts() returned {})."""
    try:
        import lief
    except ImportError:
        return {}
    try:
        fat = lief.MachO.parse(raw=list(data))
    except Exception:  # noqa: BLE001
        return {}
    if fat is None or fat.size == 0:
        return {}
    b = fat.at(0)
    h = b.header
    return {
        "format": "mach-o",
        "cpu_type": str(h.cpu_type).split(".")[-1].lower(),
        "file_type": str(h.file_type).split(".")[-1].lower(),
        "nb_cmds": h.nb_cmds,
        "pie": bool(h.has(lief.MachO.Header.FLAGS.PIE)) if hasattr(h, "has") else None,
        "libraries": [lib.name for lib in b.libraries][:40],
        "entrypoint": hex(b.entrypoint) if hasattr(b, "entrypoint") else None,
    }


# --- robust constant recovery (replaces the fragile b8..c3 regex) --------------------------------
def recover_return_constants(data, max_funcs=400):
    """Find functions that return an immediate constant, via capstone linear disassembly from the ELF's
    symbol/section entry points — robust where the old `\\xb8(.{4})\\xc3` whole-.text regex went ambiguous.
    Returns {addr: const} for `mov eax/rax, imm; ret` leaves. Works stripped (scans .text) and unstripped."""
    try:
        import capstone
        from elftools.elf.elffile import ELFFile
    except ImportError:
        return {}
    try:
        elf = ELFFile(io.BytesIO(data))
    except Exception:  # noqa: BLE001
        return {}
    text = elf.get_section_by_name(".text")
    if not text:
        return {}
    code, base = text.data(), text["sh_addr"]
    bits = 64 if elf.elfclass == 64 else 32
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64 if bits == 64 else capstone.CS_MODE_32)
    out = {}
    last_imm = None
    last_addr = None
    for ins in md.disasm(code, base):
        if ins.mnemonic == "mov" and ins.op_str.split(",")[0].strip() in ("eax", "rax", "al", "ax"):
            m = re.search(r",\s*(?:0x[0-9a-fA-F]+|\d+)$", ins.op_str)
            if m:
                last_imm = int(m.group(0).lstrip(", ").strip(), 0)
                last_addr = ins.address
        elif ins.mnemonic == "ret" and last_imm is not None and last_addr is not None:
            out[hex(last_addr)] = last_imm
            last_imm = last_addr = None
            if len(out) >= max_funcs:
                break
        elif ins.mnemonic not in ("nop",):
            # only a mov-imm immediately followed by ret counts as a return-constant leaf
            if ins.mnemonic != "mov":
                last_imm = last_addr = None
    return out


# --- Ghidra headless decompile -------------------------------------------------------------------
def ghidra_decompile(path, timeout=300):
    """Decompile every function with Ghidra headless (JDK 21 wired in launch.properties) and return the C
    text. Empty string on failure. Heavy (~minutes) — use only when symbol/pattern reads don't suffice."""
    headless = Path(__file__).resolve().parents[1] / "bin" / "analyzeHeadless"
    if not headless.exists() or not GHIDRA_SCRIPT.exists():
        return ""
    with tempfile.TemporaryDirectory() as proj, tempfile.NamedTemporaryFile(suffix=".c") as outf:
        # Output must live OUTSIDE the project dir: -deleteProject wipes the project tree on exit.
        subprocess.run(
            [str(headless), proj, "P", "-import", str(path), "-scriptPath", str(GHIDRA_SCRIPT.parent),
             "-postScript", GHIDRA_SCRIPT.name, outf.name, "-deleteProject"],
            capture_output=True, text=True, timeout=timeout)
        return Path(outf.name).read_text(errors="replace")
