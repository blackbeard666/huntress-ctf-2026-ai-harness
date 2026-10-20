#!/bin/bash
# usage: beam_gen.sh out.bin kind json key form
# kind: beam (erlc, OTP 27: the binary literal lands in the zlib'd LitT chunk) | escript (escript:create shebang +
#       deflated zip archive holding the .beam) | strbeam (literal is a list string -> LitT STRING_EXT)
# form: raw (blob bytes as an Erlang binary literal, \xNN escapes) | b64 (coreutils base64 -w0 of the blob)
# BADCRC=1: header crc = 0xefbeadde (decoy). blob = 'HCFG' u8 ver=1, u8 key, u16le len, u32le crc32 (gzip trailer,
# coreutils) + JSON xor key (perl). erlang-base 27.3 from `apt-get download` + dpkg -x under tools/erlang-dl (no root).
set -e
OUT=$(realpath -m "$1"); P="$3"; K=$(( ${4:-0} )); F="$5"; W=$(mktemp -d)
ERL=$(dirname "$(realpath "$0")")/../../../tools/erlang-dl/root/usr/lib/erlang/bin; export PATH="$ERL:$PATH"
LEN=$(printf '%s' "$P" | wc -c)
{ printf 'HCFG\x01'; perl -e 'print pack("Cv", $ARGV[0], $ARGV[1])' "$K" "$LEN"
  if [ -n "$BADCRC" ]; then printf '\xde\xad\xbe\xef'; else printf '%s' "$P" | gzip -c | tail -c8 | head -c4; fi
  perl -e 'print join "", map { chr(ord($_) ^ $ARGV[1]) } split //, $ARGV[0]' "$P" "$K"; } > "$W/blob"
if [ "$F" = b64 ]; then S=$(base64 -w0 "$W/blob"); else S=$(perl -0777 -ne 'print map { sprintf "\\x%02x", ord } split //' "$W/blob"); fi
if [ "$2" = strbeam ]; then L="\"$S\""; else L="<<\"$S\">>"; fi
printf -- '-module(cfgmod).\n-export([main/1, cfg/0]).\ncfg() -> %s.\nmain(_) -> io:format("~p~n", [byte_size(iolist_to_binary(cfg()))]).\n' "$L" > "$W/cfgmod.erl"
(cd "$W" && erlc cfgmod.erl)
case "$2" in
  beam|strbeam) cp "$W/cfgmod.beam" "$OUT" ;;
  escript)
    (cd "$W" && erl -noshell -eval '{ok,B}=file:read_file("cfgmod.beam"), ok=escript:create("out.escript", [shebang, comment, {emu_args, "-escript main cfgmod"}, {archive, [{"cfgmod.beam", B}], []}]), halt().')
    cp "$W/out.escript" "$OUT" ;;
esac
rm -rf "$W"
