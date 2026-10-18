"""Independent oracle for locate_*.bin (NOT lib.binary): readelf -SW / -lW (ELF), pefile (PE), lief (Mach-O),
wasm-objdump -x (wasm). Probe offset = first occurrence of b"LOCMARK". Prints the expected locate_offset subset as JSON.
usage: python3 locate_oracle.py file.bin"""
import json, re, subprocess, sys
d = open(sys.argv[1], "rb").read()
off = d.find(b"LOCMARK")
hx = lambda v: f"0x{v:x}"
exp = None
if d[:4] == b"\x7fELF":
    exp = {"container": "elf", "section": "none"}
    rs = subprocess.run(["readelf", "-SW", sys.argv[1]], capture_output=True, text=True).stdout
    # [Nr] Name Type Address Off Size ES Flg Lk Inf Al
    for m in re.finditer(r"\]\s+(\S+)\s+(\S+)\s+([0-9a-f]+)\s+([0-9a-f]+)\s+([0-9a-f]+)\s+[0-9a-f]+\s+([A-Za-z]*)\s+\d", rs):
        nm, ty, ad, o, n, fl = m.groups()
        if ty not in ("NULL", "NOBITS") and int(o, 16) <= off < int(o, 16) + int(n, 16):
            exp.update(section=nm, section_flags=fl, vaddr=hx(int(ad, 16) + off - int(o, 16)))
    rl = subprocess.run(["readelf", "-lW", sys.argv[1]], capture_output=True, text=True).stdout
    loads, k = [], -1
    for line in rl.splitlines():
        m = re.match(r"\s+([A-Z_]+[A-Za-z_+]*)\s+0x([0-9a-f]+)\s+0x([0-9a-f]+)\s+0x[0-9a-f]+\s+0x([0-9a-f]+)\s+0x[0-9a-f]+\s+([RWE ]+?)\s+0x", line)
        if not m:
            continue
        k += 1
        ty, o, va, fs, fl = m.group(1), *(int(x, 16) for x in m.groups()[1:4]), m.group(5).replace(" ", "")
        if ty == "LOAD":
            loads.append(va - o)
            if o <= off < o + fs and "segment" not in exp:
                exp.update(segment="LOAD", segment_index=k, segment_flags=fl)
                exp.setdefault("vaddr", hx(va + off - o))
    exp["rva"] = hx(int(exp["vaddr"], 16) - min(loads))
elif d[:2] == b"MZ":
    import pefile
    pe = pefile.PE(data=d)
    for k, s in enumerate(pe.sections):
        if s.PointerToRawData <= off < s.PointerToRawData + s.SizeOfRawData:
            rva = pe.get_rva_from_offset(off)
            exp = {"container": "pe", "section": s.Name.rstrip(b"\0").decode(), "section_flags": hx(s.Characteristics),
                   "segment_index": k, "rva": hx(rva), "vaddr": hx(pe.OPTIONAL_HEADER.ImageBase + rva)}
elif d[:4] in (b"\xcf\xfa\xed\xfe", b"\xce\xfa\xed\xfe"):
    import lief
    b = lief.MachO.parse(sys.argv[1]).at(0)
    s = b.section_from_offset(off)
    sg = b.segment_from_offset(off)
    va = b.offset_to_virtual_address(off)
    exp = {"container": "mach-o", "section": s.name, "segment": sg.name, "vaddr": hx(va),
           "rva": hx(va - b.get_segment("__TEXT").virtual_address)}
elif d[:4] == b"\0asm":
    x = subprocess.run(["wasm-objdump", "-x", "-j", "Data", sys.argv[1]], capture_output=True, text=True).stdout
    for m in re.finditer(r"segment\[(\d+)\] memory=\d+ size=(\d+) - init i32=(\d+)", x):
        idx, size, init = map(int, m.groups())
        # segment payload = the bytes of this segment as dumped; locate them in the file via the hexdump text
        hexd = "".join(re.findall(r"^\s+-\s+[0-9a-f]+:\s+((?:[0-9a-f]{2,4} ?)+)", x[m.end():], re.M)).replace(" ", "")
        payload = bytes.fromhex(hexd)[:size]
        p = d.find(payload)
        if p <= off < p + size:
            exp = {"container": "wasm", "section": "data", "wasm_data_index": idx, "wasm_mem_offset": init + off - p}
print(json.dumps(exp))
