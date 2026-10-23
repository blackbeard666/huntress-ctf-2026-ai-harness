#!/bin/bash
# Independent oracle for smc_<name>.bin (never lib.binary): run the program natively (it decrypts itself and prints
# the HCFG blob) and check the blob with python3 struct+zlib+json; locate the stored form with readelf/objdump:
#   func_*: python3 xor-decrypts [build, build_end) of a copy (readelf -sW symbols; smc_src/*.unstripped when the
#           fixture is stripped), objdump -d of the copy -> the first `movb $0x48` in build (file offset of that
#           instruction, and of its imm8 byte for the -O0 4-byte-stride `c6 45 xx imm` run)
#   data_*: readelf -SW .cfgx section file offset
# usage: bash smc_oracle.sh <name> <xor key>      (run from this directory)
set -euo pipefail
n=$1 k=${2:-0}; f=smc_$n.bin; sym=$f; [ -f smc_src/smc_$n.unstripped ] && sym=smc_src/smc_$n.unstripped
./$f | python3 -c 'import sys, struct, zlib, json
b = sys.stdin.buffer.read(); ver, key, n, crc = struct.unpack_from("<BBHI", b, 4); p = bytes(c ^ key for c in b[12:12 + n])
print("blob", b[:4], "ver", ver, "key", key, "len", n, "crc_ok", zlib.crc32(p) == crc); print("config", json.dumps(json.loads(p)))'
case $n in
data_*) readelf -SW "$f" | awk '$2 == ".cfgx" {print ".cfgx file offset", strtonum("0x" $5)}' ;;
*) s=$(readelf -sW "$sym" | awk '$8 == "build" {print $2}'); e=$(readelf -sW "$sym" | awk '$8 == "build_end" {print $2}')
   t=$(mktemp); trap 'rm -f "$t"' EXIT
   python3 - "$sym" "$t" "$s" "$e" "$k" "$(readelf -lW "$sym" | awk '$1 == "LOAD" {print $2, $3, $5}' | tr '\n' ';')" <<'PY'
import sys
f, t, s, e, k, loads = sys.argv[1], sys.argv[2], int(sys.argv[3], 16), int(sys.argv[4], 16), int(sys.argv[5], 0), sys.argv[6]
d = bytearray(open(f, "rb").read())
for ld in filter(None, loads.split(";")):
    off, va, fsz = (int(x, 16) for x in ld.split())
    if va <= s < va + fsz:
        o = off + s - va
        d[o:o + e - s] = bytes(c ^ k for c in d[o:o + e - s])
        print("decrypted range file offset", o, "size", e - s)
open(t, "wb").write(d)
PY
   delta=$(readelf -lW "$sym" | awk -v s=$((16#$s)) '$1 == "LOAD" && strtonum($3) <= s && s < strtonum($3) + strtonum($5) {print strtonum($3) - strtonum($2)}')
   dis=$(objdump -d "$t" --start-address=0x$s --stop-address=0x$e)
   line=$(grep -m1 'movb *\$0x48,' <<<"$dis"); echo "$line"
   awk -v d=$delta -F'\t' '{h = substr($1, 1, index($1, ":") - 1); gsub(/ /, "", h); a = strtonum("0x" h); nb = split($2, x, " ")
     print "first movb $0x48 file offset", a - d; print "  its imm8 byte file offset", a - d + nb - 1}' <<<"$line" ;;
esac
