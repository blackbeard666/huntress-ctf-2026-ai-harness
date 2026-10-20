#!/bin/bash
# usage: neko_gen.sh out.bin kind json key form   (Neko VM 2.4.1 / Haxe 4.3.7 Ubuntu debs unpacked under tools/neko/root)
# kind: nekoc (raw Neko source -> nekoc) | haxe (haxe -neko out.n) | boot (nekoc, then `nekotools boot` = neko ELF + module)
#       | trunc (nekoc module cut to its first 60 bytes: header + partial globals; decoy)
# form: raw (blob bytes as the string literal, nekoc decimal \NNN escapes) | b64 (coreutils base64 -w0 of the blob) | none
# blob = 'HCFG' u8 ver=1, u8 key, u16le len, u32le crc32 (gzip trailer, coreutils) + JSON xor key (perl).
set -e
OUT=$(realpath -m "$1"); P="$3"; K=$(( ${4:-0} )); F="$5"; W=$(mktemp -d)
R=$(realpath "$(dirname "$(realpath "$0")")/../../../tools/neko/root")
export LD_LIBRARY_PATH=$R/usr/lib/x86_64-linux-gnu NEKOPATH=$R/usr/lib/x86_64-linux-gnu/neko HAXE_STD_PATH=$R/usr/share/haxe/std
export PATH=$R/usr/bin:$PATH
LEN=$(printf '%s' "$P" | wc -c)
{ printf 'HCFG\x01'; perl -e 'print pack("Cv", $ARGV[0], $ARGV[1])' "$K" "$LEN"
  printf '%s' "$P" | gzip -c | tail -c8 | head -c4
  perl -e 'print join "", map { chr(ord($_) ^ $ARGV[1]) } split //, $ARGV[0]' "$P" "$K"; } > "$W/blob"
case "$F" in
  b64) S=$(base64 -w0 "$W/blob") ;;
  raw) S=$(perl -0777 -ne 'print map { sprintf "\\%03d", ord } split //' "$W/blob") ;;
  *) S="hello neko" ;;
esac
case "$2" in
  nekoc|boot|trunc)
    printf 'var cfg = "%s";\nvar greet = "neko-fixture";\nvar f = function(a, b) { return a + b; };\n$print($ssize(cfg) + f(1, 2), " ", greet, "\\n");\n' "$S" > "$W/m.neko"
    (cd "$W" && nekoc m.neko)
    if [ "$2" = boot ]; then (cd "$W" && nekotools boot m.n && cp m "$OUT")
    elif [ "$2" = trunc ]; then head -c 60 "$W/m.n" > "$OUT"
    else cp "$W/m.n" "$OUT"; fi ;;
  haxe)
    printf 'class Main { static var CFG = "%s"; static function main() { Sys.println(CFG.length); } }\n' "$S" > "$W/Main.hx"
    (cd "$W" && haxe -main Main -neko out.n) && cp "$W/out.n" "$OUT" ;;
esac
rm -rf "$W"
