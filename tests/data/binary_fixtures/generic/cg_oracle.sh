#!/bin/sh
# Independent reader for the campaign-graph fixtures (no lib.binary): Python finds the LAST offset of the magic whose
# 12-byte header crc32-validates the xor-decoded payload, writes the plain JSON to stdout; jq evaluates the filter.
# usage: cg_oracle.sh MEMBER MAGIC 'JQ_FILTER'   (prints nothing when no valid record)
python3 -I -c '
import sys, struct, zlib
b = open(sys.argv[1], "rb").read(); m = sys.argv[2].encode()
for o in sorted((i for i in range(len(b) - 3) if b[i:i + 4] == m), reverse=True):
    ver, k, n, c = struct.unpack("<BBHI", b[o + 4:o + 12]); p = bytes(x ^ k for x in b[o + 12:o + 12 + n])
    if len(p) == n and zlib.crc32(p) == c:
        sys.stdout.write(p.decode()); break
' "$1" "$2" | jq -r "$3"
