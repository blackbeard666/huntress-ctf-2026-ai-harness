#!/bin/bash
# usage: bytecode_oracle.sh file.bin -> "file -b | version fact | first offset | HCFG ver key len crc crc32(body) | JSON"
# Independent readers only: file(1); version from javap -v (class), /usr/bin/python3.14 marshal + magic (pyc),
# luac5.4 -l (luac), llvm-dis-18 / llvm-bcanalyzer-18 (bitcode); offset grep -obUa (verbatim forms only);
# the string constant is taken from llvm-dis-18 (bitcode) or grep -oa (others), decoded with coreutils base64 + perl.
f="$1"; T=$(mktemp -d)
ft=$(file -b "$f")
case "$ft" in
  *"Java class"*) cp "$f" "$T/M.class"; ver=$(javap -v "$T/M.class" 2>/dev/null | sed -n 's/.*major version: //p') ;;
  *"Lua bytecode"*) ver=$(luac5.4 -l -p "$f" >/dev/null 2>&1 && echo "lua ${ft##*version }") ;;
  *"LLVM"*) ver=$(llvm-dis-18 -o - "$f" 2>/dev/null | sed -n 's/^target triple = "\(.*\)"/\1/p') ;;
  *"Dalvik dex"*) ver=$(head -c7 "$f" | tail -c3) ;;
  *) ver=$(/usr/bin/python3.14 -I -c 'import sys, marshal; d = open(sys.argv[1], "rb").read(); marshal.loads(d[16:]); print("pyc", int.from_bytes(d[:2], "little"))' "$f" 2>/dev/null) ;;
esac
off=$(grep -obUa -m1 -e HCFG -e SENGR "$f" | head -1 | cut -d: -f1)
if [[ "$ft" == *LLVM* ]]; then
  llvm-dis-18 -o - "$f" | perl -ne 'if (/^\@cfg = .*c"(.*)\\00"/) { ($s = $1) =~ s/\\([0-9A-Fa-f]{2})/chr hex $1/ge; print $s }' > "$T/s"
else
  grep -oaE -m1 'SENGR[A-Za-z0-9+/=]+|HCFG.*' "$f" | head -1 | tr -d '\n' > "$T/s"
fi
# base64: whole 4-char groups only (marshal's TYPE_NONE 'N' may follow an unpadded run); raw: the file from the 'H'
if head -c5 "$T/s" | grep -q SENGR; then S=$(cat "$T/s"); printf '%s' "${S:0:$(( ${#S} / 4 * 4 ))}" | base64 -d > "$T/b" 2>/dev/null
elif [ -n "$off" ]; then tail -c +$((off + 1)) "$f" > "$T/b"; else cp "$T/s" "$T/b"; fi
hdr=$(perl -e 'local $/; $_ = <STDIN>; ($m, $v, $k, $n, $c) = unpack "a4CCvV"; $b = substr($_, 12, $n);
  $b =~ s/(.)/chr(ord($1) ^ $k)/ges; open F, ">", $ARGV[0]; print F $b; print "$m $v $k $n $c"' "$T/body" < "$T/b")
crc=$( [ -s "$T/body" ] && gzip -c < "$T/body" | tail -c8 | head -c4 | od -An -tu4 | tr -d ' ')
echo "$ft | ${ver:-none} | ${off:-none} | ${hdr:-none} ${crc:-none} | $(cat "$T/body" 2>/dev/null)"
rm -rf "$T"
