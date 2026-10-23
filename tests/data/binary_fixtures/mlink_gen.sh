#!/bin/bash
# usage: mlink_gen.sh out kind [json]
# Mach-O loader + dylib pair (lib.binary.macho_link_facts). The dylib carries the macho_gen.sh HCFG struct in
# section("__DATA,__hcfg") (key 0, crc32 = gzip trailer). kinds:
#  x64_dylib  zig cc -target x86_64-macos -shared, install_name @rpath/libpair.dylib, current 2.1.0 / compat 2.0.0
#  x64_app    zig cc -target x86_64-macos: -lpair (LC_LOAD_DYLIB @rpath) + -weak-lweak (LC_LOAD_WEAK_DYLIB
#             @loader_path/libweak.dylib) + LC_RPATH @executable_path/../Frameworks, @loader_path/lib (LC_DYLD_INFO_ONLY)
#  a64cf_dylib / a64cf_app  zig cc -c (aarch64-macos) + NDK ld64.lld -fixup_chains (LC_DYLD_CHAINED_FIXUPS +
#             LC_DYLD_EXPORTS_TRIE); app weak-links libpair (-weak-lpair_cf), rpaths @executable_path/../Frameworks, @loader_path
#  decoy_obj  (decoy) zig cc -c aarch64-macos: MH_OBJECT, no dylibs / rpaths / install name / exports trie
#  decoy_elf  (decoy) gcc -shared ELF (weak.c) renamed libpair.dylib: not a Mach-O, no HCFG
set -e
R="$(cd "$(dirname "$0")/../../.." && pwd)"; W=$(mktemp -d); O="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
Z() { (cd "$W" && PYTHONPATH="$R/tools/pyziglang" python3 -m ziglang cc "$@"); }
LLD=/home/testpwn/ndk/toolchains/llvm/prebuilt/linux-x86_64/bin/ld64.lld
D='{"c2":"198.51.100.7:443","campaign":"pairing","sleep":45,"flag":"flag{dyl1b_p41r}"}'; P="${3:-$D}"
LEN=$(printf '%s' "$P" | wc -c)
CRC=$(printf '%s' "$P" | gzip -c | tail -c8 | head -c4 | od -An -tx4 | tr -d ' ')
BODY=$(perl -e 'print join ",", map { ord($_) } split //, $ARGV[0]' "$P")
cat > "$W/pair.c" <<C
struct hcfg { char m[4]; unsigned char ver, key; unsigned short len; unsigned int crc; unsigned char body[$LEN]; };
__attribute__((section("__DATA,__hcfg"), used)) const struct hcfg hcfg_blob = {{'H','C','F','G'}, 1, 0, $LEN, 0x$CRC, {$BODY}};
int pair_table[4] = {1, 2, 3, 4};
int pair_api(int x) { return x * 7 + hcfg_blob.len; }
const char *pair_ver(void) { return "2.1"; }
C
echo 'int weak_hook(int x) { return x + 1; }' > "$W/weak.c"
cat > "$W/main.c" <<'C'
#include <stdio.h>
int pair_api(int); int weak_hook(int) __attribute__((weak_import));
int main(int c, char **v) { printf("%d\n", pair_api(c) + (weak_hook ? weak_hook(c) : 0)); return 0; }
C
cat > "$W/main2.c" <<'C'
#include <stdio.h>
int pair_api(int); extern int pair_table[4];
int *tp = pair_table;
int main(int c, char **v) { printf("%d\n", pair_api(c) + tp[1]); return 0; }
C
mkdir -p "$W/sdk"; cat > "$W/sdk/libSystem.tbd" <<'T'
--- !tapi-tbd
tbd-version:     4
targets:         [ arm64-macos, x86_64-macos ]
install-name:    '/usr/lib/libSystem.B.dylib'
current-version: 1319
exports:
  - targets:     [ arm64-macos, x86_64-macos ]
    symbols:     [ _printf, dyld_stub_binder ]
...
T
x64dylibs() { Z -target x86_64-macos -shared -O2 -o libpair.dylib pair.c -Wl,-install_name,@rpath/libpair.dylib \
                -Wl,-current_version,2.1.0 -Wl,-compatibility_version,2.0.0
              Z -target x86_64-macos -shared -O2 -o libweak.dylib weak.c -Wl,-install_name,@loader_path/libweak.dylib; }
a64dylib() { Z -target aarch64-macos -O2 -c -o pair_a.o pair.c
             (cd "$W" && $LLD -arch arm64 -platform_version macos 15.0 15.0 -dylib -o libpair_cf.dylib pair_a.o \
                -install_name @rpath/libpair.dylib -fixup_chains -Lsdk -lSystem); }
case "$2" in
  x64_dylib) x64dylibs && cp "$W/libpair.dylib" "$O" ;;
  x64_app) x64dylibs && Z -target x86_64-macos -O2 -o app main.c -L. -lpair -Wl,-weak-lweak \
             -Wl,-rpath,@executable_path/../Frameworks -Wl,-rpath,@loader_path/lib && cp "$W/app" "$O" ;;
  a64cf_dylib) a64dylib && cp "$W/libpair_cf.dylib" "$O" ;;
  a64cf_app) a64dylib && Z -target aarch64-macos -O2 -c -o main_a.o main2.c && (cd "$W" && $LLD -arch arm64 \
             -platform_version macos 15.0 15.0 -o app_cf main_a.o -Lsdk -lSystem -L. -weak-lpair_cf \
             -rpath @executable_path/../Frameworks -rpath @loader_path -fixup_chains) && cp "$W/app_cf" "$O" ;;
  decoy_obj) Z -target aarch64-macos -O2 -c -o o.o main.c && cp "$W/o.o" "$O" ;;
  decoy_elf) (cd "$W" && gcc -O2 -shared -fPIC -o libpair.dylib weak.c) && cp "$W/libpair.dylib" "$O" ;;
esac
rm -rf "$W"
