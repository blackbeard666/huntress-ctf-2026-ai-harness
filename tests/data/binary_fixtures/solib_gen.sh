#!/bin/bash
# usage: solib_gen.sh out kind json key [soname]
# kind: so (gcc -shared -fPIC, ET_DYN, optional -Wl,-soname) | o (gcc -c, ET_REL) | dll (zig cc -target
# x86_64-windows-gnu -shared via pip ziglang under tools/pyziglang, IMAGE_FILE_DLL + export directory)
# | exe (gcc -no-pie ET_EXEC, nothing exported: decoy).
# The HCFG blob is a C struct {char m[4]; u8 ver, key; u16 len; u32 crc; u8 body[]} in a `.hcfg` section (compiler
# writes the header); crc32 = gzip trailer of the JSON (coreutils), body = JSON xor key (perl). Exported API:
# hcfg_get_c2 / hcfg_get_sleep functions + hcfg_campaign data object (dllexport for the DLL).
set -e
P="$3"; K=$(( ${4:-0} )); W=$(mktemp -d)
LEN=$(printf '%s' "$P" | wc -c)
CRC=$(printf '%s' "$P" | gzip -c | tail -c8 | head -c4 | od -An -tx4 | tr -d ' ')
BODY=$(perl -e 'print join ",", map { ord($_) ^ $ARGV[1] } split //, $ARGV[0]' "$P" "$K")
X=""; [ "$2" = dll ] && X="__declspec(dllexport)"
[ "$2" = exe ] && X="static"
cat > "$W/m.c" <<C
struct hcfg { char m[4]; unsigned char ver, key; unsigned short len; unsigned int crc; unsigned char body[$LEN]; };
__attribute__((section(".hcfg"), used)) static const struct hcfg hcfg_blob = {{'H','C','F','G'}, 1, $K, $LEN, 0x$CRC, {$BODY}};
static unsigned char dec[$LEN + 1];
$X const char hcfg_campaign[] = "tower";
$X const char *hcfg_get_c2(void) { for (int i = 0; i < $LEN; i++) dec[i] = hcfg_blob.body[i] ^ hcfg_blob.key; return (const char *)dec; }
$X int hcfg_get_sleep(void) { return hcfg_blob.len; }
C
[ "$2" = exe ] && echo 'int main(void) { return hcfg_get_c2()[0] + hcfg_campaign[0] + hcfg_get_sleep(); }' >> "$W/m.c"
case "$2" in
  so)  gcc -O2 -fPIC -shared ${5:+-Wl,-soname,$5} -o "$1" "$W/m.c" ;;
  o)   gcc -O2 -c -o "$1" "$W/m.c" ;;
  exe) gcc -O2 -no-pie -o "$1" "$W/m.c" ;;
  dll) (cd "$W" && PYTHONPATH="$(cd "$(dirname "$0")/../../.." && pwd)/tools/pyziglang" python3 -m ziglang cc \
         -target x86_64-windows-gnu -shared -O2 -s -o "${5:-hcfg.dll}" m.c) && cp "$W/${5:-hcfg.dll}" "$1" ;;
esac
rm -rf "$W"
