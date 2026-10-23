#!/bin/sh
# usage: sh vmbc_oracle.sh <fixture.bin>   (after vmbc_gen.sh; never imports lib.binary)
# Runs the -DORACLE twin build natively (the real CPU executes the VM), decodes the dumped buffer (raw HCFG or base64 of
# it) with stdlib. Offset of the program blob: `prog` symbol of the (unstripped) twin via nm -S + readelf -SW -> its
# bytes -> their unique file offset in the fixture (stripped builds have no symbol of their own).
set -e
T=${TMPDIR:-/tmp}/vmbc_gen; b=$1; o="$T/$(basename "$b" .bin).oracle"
out=$("$o" | base64 -w0)
sym=$(nm -S "$o" | awk '$4=="prog"{print $1, $2}')
sec=$(readelf -SW "$o" | awk '$2==".rodata"{print $4, $5}')
python3 -I -c '
import base64, json, struct, sys, zlib
raw, b, o = base64.b64decode(sys.argv[1]), open(sys.argv[2], "rb").read(), open(sys.argv[3], "rb").read()
va, n, sa, so = (int(x, 16) for x in sys.argv[4:8])
prog = o[va - sa + so:va - sa + so + n]
off = b.find(prog) if b.count(prog) == 1 else None
for blob, enc in ((raw, "vm-raw"), (base64.b64decode(raw) if raw[:4] == b"SENG" else b"", "vm-base64")):
    if blob[:4] == b"HCFG":
        v, k, n, crc = struct.unpack_from("<BBHI", blob, 4); p = bytes(c ^ k for c in blob[12:12 + n])
        if zlib.crc32(p) == crc:
            print(json.dumps({"encoding": enc, "offset": off, "prog_size": len(prog), "config": json.loads(p)})); break
else:
    print("none")' "$out" "$b" "$o" $sym $sec
