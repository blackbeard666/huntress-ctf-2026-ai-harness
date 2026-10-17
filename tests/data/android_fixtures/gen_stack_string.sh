#!/bin/bash
# Native stack-string fixtures (coverage atlas row 40): a Java_* checker builds the ENCODED answer on the stack with
# immediate stores and compares enc(input[i]) against it -- no ANS literal / encoded blob in any data section, and the
# plaintext never exists at run time. Bytes encoded with perl; built with gcc / aarch64-linux-gnu-gcc; zipped with `zip`.
# Oracle: native_src/stack_harness.c dlopen()s the real .so and calls the checker with the token -> "= 1".
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); SRC=$HERE/native_src; OUT=${1:-$HERE}
mkapk() {  # name abi so
  local d; d=$(mktemp -d); mkdir -p "$d/lib/$2" "$d/assets"
  cp "$3" "$d/lib/$2/"; printf '{"hint":"the check is native"}' > "$d/assets/config.json"
  rm -f "$OUT/$1.apk"; (cd "$d" && zip -qX -r "$OUT/$1.apk" assets lib); rm -rf "$d"
}
T=$(mktemp -d)
# 1. x86_64 -O0, initializer list -> movabs rax/rdx + mov qword/dword [rbp-off]; enc = c ^ 0x37
xblob() { perl -e 'print join ",", map { sprintf "0x%02x", ord($_) ^ 0x37 } split //, $ARGV[0]' "$1"; }
gcc -shared -fPIC -O0 -DBLOB="$(xblob 'ANS-5b0e8d71f3a9c246')" -o "$T/libcheck.so" "$SRC/stack_check.c"
mkapk native_stack_xor_x86_64 x86_64 "$T/libcheck.so"
# 2. arm64 -O2, volatile per-byte stores -> mov w2, #imm; strb w2, [sp, #off]; enc = c + 7 + 13*i
ST=$(perl -e '$i=0; print join " ", map { $j=$i++; sprintf "s[%d]=0x%02x;", $j, (ord($_)+7+13*$j)&255 } split //, $ARGV[0]' 'ANS-e7d2094cb1f86a3e')
aarch64-linux-gnu-gcc -shared -fPIC -O2 -DNLEN=20 -DSTORES="$ST" -D'ENC(c,i)=((c)+7+13*(i))' -o "$T/libcheck.so" "$SRC/stack_check.c"
mkapk native_stack_addidx_arm64 arm64-v8a "$T/libcheck.so"
# 3. arm64 -O0, volatile per-byte stores; rolling xor enc = c ^ (0x5c + 3*i)
ST=$(perl -e '$i=0; print join " ", map { $j=$i++; sprintf "s[%d]=0x%02x;", $j, ord($_) ^ ((0x5c+3*$j)&255) } split //, $ARGV[0]' 'ANS-0f9c3b6a2e7d1584')
aarch64-linux-gnu-gcc -shared -fPIC -O0 -DNLEN=20 -DSTORES="$ST" -D'ENC(c,i)=((c)^(0x5c+3*(i)))' -o "$T/libcheck.so" "$SRC/stack_check.c"
mkapk native_stack_rollxor_arm64 arm64-v8a "$T/libcheck.so"
# 4. DECOY: as 1 with a near-miss token (15 hex + 'Z')
gcc -shared -fPIC -O0 -DBLOB="$(xblob 'ANS-5b0e8d71f3a9c24Z')" -o "$T/libcheck.so" "$SRC/stack_check.c"
mkapk native_decoy_stack_xor_nearmiss x86_64 "$T/libcheck.so"
rm -rf "$T"
