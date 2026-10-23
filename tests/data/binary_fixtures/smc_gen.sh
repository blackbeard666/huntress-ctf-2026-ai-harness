#!/bin/bash
# Generate smc_<name>.bin: a gcc x86-64 ELF that decrypts code or data IN PLACE at runtime (mprotect RWX / inline
# mprotect syscall, xor / keystream loop, then call / print). The HCFG blob (python3 stdlib struct+zlib writer) is
# either built by stack stores inside a function that python3 xor-encrypts POST-LINK (symbol range from readelf -sW),
# or a raw blob in a .cfgx section stored under an LCG keystream. The program prints the decrypted blob on stdout, so
# the oracle runs it natively (smc_oracle.sh).    usage: bash smc_gen.sh <name>    (run from this directory)
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd); n=$1
src="$here/smc_src/smc_$n.c"; out="$here/smc_$n.bin"
blob() {  # $1 = json config, $2 = header key byte, $3 = "bad" to corrupt the crc  -> C initialiser list on stdout
python3 - "$1" "$2" "${3:-}" <<'PY'
import struct, sys, zlib
cfg, key, bad = sys.argv[1].encode(), int(sys.argv[2], 0), sys.argv[3] == "bad"
body = bytes(b ^ key for b in cfg)
crc = zlib.crc32(cfg) ^ (0x1111 if bad else 0)
b = b"HCFG" + struct.pack("<BBHI", 1, key, len(cfg), crc) + body
print(",".join("0x%02x" % c for c in b))
PY
}
stores() { python3 -c 'import sys; print("".join("b[%d]=%s;" % (i, v) for i, v in enumerate(sys.argv[1].split(","))))' "$1"; }
lcg() {   # $1 = initialiser list, $2 = seed: c[i] = p[i] ^ k, k = k*0x6d + 0x3b (mod 256) after each byte
python3 -c 'import sys
k = int(sys.argv[2], 0); o = []
for v in sys.argv[1].split(","):
    o.append("0x%02x" % (int(v, 0) ^ k)); k = (k * 0x6d + 0x3b) & 0xff
print(",".join(o))' "$1" "$2"; }
func_prog() {  # $1 = initialiser list, $2 = xor key, $3 = protect: libc|syscall
  local B=$1 K=$2 P=$3 L; L=$(tr -cd , <<<"$B" | wc -c); L=$((L + 1))
  cat <<C
#include <stdio.h>
#include <stdint.h>
#include <unistd.h>
#include <sys/mman.h>
#define N $L
__attribute__((noinline, section(".text.enc"))) void build(unsigned char *out) {
  volatile unsigned char b[N]; $(stores "$B")
  for (int i = 0; i < N; i++) out[i] = b[i]; }
__attribute__((noinline, section(".text.enc"))) void build_end(void) { __asm__ volatile("nop"); }
static long prot(void *a, unsigned long n) {
$(if [ "$P" = syscall ]; then echo '  long r; __asm__ volatile("syscall" : "=a"(r) : "0"(10L), "D"(a), "S"(n), "d"(7L) : "rcx", "r11", "memory"); return r;'
  else echo '  return mprotect(a, n, PROT_READ | PROT_WRITE | PROT_EXEC);'; fi) }
int main(void) {
  unsigned char buf[N]; uintptr_t a = (uintptr_t)build & ~(uintptr_t)4095;
  if (prot((void *)a, ((uintptr_t)build_end - a + 4096) & ~(uintptr_t)4095)) return 1;
  for (volatile unsigned char *p = (unsigned char *)build; p < (unsigned char *)build_end; p++) *p ^= $K;
  build(buf); fwrite(buf, 1, N, stdout); return 0; }
C
}
patch() {  # xor-encrypt [build, build_end) of $1 post-link with key $2 (readelf -sW symbol vaddrs -> file offsets)
  local f=$1 K=$2 s e
  s=$(readelf -sW "$f" | awk '$8 == "build" {print $2}'); e=$(readelf -sW "$f" | awk '$8 == "build_end" {print $2}')
  python3 - "$f" "$s" "$e" "$K" "$(readelf -lW "$f" | awk '$1 == "LOAD" {print $2, $3, $5}' | tr '\n' ';')" <<'PY'
import sys
f, s, e, k, loads = sys.argv[1], int(sys.argv[2], 16), int(sys.argv[3], 16), int(sys.argv[4], 0), sys.argv[5]
d = bytearray(open(f, "rb").read())
for ld in filter(None, loads.split(";")):
    off, va, fsz = (int(x, 16) for x in ld.split())
    if va <= s < va + fsz:
        o = off + s - va
        d[o:o + e - s] = bytes(c ^ k for c in d[o:o + e - s])
        break
else:
    sys.exit("no LOAD for build")
open(f, "wb").write(d)
PY
}
CFG1='{"campaign":"smc-func","beacon":"https://c2.smc-one.example/gate","sleep":41,"id":"SMC-7F31"}'
CFG2='{"campaign":"smc-data","mutex":"Global\\smc_cfgx","port":8443,"id":"SMC-2C9A"}'
CFG3='{"campaign":"smc-sys","beacon":"tcp://203.0.113.9:4444","jitter":7,"id":"SMC-55E0"}'
case $n in
func_O0)        func_prog "$(blob "$CFG1" 0x00)" 0xa7 libc > "$src"; gcc -O0 -no-pie -o "$out" "$src"; patch "$out" 0xa7 ;;
func_O2_sys)    func_prog "$(blob "$CFG3" 0x5c)" 0x3d syscall > "$src"; gcc -O2 -o "$out" "$src"; patch "$out" 0x3d
                cp "$out" "$here/smc_src/smc_func_O2_sys.unstripped"   # symbols for the oracle
                strip -s "$out" ;;
