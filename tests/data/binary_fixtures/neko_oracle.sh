#!/bin/bash
# usage: neko_oracle.sh file.bin -> "file -b | neko VM run (exit) | boot trailer offset | first offset | HCFG ver key len crc crc32(body) | JSON"
# Independent readers only: file(1) (NekoVM magic: global symbols / fields / bytecode ops), the neko 2.4.1 VM itself
# (loads + runs the module: a truncated / impostor module fails to load), od on the `nekotools boot` trailer,
# grep -obUa for the offset, coreutils base64 + perl unpack/xor for the blob, gzip trailer crc32.
f=$(realpath "$1"); T=$(mktemp -d)
R=$(realpath "$(dirname "$(realpath "$0")")/../../../tools/neko/root")
export LD_LIBRARY_PATH=$R/usr/lib/x86_64-linux-gnu NEKOPATH=$R/usr/lib/x86_64-linux-gnu/neko
ft=$(file -b "$f")
if [[ "$ft" == ELF* ]]; then cp "$f" "$T/x"; chmod +x "$T/x"; run=$("$T/x" 2>&1 | head -1; echo "exit ${PIPESTATUS[0]}")
  boot=$(tail -c8 "$f" | head -c4)" "$(tail -c4 "$f" | od -An -tu4 | tr -d ' ')
else cp "$f" "$T/m.n"; run=$(cd "$T" && "$R/usr/bin/neko" m.n 2>&1 | tail -1; echo "exit ${PIPESTATUS[0]}"); boot=none; fi
off=$(grep -obUa -m1 -e HCFG -e SENGR "$f" | head -1 | cut -d: -f1)
grep -oaE -m1 'SENGR[A-Za-z0-9+/=]+' "$f" | head -1 | tr -d '\n' > "$T/s"
if [ -s "$T/s" ]; then S=$(cat "$T/s"); printf '%s' "${S:0:$(( ${#S} / 4 * 4 ))}" | base64 -d > "$T/b" 2>/dev/null
elif [ -n "$off" ]; then tail -c +$((off + 1)) "$f" > "$T/b"; else : > "$T/b"; fi
hdr=$(perl -e 'local $/; $_ = <STDIN>; exit unless length > 12; ($m, $v, $k, $n, $c) = unpack "a4CCvV"; $b = substr($_, 12, $n);
  $b =~ s/(.)/chr(ord($1) ^ $k)/ges; open F, ">", $ARGV[0]; print F $b; print "$m $v $k $n $c"' "$T/body" < "$T/b")
crc=$( [ -s "$T/body" ] && gzip -c < "$T/body" | tail -c8 | head -c4 | od -An -tu4 | tr -d ' ')
echo "$ft | $(echo $run) | $boot | ${off:-none} | ${hdr:-none} ${crc:-none} | $(cat "$T/body" 2>/dev/null)"
rm -rf "$T"
