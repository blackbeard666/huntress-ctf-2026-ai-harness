#!/bin/bash
# Independent oracle for pair_*.bin: Info-ZIP `unzip -Z1` (central-directory order) + sha256sum, GNU readelf
# (-h Type/Entry, -SW names, -lW INTERP, --dyn-syms UND, -dW NEEDED), `upx -t` for packed. One JSON line per member.
# usage: bash pair_oracle.sh pair_x.bin
set -uo pipefail
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
unzip -q -o -j "$1" -d "$T" 2>/dev/null
unzip -Z1 "$1" | while read -r m; do
  f="$T/$(basename "$m")"; sha=$(sha256sum "$f" | cut -d' ' -f1)
  if ! readelf -h "$f" >/dev/null 2>&1; then
    jq -cn --arg m "$m" --arg s "$sha" '{member:$m, sha256:$s, elf:false}'; continue; fi
  typ=$(readelf -hW "$f" | awk '/^  Type:/{print $2}'); ent=$(readelf -hW "$f" | awk '/Entry point/{print $4}')
  secs=$(readelf -SW "$f" 2>/dev/null | sed -n 's/^ *\[ *[0-9]*\] \(\S*\).*/\1/p' | sed 's/^NULL$//' | jq -R . | jq -sc .)
  [ "$secs" = "" ] && secs='[]'
  symtab=$(readelf -SW "$f" 2>/dev/null | grep -q ' SYMTAB ' && echo true || echo false)
  interp=$(readelf -lW "$f" 2>/dev/null | grep -q ' INTERP ' && echo true || echo false)
  dbg=$(readelf -SW "$f" 2>/dev/null | grep -q ' \.debug_info ' && echo true || echo false)
  imp=$(readelf --dyn-syms -W "$f" 2>/dev/null | awk '$7=="UND" && $8!="" {sub(/@.*/,"",$8); print $8}' | jq -R . | jq -sc .)
  need=$(readelf -dW "$f" 2>/dev/null | sed -n 's/.*(NEEDED).*\[\(.*\)\]/\1/p' | jq -R . | jq -sc .)
  packed=$(upx -t -q "$f" >/dev/null 2>&1 && echo true || echo false)
  jq -cn --arg m "$m" --arg s "$sha" --arg t "$typ" --arg e "$ent" --argjson sn "$secs" --arg st "$symtab" \
     --arg i "$interp" --arg d "$dbg" --argjson im "$imp" --argjson n "$need" --arg p "$packed" \
     '{member:$m, sha256:$s, elf:true, elf_type:("ET_"+$t), entry_point:$e, section_names:$sn, has_symtab:$st,
       has_interp:$i, has_debug_info:$d, imports:$im, needed:$n, is_packed:$p}'
done
