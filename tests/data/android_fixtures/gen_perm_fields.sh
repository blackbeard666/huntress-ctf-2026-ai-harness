#!/bin/bash
# Permutation-codec fixtures (D17 `indexed` family): assets/huntress_puzzle.json built with perl (permute) + jq + zip.
#   scatter: r[o[i]] = d[i]  ->  d[i] = A[o[i]]        gather: r[i] = d[o[i]]  ->  d[o[i]] = A[i]
set -euo pipefail
OUT=$(cd "${1:?outdir}" && pwd)
# perm <len> <seed> <base>: a seeded Fisher-Yates shuffle of 0..len-1 (+base), comma separated
perm() { perl -e 'srand($ARGV[1]); @a=(0..$ARGV[0]-1); for($i=$#a;$i>0;$i--){$j=int(rand($i+1));@a[$i,$j]=@a[$j,$i]} print join ",", map {$_+$ARGV[2]} @a' "$@"; }
# enc <mode> <answer> <perm csv> <base>
enc() { perl -e '($m,$s,$p,$b)=@ARGV; @o=map{$_-$b}split/,/,$p; @c=split//,$s; @d=();
  if($m eq "scatter"){ @d=map{$c[$_]}@o } else { $d[$o[$_]]=$c[$_] for 0..$#o } print join "",@d' "$@"; }
mk() {  # name codec field perm-csv data
  local d; d=$(mktemp -d); mkdir -p "$d/assets"
  jq -cn --arg c "$2" --arg f "$3" --arg p "$4" --arg d "$5" \
    '{schema:"huntress.mobile.puzzle.v1",day:18,codec:$c,data:$d} + {($f): ($p|split(",")|map(tonumber))}' \
    > "$d/assets/huntress_puzzle.json"
  rm -f "$OUT/$1.apk"; (cd "$d" && zip -qX -r "$OUT/$1.apk" assets); rm -rf "$d"
}
P1=$(perm 20 1717 0); mk perm_indexed_scatter "indexed"    "order"     "$P1" "$(enc scatter ANS-7C19E04B5A2D86F3 "$P1" 0)"
P2=$(perm 20 4242 1); mk perm_shuffle_gather1 "shuffle_v2" "positions" "$P2" "$(enc gather  ANS-B03F6D2E91C4A758 "$P2" 1)"
P3=$(perm 20 9001 0); mk perm_decoy_nearmiss  "indexed"    "order"     "$P3" "$(enc scatter ANS-5E2A90C4D17B3F6G "$P3" 0)"
