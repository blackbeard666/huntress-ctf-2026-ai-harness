#!/bin/bash
# provenance oracle (independent READERS, not lib.binary): binutils readelf -n / -p .comment /
# --debug-dump=info --dwarf-depth=1 (first CU), `go version`, and pefile for PE (FILE_HEADER, DEBUG CodeView, Rich).
# usage: bash prov_oracle.sh <file>  -> JSON {field: expected}
f=$1
if [ "$(head -c4 "$f" | od -An -c | tr -d ' ')" = '177ELF' ] && readelf -h "$f" >/dev/null 2>&1; then
  bid=$(readelf -nW "$f" 2>/dev/null | sed -n 's/.*Build ID: *\([0-9a-f]*\).*/\1/p' | head -1)
  com=$(readelf -p .comment "$f" 2>/dev/null | sed -n 's/^ *\[ *[0-9a-f]*\]  //p')
  cu=$(readelf --debug-dump=info --dwarf-depth=1 "$f" 2>/dev/null | awk '/Compilation Unit @/{n++} n==1')
  at() { printf '%s\n' "$cu" | grep -m1 "DW_AT_$1 " | sed 's/^[^:]*: //; s/^(\(indirect\|indirect line\) string, offset: [0-9a-fx]*): //'; }
  lang=$(printf '%s\n' "$cu" | grep -m1 'DW_AT_language ' | sed 's/^[^:]*: *\([0-9]*\).*/\1/')
  gov=$(go version "$f" 2>/dev/null | sed -n 's/^[^:]*: //p')
  F="$f" BID="$bid" COM="$com" PROD="$(at producer)" LANG="$lang" CDIR="$(at comp_dir)" NAME="$(at name)" GOV="$gov" \
  python3 -I -c '
import json, os, re
e = os.environ; n = lambda v: v if v else "none"
cm = [s for s in e["COM"].split("\n") if s]
gcc = next((s.split()[-1] for s in cm if s.startswith("GCC:")), "none")
rv = next((re.search(r"rustc version (\S+)", s).group(1) for s in cm if "rustc version" in s), "none")
print(json.dumps({"format": "elf", "build_id": n(e["BID"]), "compiler": cm[0] if cm else "none",
    "comment_strings": cm, "gcc_version": gcc, "rustc_version": rv, "go_version": n(e["GOV"]),
    "has_dwarf": "true" if e["PROD"] or e["LANG"] else "false",
    "dwarf_producer": n(e["PROD"]), "dwarf_language_num": n(e["LANG"]), "dwarf_comp_dir": n(e["CDIR"]),
    "dwarf_name": n(e["NAME"])}, indent=1))'
else
  ROOT=$(cd "$(dirname "$0")/../../.." && pwd)
  "$ROOT/.venv/bin/python" -I -c '
import json, sys, datetime, pefile
try:
    p = pefile.PE(sys.argv[1])
except pefile.PEFormatError:
    print("null"); sys.exit()
ts = p.FILE_HEADER.TimeDateStamp
o = {"format": "pe", "timestamp": str(ts), "timestamp_hex": "0x%08x" % ts,
     "timestamp_iso": datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
     "linker_version": "%d.%02d" % (p.OPTIONAL_HEADER.MajorLinkerVersion, p.OPTIONAL_HEADER.MinorLinkerVersion),
     "pdb_path": "none", "pdb_guid": "none", "pdb_age": "none"}
for d in getattr(p, "DIRECTORY_ENTRY_DEBUG", []):
    cv = d.entry
    if cv is not None and getattr(cv, "CvSignature", b"") == b"RSDS":
        o["pdb_path"] = cv.PdbFileName.rstrip(b"\0").decode()
        o["pdb_guid"] = "%08x-%04x-%04x-%02x%02x-%s" % (cv.Signature_Data1, cv.Signature_Data2, cv.Signature_Data3,
                                                     cv.Signature_Data4, cv.Signature_Data5, cv.Signature_Data6.hex())
        o["pdb_age"] = str(cv.Age)
        break
r = p.parse_rich_header()
v = r["values"] if r else []
o["has_rich"] = "true" if v else "false"
o["rich_count"] = str(len(v) // 2)
o["rich_entries"] = [[v[i] >> 16, v[i] & 0xffff, v[i + 1]] for i in range(0, len(v), 2)]
o["rich_xor_key"] = "0x%08x" % int.from_bytes(r["key"], "little") if r else "none"
print(json.dumps(o, indent=1))' "$f"
fi
