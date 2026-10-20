#!/bin/bash
# usage: hl_gen.sh out.bin kind json key form   (Haxe 4.3.7 Ubuntu deb unpacked under tools/neko/root; no hl VM needed)
# kind: hl (haxe -main Main -hl out.hl: HLB v4, debug flag 1) | nodebug (+ -D hl-no-debug: flags 0)
#       | trunc (hl output cut to its first 48 bytes: header + partial int table; decoy) | source (Main.hx itself; decoy)
# form: b64 (coreutils base64 -w0 of the blob) | utf8 (blob bytes as \u00NN escapes: the HL string table stores the
#       Haxe string UTF-8, so bytes >= 0x80 become C2/C3 xx pairs) | none
# blob = 'HCFG' u8 ver=1, u8 key, u16le len, u32le crc32 (gzip trailer, coreutils) + JSON xor key (perl).
set -e
OUT=$(realpath -m "$1"); P="$3"; K=$(( ${4:-0} )); F="$5"; W=$(mktemp -d)
R=$(realpath "$(dirname "$(realpath "$0")")/../../../tools/neko/root")
export LD_LIBRARY_PATH=$R/usr/lib/x86_64-linux-gnu HAXE_STD_PATH=$R/usr/share/haxe/std PATH=$R/usr/bin:$PATH
LEN=$(printf '%s' "$P" | wc -c)
{ printf 'HCFG\x01'; perl -e 'print pack("Cv", $ARGV[0], $ARGV[1])' "$K" "$LEN"
  printf '%s' "$P" | gzip -c | tail -c8 | head -c4
  perl -e 'print join "", map { chr(ord($_) ^ $ARGV[1]) } split //, $ARGV[0]' "$P" "$K"; } > "$W/blob"
case "$F" in
  b64) S=$(base64 -w0 "$W/blob") ;;
  utf8) S=$(perl -0777 -ne 'print map { sprintf "\\u%04x", ord } split //' "$W/blob") ;;
  *) S="hello hashlink" ;;
esac
printf 'class Main { static var CFG = "%s"; static var GREET = "hl-fixture"; static function main() { Sys.println(CFG.length + " " + GREET); } }\n' "$S" > "$W/Main.hx"
case "$2" in
  hl|trunc) (cd "$W" && haxe -main Main -hl out.hl) ;;
  nodebug) (cd "$W" && haxe -main Main -hl out.hl -D hl-no-debug) ;;
  source) cp "$W/Main.hx" "$W/out.hl" ;;
esac
if [ "$2" = trunc ]; then head -c 48 "$W/out.hl" > "$OUT"; else cp "$W/out.hl" "$OUT"; fi
rm -rf "$W"
