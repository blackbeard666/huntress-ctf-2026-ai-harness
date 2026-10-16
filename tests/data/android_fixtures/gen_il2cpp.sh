#!/usr/bin/env bash
# Unity IL2CPP global-metadata.dat fixtures for lib.android.il2cpp_literal_scan (coverage atlas row 56).
# Writer: a stdlib struct writer of the documented header (Il2CppGlobalMetadataHeader: magic 0xFAB11BAF, version,
#   stringLiteral{Offset,Size} @8, stringLiteralData{Offset,Size} @16, string{Offset,Size} @24 for v24-v31;
#   v38+ sections {offset,size,count}) + Il2CppStringLiteral {uint32 length, int32 dataIndex}; packaged with `zip`.
# Oracle: binutils `strings` on the unzipped entry + coreutils base64 / xxd / a python3 xor one-liner.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
W=$(mktemp -d); trap 'rm -rf "$W"' EXIT
META=assets/bin/Data/Managed/Metadata/global-metadata.dat
mk() {  # name magic-hex version literal...
  local name=$1 magic=$2 ver=$3; shift 3
  mkdir -p "$W/$name/$(dirname $META)" "$W/$name/lib/arm64-v8a"
  python3 -I - "$W/$name/$META" "$magic" "$ver" "$@" <<'PY'
import struct, sys
out, magic, ver, lits = sys.argv[1], int(sys.argv[2], 16), int(sys.argv[3]), [s.encode() for s in sys.argv[4:]]
idents = b"\0".join([b"Assembly-CSharp", b"PuzzleController", b"Start", b"Update", b"<Module>", b""])
hdr = 0x110 if ver < 38 else 0x200
data, table = b"", b""
for s in lits:
    table += struct.pack("<Ii", len(s), len(data)); data += s
lo, do = hdr, hdr + len(table); so = do + len(data)
h = struct.pack("<Ii", magic, ver)
if ver < 38:
    h += struct.pack("<iiiiii", lo, len(table), do, len(data), so, len(idents))
else:
    h += struct.pack("<iiiiiiiii", lo, len(table), len(lits), do, len(data), len(data), so, len(idents), 6)
h = h.ljust(hdr, b"\0")
open(out, "wb").write(h + table + data + idents)
PY
  printf 'placeholder' > "$W/$name/AndroidManifest.xml"
  printf '\x7fELF-placeholder-libil2cpp' > "$W/$name/lib/arm64-v8a/libil2cpp.so"
  rm -f "$HERE/$name.apk"; (cd "$W/$name" && zip -qX "$HERE/$name.apk" AndroidManifest.xml lib/arm64-v8a/libil2cpp.so $META)
}
B64=$(printf 'ANS-5d1c8e3fa07b2946' | base64 -w0)
mk il2cpp_v29_b64 FAB11BAF 29 "Score: " "https://api.example.invalid/unity/v2" "$B64" "Player"
KEY=unitykey
XOR=$(python3 -I -c 'import base64,sys; p,k=sys.argv[1].encode(),sys.argv[2].encode(); print(base64.b64encode(bytes(c^k[i%len(k)] for i,c in enumerate(p))).decode())' 'flag=ANS-a4e07c19d36b582f' $KEY)
mk il2cpp_v29_xor_neighbor_key FAB11BAF 29 "Loading..." "$KEY" "$XOR" "GameOver"
HEX=$(printf 'ANS-0b9f6c2d4e81a735' | xxd -p | tr -d '\n')
mk il2cpp_v39_hex FAB11BAF 39 "MainMenu" "$HEX" "Quit"
NEAR=$(printf 'ANS-3c7e1a9f0d2b6e4' | base64 -w0)   # 15 hex digits: near-miss
mk il2cpp_decoy_nearmiss FAB11BAF 29 "Score: " "$NEAR" "QU5YLTAxMjM0NTY3ODlhYmNkZWY=" "Player"
WM=$(printf 'ANS-8e2a4c6f1b3d5e70' | base64 -w0)
mk il2cpp_decoy_wrong_magic DEADBEEF 29 "Score: " "$WM" "Player"  # impostor: valid literal, not IL2CPP metadata
