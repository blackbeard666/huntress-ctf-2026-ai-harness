"""Steganography + hidden-data + encrypted-container helpers for the metadata-forensics lane.

The lane's byte parsers are strong for declared fields but had nothing for HIDDEN data. This adds: LSB /
bit-plane extraction, trailing-data carving (bytes after a format's EOF marker), PNG text-chunk extraction
(incl. zTXt inflate) and non-standard-chunk flagging, binwalk/foremost carving wrappers, and a wordlist
cracker for encrypted zip/Office (we have pyzipper + msoffcrypto; the distro `john` lacks zip2john). Static.
"""
import re
import subprocess
import zlib
from pathlib import Path

CTF_WORDS = ["infected", "flare", "malware", "virus", "huntress", "password", "secret", "ctf",
             "admin", "letmein", "changeme", "1234", "huntressctf"]


# --- LSB / bit-plane stego -----------------------------------------------------------------------
def lsb_extract(path, planes=1):
    """Extract the low `planes` bit(s) of each RGB channel (row-major, MSB-first packing) and return the
    packed bytes. The flag/text usually falls out as a printable run near the start. Also try channel subsets
    with lsb_variants(). Returns b'' if PIL/numpy unavailable or not an image."""
    try:
        import numpy as np
        from PIL import Image
    except ImportError:
        return b""
    try:
        arr = np.array(Image.open(path).convert("RGB"))
    except Exception:  # noqa: BLE001
        return b""
    bits = []
    for p in range(planes):
        bits.append((arr[:, :, :3].reshape(-1) >> p) & 1)
    stream = np.empty(sum(len(b) for b in bits), dtype=np.uint8)
    # interleave planes per sample is uncommon; default: plane 0 full stream, then plane 1, ...
    off = 0
    for b in bits:
        stream[off:off + len(b)] = b
        off += len(b)
    n = (len(stream) // 8) * 8
    packed = np.packbits(stream[:n])
    return packed.tobytes()


def lsb_variants(path):
    """Several common LSB orderings -> bytes, so a solver can scan each for a printable/flag run.
    Returns {label: bytes}: per-channel R/G/B, all-RGB, and column-major all-RGB."""
    try:
        import numpy as np
        from PIL import Image
    except ImportError:
        return {}
    try:
        arr = np.array(Image.open(path).convert("RGB"))
    except Exception:  # noqa: BLE001
        return {}
    out = {}
    for idx, name in ((0, "R"), (1, "G"), (2, "B")):
        s = (arr[:, :, idx].reshape(-1) & 1)
        out[f"lsb-{name}"] = np.packbits(s[:(len(s) // 8) * 8]).tobytes()
    rgb = (arr[:, :, :3].reshape(-1) & 1)
    out["lsb-RGB"] = np.packbits(rgb[:(len(rgb) // 8) * 8]).tobytes()
    colmaj = (arr[:, :, :3].transpose(1, 0, 2).reshape(-1) & 1)
    out["lsb-RGB-col"] = np.packbits(colmaj[:(len(colmaj) // 8) * 8]).tobytes()
    return out


# --- trailing / appended data --------------------------------------------------------------------
_EOF = {b"\x89PNG\r\n\x1a\n": (b"IEND", 8), b"\xff\xd8\xff": (b"\xff\xd9", 2),
        b"GIF8": (b"\x00\x3b", 2), b"BM": (None, 0)}


def trailing_data(path):
    """Bytes appended after a format's logical EOF (classic hide-a-zip-after-the-PNG). b'' if none/unknown."""
    data = Path(path).read_bytes()
    for magic, (end, elen) in _EOF.items():
        if data.startswith(magic) and end:
            i = data.rfind(end)
            if i >= 0 and i + elen < len(data):
                return data[i + elen:]
    return b""


# --- PNG chunks ----------------------------------------------------------------------------------
def png_chunks(path):
    """List PNG chunks: [(type, length, is_standard)]. Non-standard/ancillary chunks can hide payloads."""
    data = Path(path).read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        return []
    std = {"IHDR", "PLTE", "IDAT", "IEND", "tRNS", "cHRM", "gAMA", "iCCP", "sBIT", "sRGB", "tEXt",
           "zTXt", "iTXt", "bKGD", "hIST", "pHYs", "sPLT", "tIME"}
    out, i = [], 8
    while i + 8 <= len(data):
        ln = int.from_bytes(data[i:i + 4], "big")
        typ = data[i + 4:i + 8].decode("latin-1")
        out.append((typ, ln, typ in std))
        i += 12 + ln
        if typ == "IEND":
            break
    return out


def png_text(path):
    """Decoded tEXt/zTXt/iTXt key->value pairs (zTXt inflated). Where GM/stego hide ASCII in a PNG."""
    data = Path(path).read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        return {}
    out, i = {}, 8
    while i + 8 <= len(data):
        ln = int.from_bytes(data[i:i + 4], "big")
        typ = data[i + 4:i + 8]
        body = data[i + 8:i + 8 + ln]
        try:
            if typ == b"tEXt" and b"\x00" in body:
                k, v = body.split(b"\x00", 1)
                out[k.decode("latin-1")] = v.decode("latin-1")
            elif typ == b"zTXt" and b"\x00" in body:
                k, rest = body.split(b"\x00", 1)
                out[k.decode("latin-1")] = zlib.decompress(rest[1:]).decode("latin-1", "replace")
            elif typ == b"iTXt" and b"\x00" in body:
                k = body.split(b"\x00", 1)[0]
                out[k.decode("latin-1")] = body.rsplit(b"\x00", 1)[-1].decode("utf-8", "replace")
        except Exception:  # noqa: BLE001
            pass
        i += 12 + ln
        if typ == b"IEND":
            break
    return out


# --- carving + cracking --------------------------------------------------------------------------
def carve(path, outdir=None):
    """Run binwalk extraction (if present) and return the list of carved file paths. For polyglots/embeds."""
    import shutil
    if not shutil.which("binwalk"):
        return []
    outdir = outdir or (str(path) + ".extracted")
    subprocess.run(["binwalk", "-e", "-q", "--directory", str(Path(outdir).parent), str(path)],
                   capture_output=True, timeout=120)
    d = Path(outdir)
    return [str(p) for p in d.rglob("*") if p.is_file()] if d.exists() else []


def crack_zip(path, words=None, extra_wordlist=None):
    """Try to open an encrypted zip with a wordlist (ZipCrypto + AES via pyzipper). Returns the password
    (str) or None. Covers the common CTF case without needing john/zip2john (absent on this box)."""
    try:
        import pyzipper
    except ImportError:
        return None
    cands = list(words or CTF_WORDS)
    if extra_wordlist and Path(extra_wordlist).exists():
        cands += Path(extra_wordlist).read_text(errors="replace").split()
    for pw in cands:
        for opener in (pyzipper.AESZipFile, pyzipper.ZipFile):
            try:
                with opener(path) as z:
                    z.pwd = pw.encode()
                    z.testzip()
                    return pw
            except Exception:  # noqa: BLE001 - wrong password / wrong cipher class
                continue
    return None


def printable_runs(data, minlen=6):
    """ASCII runs >= minlen from extracted bytes (LSB/carve output) — where a flag/answer surfaces."""
    return [m.decode("latin-1") for m in re.findall(rb"[\x20-\x7e]{%d,}" % minlen, data)]
