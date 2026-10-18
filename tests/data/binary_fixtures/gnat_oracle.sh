#!/bin/sh
# Independent oracle for gnat_* fixtures (binutils + pyelftools; never lib.binary): prints the facts the json records.
f=$1
file -b "$f"
echo "--- GNAT Version (strings -a)"; strings -a "$f" | grep -m1 -o 'GNAT Version: .*'
echo "--- _ada_ main (nm --defined-only, else strings)"; nm --defined-only "$f" 2>/dev/null | awk '$3 ~ /^_ada_/ {print $3}'; strings -a "$f" | grep -m1 -x '_ada_[a-z0-9_]*'
echo "--- binder / elab / user subprograms (nm --defined-only)"; nm --defined-only "$f" 2>/dev/null | awk '{print $2, $3}' | grep -E ' (adainit|adafinal|main|__gnat_main|ada_main___elabb|.*___elab[bs]|[a-z0-9_]+__[a-z0-9_]+)$'
echo "--- DWARF CU (readelf --debug-dump=info)"; readelf --debug-dump=info "$f" 2>/dev/null | grep -A6 DW_TAG_compile_unit | grep -E 'producer|language|DW_AT_name'
echo "--- exception data (pyelftools: data symbol -> {u8, 'A', u32 len, ptr} -> name)"
python3 -I - "$f" <<'P'
import sys, struct
try:
    from elftools.elf.elffile import ELFFile
    e = ELFFile(open(sys.argv[1], 'rb'))
except Exception as x:
    print('not ELF:', x); sys.exit(0)
def rd(va, n):
    for s in e.iter_sections():
        if s['sh_addr'] and s['sh_type'] != 'SHT_NOBITS' and s['sh_addr'] <= va < s['sh_addr'] + s['sh_size']:
            return s.data()[va - s['sh_addr']:va - s['sh_addr'] + n]
st = e.get_section_by_name('.symtab')
for sym in (st.iter_symbols() if st else []):
    if sym['st_info']['type'] == 'STT_OBJECT' and sym['st_size'] == 40:
        b = rd(sym['st_value'], 16)
        if b and b[1:2] == b'A':
            n, p = struct.unpack('<4xIQ', b[:16])
            print(sym.name, rd(p, n)[:-1].decode())
P
