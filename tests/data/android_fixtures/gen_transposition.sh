#!/bin/bash
# Keyless transposition fixtures (Row 36, no index list in the JSON): perl encoders + jq + zip.
#   every encoder writes data[j] = answer[o[j]] for the family's read order o.
set -euo pipefail
OUT=$(cd "${1:?outdir}" && pwd)
# stride <answer> <k> <off>: data[j] = a[(k*j+off) mod n]   (D17's slot map was 3+7i mod 20)
stride() { perl -e '($s,$k,$o)=@ARGV; @c=split//,$s; $n=@c; print join "", map {$c[($k*$_+$o)%$n]} 0..$n-1' "$@"; }
# columnar <answer> <colorder csv>: write row-wise, read the columns in the given order
columnar() { perl -e '($s,$k)=@ARGV; @c=split//,$s; @k=split/,/,$k; $w=@k; $o="";
  for $col (@k){ for($i=$col;$i<@c;$i+=$w){ $o.=$c[$i] } } print $o' "$@"; }
# rail <answer> <rails>: zig-zag rail fence, rails read top to bottom
rail() { perl -e '($s,$r)=@ARGV; @c=split//,$s; @rows=map{""}1..$r; $y=0; $d=1;
  for $ch (@c){ $rows[$y].=$ch; $d=-$d if ($y==0&&$d<0)||($y==$r-1&&$d>0); $y+=$d } print join "",@rows' "$@"; }
# fy <answer> <seed>: seeded Fisher-Yates (no family) -- decoy
fy() { perl -e '($s,$sd)=@ARGV; srand($sd); @a=split//,$s; for($i=$#a;$i>0;$i--){$j=int(rand($i+1));@a[$i,$j]=@a[$j,$i]} print @a' "$@"; }
mk() {  # name codec data [extra json object, e.g. the public shape {"rails":8}]
  local d; d=$(mktemp -d); mkdir -p "$d/assets"
  jq -cn --arg c "$2" --arg d "$3" --argjson x "${4:-{\}}" '{schema:"huntress.mobile.puzzle.v1",day:18,codec:$c,data:$d} + $x' \
    > "$d/assets/huntress_puzzle.json"
  rm -f "$OUT/$1.apk"; (cd "$d" && zip -qX -r "$OUT/$1.apk" assets); rm -rf "$d"
}
mk tp_stride_3p7i      "slotmap"    "$(stride   ANS-4D8E1F07C2B9A635 7 3)"
mk tp_columnar_keyed5  "columnar"   "$(columnar ANS-E61C0B937F2D48A5 2,0,4,1,3)"
mk tp_rail8            "zigzag"     "$(rail     ANS-90B7D3C1E5F2864A 8)" '{"rails":8}'
mk tp_decoy_nearmiss   "slotmap"    "$(stride   ANS-3C5E7A9B1D0F246G 7 3)"
mk tp_decoy_fyshuffle  "scramble"   "$(fy       ANS-71F0C3E95A2B8D46 31337)"
