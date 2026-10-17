#!/bin/bash
# usage: wasmhid_gen.sh out.wasm kind json key   (wat2wasm 1.0.36 --enable-annotations; blob packed by perl)
# kind: custom   (blob in a custom section named "hcfg" via (@custom "hcfg" ...), plus an ordinary active segment)
#     | passive  (blob 4 bytes into a passive segment; start func does memory.init seg -> linear address 8192)
#     | split    (blob cut 9 bytes into the body over two ADJACENT active segments 2048 / 2048+21, tail segment first
#                 in the file, a banner segment between them)
#     | store    (blob built by code: one `i32.const 4*i; i32.const word_i; i32.store offset=12288` per 4-byte LE word)
#     | splitgap (DECOY: like split but the tail segment 1 byte too far -> linear memory has a 0 byte in the body)
#     | storebad (DECOY: like store but header crc off by one)
# crc32 = gzip trailer of the JSON (coreutils), body = JSON xor key (perl).
set -e
P="$3"; K=$(( ${4:-0} )); W=$(mktemp -d)
CRC=$(printf '%s' "$P" | gzip -c | tail -c8 | head -c4 | od -An -tx4 | tr -d ' ')
[ "$2" = storebad ] && CRC=$(printf '%08x' $(( 0x$CRC ^ 1 )))
perl -e 'print pack("a4 C C v V", "HCFG", 1, $ARGV[1], length $ARGV[0], hex $ARGV[2]) .
  join "", map { chr(ord($_) ^ $ARGV[1]) } split //, $ARGV[0]' "$P" "$K" "$CRC" > "$W/blob"
esc() { perl -e 'local $/; $_ = <STDIN>; print join "", map { sprintf "\\%02x", ord } split //' ; }
ESC=$(esc < "$W/blob"); N=$(wc -c < "$W/blob")
HEAD=$(head -c 21 "$W/blob" | esc); TAIL=$(tail -c +22 "$W/blob" | esc)
case "$2" in
  custom) cat > "$W/m.wat" <<WAT
(module
  (memory (export "memory") 1)
  (data (i32.const 1024) "orchard beacon v3\00")
  (@custom "hcfg" "$ESC"))
WAT
  ;;
  passive) cat > "$W/m.wat" <<WAT
(module
  (memory (export "memory") 1)
  (data (i32.const 1024) "orchard beacon v3\00")
  (data \$p "pad\00$ESC")
  (func \$init (memory.init \$p (i32.const 8192) (i32.const 4) (i32.const $N)) (data.drop \$p))
  (start \$init))
WAT
  ;;
  split|splitgap) G=$([ "$2" = splitgap ] && echo 1 || echo 0); cat > "$W/m.wat" <<WAT
(module
  (memory (export "memory") 1)
  (data (i32.const $((2048 + 21 + G))) "$TAIL")
  (data (i32.const 1024) "orchard beacon v3\00")
  (data (i32.const 2048) "$HEAD"))
WAT
  ;;
  store|storebad) ST=$(perl -e 'local $/; $b = <STDIN>; $b .= "\0" x ((4 - length($b) % 4) % 4); $i = 0;
     print join "\n", map { sprintf "    (i32.store offset=12288 (i32.const %d) (i32.const 0x%08x))", 4 * $i++, $_ } unpack("V*", $b)' < "$W/blob")
     cat > "$W/m.wat" <<WAT
(module
  (memory (export "memory") 1)
  (data (i32.const 1024) "orchard beacon v3\00")
  (func \$build (export "build") (local i32)
    (local.set 0 (i32.const 7))
$ST
  ))
WAT
  ;;
esac
wat2wasm --enable-annotations -o "$1" "$W/m.wat"
rm -rf "$W"
