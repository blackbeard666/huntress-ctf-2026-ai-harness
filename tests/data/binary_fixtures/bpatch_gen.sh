#!/bin/bash
# Generate binary-patch-file fixtures: two gcc ELF builds (A vulnerable, B fixed), then base A + patch -> B written by
# INDEPENDENT writers: bsdiff4.diff (C ext, pip into tools/pypatch) for BSDIFF40, stdlib struct writers below for
# IPS / BPS / UPS (spec writers, not lib code). usage (from this dir): bash bpatch_gen.sh
set -e
D=$(cd "$(dirname "$0")" && pwd); T=${TMPDIR:-/tmp}/bpatch; mkdir -p "$T"
cat > "$T/a.c" <<'C'
#include <stdio.h>
#include <string.h>
int copy_name(char *dst, const char *s, size_t n) { if (n > 64) return -1; memcpy(dst, s, n); return 0; }
int main(int c, char **v) { char b[64]; return c > 1 ? copy_name(b, v[1], strlen(v[1])) : puts("usage"); }
C
sed 's/n > 64/n >= 64/' "$T/a.c" > "$T/b.c"
sed 's/memcpy(dst, s, n); return 0;/strncpy(dst, s, n); dst[63] = 0; return 0;/' "$T/b.c" > "$T/c.c"
for x in a b c; do gcc -O1 -fno-inline -o "$T/$x.elf" "$T/$x.c"; done
cp "$T/a.elf" "$D/bpatch_base.bin"; cp "$T/b.elf" "$D/bpatch_target_flip.elf"
PYTHONPATH="$D/../../../tools/pypatch" python3 - "$T" "$D" <<'PY'
import sys, struct, zlib, bsdiff4
T, D = sys.argv[1:]
A, B, C = (open(f"{T}/{x}.elf", "rb").read() for x in "abc")
def vi(n):   # beat varint
    o = bytearray()
    while True:
        x = n & 0x7f; n >>= 7
        if not n: o.append(0x80 | x); return bytes(o)
        o.append(x); n -= 1
def runs(a, b):
    i, n = 0, len(b)
    while i < n:
        if i < len(a) and a[i] == b[i]: i += 1; continue
        j = i
        while j < n and not (j < len(a) and a[j] == b[j]): j += 1
        yield i, j; i = j
def ips(a, b):
    o = bytearray(b"PATCH")
    for s, e in runs(a, b):
        while s < e:
            k = min(e, s + 0xffff); c = b[s:k]
            if len(c) >= 4 and c.count(c[:1]) == len(c): o += s.to_bytes(3, "big") + b"\0\0" + len(c).to_bytes(2, "big") + c[:1]
            else: o += s.to_bytes(3, "big") + len(c).to_bytes(2, "big") + c
            s = k
    o += b"EOF"
    if len(b) < len(a): o += len(b).to_bytes(3, "big")
    return bytes(o)
def bps(a, b, meta=b""):   # SourceRead for equal bytes, TargetRead for the rest
    o = bytearray(b"BPS1" + vi(len(a)) + vi(len(b)) + vi(len(meta)) + meta); i = 0
    while i < len(b):
        j = i
        if i < len(a) and a[i] == b[i]:
            while j < len(b) and j < len(a) and a[j] == b[j]: j += 1
            o += vi(((j - i - 1) << 2) | 0)
        else:
            while j < len(b) and not (j < len(a) and a[j] == b[j]): j += 1
            o += vi(((j - i - 1) << 2) | 1) + b[i:j]
        i = j
    o += struct.pack("<II", zlib.crc32(a), zlib.crc32(b)); o += struct.pack("<I", zlib.crc32(o)); return bytes(o)
def ups(a, b):
    o = bytearray(b"UPS1" + vi(len(a)) + vi(len(b))); n = max(len(a), len(b)); last = 0
    pa, pb = a + bytes(n - len(a)), b + bytes(n - len(b)); i = 0
    while i < n:
        if pa[i] == pb[i]: i += 1; continue
        o += vi(i - last)
        while i < n and pa[i] != pb[i]: o.append(pa[i] ^ pb[i]); i += 1
        o.append(0); i += 1; last = i
    o += struct.pack("<II", zlib.crc32(a), zlib.crc32(b)); o += struct.pack("<I", zlib.crc32(o)); return bytes(o)
out = {"bpatch_bsdiff_flip": bsdiff4.diff(A, B), "bpatch_bsdiff_grow": bsdiff4.diff(A, C),
       "bpatch_ips_flip": ips(A, B), "bpatch_ips_rle": ips(A, A[:0x200] + b"\x90" * 48 + A[0x230:]),
       "bpatch_bps_flip": bps(A, B, b"<fix>bounds</fix>"), "bpatch_ups_flip": ups(A, B)}
bad = bytearray(out["bpatch_bps_flip"]); bad[-9] ^= 1   # target crc corrupted -> crc_valid false
out["bpatch_bps_badcrc"] = bytes(bad)
out["bpatch_decoy_magic"] = b"PATCX" + out["bpatch_ips_flip"][5:]                 # renamed impostor
out["bpatch_decoy_trunc"] = out["bpatch_bsdiff_flip"][:len(out["bpatch_bsdiff_flip"]) // 2]   # cut bz2 stream
for k, v in out.items(): open(f"{D}/{k}.bin", "wb").write(v)
open(f"{T}/rle_target.elf", "wb").write(A[:0x200] + b"\x90" * 48 + A[0x230:])
PY
