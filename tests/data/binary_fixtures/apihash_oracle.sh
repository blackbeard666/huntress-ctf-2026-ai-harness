#!/bin/bash
# apihash_oracle.sh <bin> <algo>: objdump -d immediates (code order) + objdump -s .rodata dwords, mapped through the
# independent perl hasher over a candidate dictionary -> "file? | names in address order | hashes".
here=$(cd "$(dirname "$0")" && pwd); f=$1 algo=$2
dict="getenv printf puts exit system socket connect VirtualAlloc CreateThread LoadLibraryA GetProcAddress malloc free"
declare -A N; while read -r h n; do N[$h]=$n; done < <(perl "$here/apihash_hash.pl" "$algo" $dict)
{ objdump -d --no-show-raw-insn "$f" | grep -oE '^ *[0-9a-f]+:|\$0x[0-9a-f]+' | tr -d '$' | awk '/:$/{a=$1;next}{print a, $1}'
  objdump -s -j .rodata "$f" 2>/dev/null | awk 'NF>=2 && $1 ~ /^[0-9a-f]+$/ {for (i=2;i<=5&&i<=NF;i++) if ($i ~ /^[0-9a-f]{8}$/) print $1, "le" $i}' ;
} | while read -r a v; do
  if [[ $v == le* ]]; then v=0x${v:8:2}${v:6:2}${v:4:2}${v:2:2}; fi
  v=$(printf '0x%08x' $((v))); [ -n "${N[$v]:-}" ] && echo "$a ${N[$v]} $v"
done | awk '!seen[$2]++' | tr '\n' ';'; echo
