"""Oracle for pelink_* fixtures: pefile (export/import/TLS directories) + `strings -a` / `strings -a -el` (runtime
LoadLibrary literals) + struct/zlib on pefile's section bytes (HCFG header + crc32). Independent of lib.binary.
usage: python3 pelink_oracle.py file.bin [plugin.bin]  -> JSON of expected_facts"""
import json, re, struct, subprocess, sys, zlib

import pefile


def facts(path):
    try:
        pe = pefile.PE(path)
    except pefile.PEFormatError:
        return None
    m = pe.FILE_HEADER.Machine
    out = {"machine": {0x8664: "x86-64", 0x14c: "i386"}[m], "machine_num": str(m), "machine_hex": hex(m),
           "is_dll": str(pe.FILE_HEADER.IMAGE_FILE_DLL).lower()}
    ed = getattr(pe, "DIRECTORY_ENTRY_EXPORT", None)
    if ed:
        out["dll_name"] = ed.name.decode()
        out["export_ordinal_base"] = str(ed.struct.Base)
        out["exports"] = [[s.ordinal, s.name.decode() if s.name else None, hex(s.address),
                           s.forwarder.decode() if s.forwarder else None] for s in sorted(ed.symbols, key=lambda s: s.ordinal)]
        out["export_names"] = sorted(s.name.decode() for s in ed.symbols if s.name)
        out["noname_ordinals"] = [s.ordinal for s in ed.symbols if not s.name] or "none"
        out["forwarders"] = [[s.name.decode(), s.forwarder.decode()] for s in ed.symbols if s.forwarder] or "none"
        out["export_count"] = str(len(ed.symbols))
    else:
        out.update({k: "none" for k in ("dll_name", "export_ordinal_base", "exports", "export_names")})
    imps = [[e.dll.decode(), [i.name.decode() if i.name else f"ord{i.ordinal}" for i in e.imports]]
            for e in getattr(pe, "DIRECTORY_ENTRY_IMPORT", [])]
    out["import_dlls"] = [d for d, _ in imps] or "none"
    out["imports"] = imps or "none"
    out["delay_import_dlls"] = [e.dll.decode() for e in getattr(pe, "DIRECTORY_ENTRY_DELAY_IMPORT", [])] or "none"
    tls = getattr(pe, "DIRECTORY_ENTRY_TLS", None)
    cbs = []
    if tls:
        rva = tls.struct.AddressOfCallBacks - pe.OPTIONAL_HEADER.ImageBase
        w = 8 if pe.PE_TYPE == pefile.OPTIONAL_HEADER_MAGIC_PE_PLUS else 4
        while True:
            v = pe.get_qword_at_rva(rva) if w == 8 else pe.get_dword_at_rva(rva)
            if not v:
                break
            cbs.append(hex(v))
            rva += w
    out["tls_callbacks"] = cbs or "none"
    out["tls_callback_count"] = str(len(cbs))
    names = {i.name.decode() for e in getattr(pe, "DIRECTORY_ENTRY_IMPORT", []) for i in e.imports if i.name}
    out["loader_apis"] = [a for a in ("LoadLibraryA", "LoadLibraryW", "GetProcAddress") if a in names] or "none"
    known = {d.lower() for d, _ in imps} | {"kernel32.dll", "ntdll.dll"}
    if ed:
        known.add(ed.name.decode().lower())
    libs = []
    for enc in ("s", "l"):
        so = subprocess.run(["strings", "-a", "-t", "d", "-e", enc, "-n", "5", path], capture_output=True, text=True).stdout
        for ln in so.splitlines():
            off, s = ln.strip().split(" ", 1)
            if re.fullmatch(r"[\w.\-\\/:]+\.dll", s, re.I) and s.lower() not in known:
                libs.append((int(off), s))
    out["loaded_libraries"] = [s for _, s in sorted(libs)] or "none"
    out["loaded_library"] = sorted(libs)[0][1] if libs else "none"
    sec = next((s for s in pe.sections if s.Name.rstrip(b"\0") == b".hcfg"), None)
    out.update(config="none", config_offset="none", config_section="none", config_symbol="none")
    if sec:
        b = sec.get_data()
        assert b[:4] == b"HCFG"
        _, key, n, crc = struct.unpack_from("<BBHI", b, 4)
        plain = bytes(c ^ key for c in b[12:12 + n])
        assert zlib.crc32(plain) == crc
        out["config"] = json.dumps(json.loads(plain), separators=(",", ":"))
        out["config_offset"] = str(sec.PointerToRawData)
        out["config_section"] = ".hcfg"
        out["config_symbol"] = next((s.name.decode() for s in ed.symbols if s.address == sec.VirtualAddress), "none")
    return out


if __name__ == "__main__":
    f = facts(sys.argv[1])
    if f and len(sys.argv) > 2:
        p = facts(sys.argv[2])
        L = open(sys.argv[1], "rb").read()
        res = sorted((L.find(n.encode() + b"\0"), n) for n in p["export_names"] if n.encode() + b"\0" in L)
        f = {"pair:loaded_library": f["loaded_library"], "pair:resolved_symbols": [n for _, n in res] or "none",
             "pair:init_export": res[0][1] if res else "none",
             "pair:sideload_match": str(f["loaded_library"].lower() == p["dll_name"].lower()).lower()}
    print(json.dumps(f))
