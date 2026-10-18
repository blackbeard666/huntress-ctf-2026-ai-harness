"""Independent oracle for the storage_* fixtures: locate the crc-valid HCFG with stdlib (bytes.find / re + base64 +
zlib.crc32), then the section holding its file offset with a THIRD-PARTY reader (pyelftools / pefile / macholib) or
wabt `wasm-objdump -x` (data segment ranges), and apply the D17 GM rule list. Prints the expected token (null = no
answer: literal HCFG in no section). usage: python3 storage_oracle.py file.bin"""
import base64, io, json, re, struct, subprocess, sys, zipfile, zlib


def valid(b, o):
    if b[o:o + 4] != b"HCFG" or len(b) < o + 12:
        return False
    _, k, n, c = struct.unpack_from("<BBHI", b, o + 4)
    p = bytes(x ^ k for x in b[o + 12:o + 12 + n])
    return n > 0 and len(p) == n and zlib.crc32(p) == c


def find(b):
    o = b.find(b"HCFG")
    while o >= 0:
        if valid(b, o):
            return "raw", o
        o = b.find(b"HCFG", o + 1)
    for m in re.finditer(rb"[A-Za-z0-9+/]{16,}={0,2}", b):
        try:
            d = base64.b64decode(m.group())
        except ValueError:
            continue
        if any(valid(d, i) for i in range(len(d)) if d[i:i + 4] == b"HCFG"):
            return "base64", m.start()
    return None, None


def section(path, b, o):
    if b[:4] == b"\x7fELF":
        from elftools.elf.elffile import ELFFile
        for s in ELFFile(io.BytesIO(b)).iter_sections():
            if s["sh_type"] not in ("SHT_NOBITS", "SHT_NULL") and s["sh_offset"] <= o < s["sh_offset"] + s["sh_size"]:
                return s.name, bool(s["sh_flags"] & 2 and not s["sh_flags"] & 4)
        return None
    if b[:2] == b"MZ":
        import pefile
        for s in pefile.PE(data=b).sections:
            if s.PointerToRawData <= o < s.PointerToRawData + s.SizeOfRawData:
                ch = s.Characteristics
                return s.Name.rstrip(b"\0").decode(), bool(ch & 0x40 and not ch & 0x20000020)
        return None
    if b[:4] == b"\0asm":
        out = subprocess.run(["wasm-objdump", "-x", path], capture_output=True, text=True).stdout
        sec = re.search(r"Data\[\d+\]:(.*?)(?:\n\S|\Z)", out, re.S)
        start = re.search(r"Data start=0x([0-9a-f]+) end=0x([0-9a-f]+)",
                          subprocess.run(["wasm-objdump", "-h", path], capture_output=True, text=True).stdout)
        if sec and start and int(start.group(1), 16) <= o < int(start.group(2), 16):
            return "wasm-data", True
        return None
    from macholib.MachO import MachO
    for h in MachO(path).headers:
        for cmd in h.commands:
            for s in (cmd[2] if isinstance(cmd[2], list) else []):
                if s.offset and s.offset <= o < s.offset + s.size:
                    seg, sect = s.segname.rstrip(b"\0").decode(), s.sectname.rstrip(b"\0").decode()
                    dat = not s.flags & 0x80000400 and (seg.startswith("__DATA") or (seg, sect) == ("__TEXT", "__const"))
                    return sect, bool(dat)
    return None


def token(path):
    b = open(path, "rb").read()
    if b[:2] == b"PK":
        z = zipfile.ZipFile(io.BytesIO(b))
        for n in z.namelist():
            enc, _ = find(z.read(n))
            if enc:
                return "base64" if enc == "base64" else "raw"
        return "none"
    enc, o = find(b)
    if enc is None:
        return "none"
    if enc == "base64":
        return "base64"
    s = section(path, b, o)
    if s is None:
        return None
    name, dat = s
    if name in (".hcfg", "__hcfg"):
        return "raw_hcfg_section"
    if name == "wasm-data":
        return "wasm_data_segment"
    return "raw_const_array" if dat else "raw"


if __name__ == "__main__":
    print(json.dumps(token(sys.argv[1])))
