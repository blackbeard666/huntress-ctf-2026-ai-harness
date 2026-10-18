#!/bin/sh
# Expected values for peh_*.bin from pefile (independent reader; lib.binary.pe_header_facts uses no pefile) and
# binutils objdump -h for section names (resolves /N via the COFF string table). usage: sh peh_oracle.sh <file.bin>
PY=${PY:-../../../.venv/bin/python3}
"$PY" -I -c '
import sys, json, pefile
f = sys.argv[1]
try:
    pe = pefile.PE(f, fast_load=True)
except pefile.PEFormatError as e:
    print(json.dumps("none")); sys.exit()
pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
F, O = pe.FILE_HEADER, pe.OPTIONAL_HEADER
d = {"format": "pe", "pe_type": "PE32+" if O.Magic == 0x20b else "PE32", "machine_num": str(F.Machine),
     "entry_point": hex(O.ImageBase + O.AddressOfEntryPoint), "entry_rva": hex(O.AddressOfEntryPoint),
     "image_base": hex(O.ImageBase), "timestamp": str(F.TimeDateStamp), "characteristics": hex(F.Characteristics),
     "characteristics_flags": sorted(k for k, v in pefile.image_characteristics if isinstance(k, str) and F.Characteristics & v),
     "dll_characteristics": hex(O.DllCharacteristics),
     "dll_characteristics_flags": sorted(k for k, v in pefile.dll_characteristics if isinstance(k, str) and O.DllCharacteristics & v),
     "subsystem_const": pefile.SUBSYSTEM_TYPE[O.Subsystem], "subsystem_int": str(O.Subsystem),
     "is_dll": "true" if pe.is_dll() else "false", "section_count": F.NumberOfSections,
     "has_symtab": "true" if F.PointerToSymbolTable and F.NumberOfSymbols else "false",
     "number_of_symbols": F.NumberOfSymbols,
     "import_dlls": [e.dll.decode() for e in getattr(pe, "DIRECTORY_ENTRY_IMPORT", [])]}
print(json.dumps(d))' "$1"
echo "objdump section names:"
objdump -h "$1" 2>/dev/null | awk '$1 ~ /^[0-9]+$/ {print $2}' | paste -sd, -