decoy_badcrc)   func_prog "$(blob "$CFG1" 0x00 bad)" 0xa7 libc > "$src"; gcc -O0 -no-pie -o "$out" "$src"; patch "$out" 0xa7 ;;
data_lcg)
  B=$(blob "$CFG2" 0x00); E=$(lcg "$B" 0x91); L=$(tr -cd , <<<"$B" | wc -c); L=$((L + 1))
  cat > "$src" <<C
#include <stdio.h>
#include <stdint.h>
#include <sys/mman.h>
__attribute__((section(".cfgx"), aligned(4096))) const unsigned char cfg[$L] = {$E};
int main(void) {
  unsigned char *p = (unsigned char *)cfg; unsigned k = 0x91;
  if (mprotect((void *)((uintptr_t)p & ~(uintptr_t)4095), 8192, PROT_READ | PROT_WRITE)) return 1;
  for (int i = 0; i < $L; i++) { p[i] ^= k; k = (k * 0x6d + 0x3b) & 0xff; }
  fwrite(p, 1, $L, stdout); return 0; }
C
  gcc -O2 -o "$out" "$src" ;;
decoy_plain)   # mprotect + in-place xor of a scratch table, no HCFG anywhere
  cat > "$src" <<'C'
#include <stdio.h>
#include <stdint.h>
#include <sys/mman.h>
__attribute__((section(".cfgx"), aligned(4096))) const unsigned char tbl[64] = {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16};
int main(void) {
  unsigned char *p = (unsigned char *)tbl;
  if (mprotect((void *)((uintptr_t)p & ~(uintptr_t)4095), 4096, PROT_READ | PROT_WRITE)) return 1;
  for (int i = 0; i < 64; i++) p[i] ^= 0x5a;
  printf("%u\n", p[3]); return 0; }
C
  gcc -O2 -o "$out" "$src" ;;
decoy_trunc)   bash "$0" func_O0; head -c 4100 "$here/smc_func_O0.bin" > "$out" ;;
*) echo "unknown $n" >&2; exit 2 ;;
esac
