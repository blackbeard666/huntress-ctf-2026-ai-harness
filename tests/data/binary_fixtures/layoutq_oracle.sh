#!/bin/bash
# Independent oracle for layoutq_* fixtures: grep -obaF (last magic), od (header ints, BE/LE, hash bytes), dd|sha256sum
# (region digests), stat (EOF). The layout spec is read by hand from the fixture's question (json "oracle_args"):
#   MAGIC m|f  name:off:u8|u16le|u16be|u32le|u32be|u64le  name:off:N (N-byte hex)  region:off|after:<len field>
# 'm' = offsets relative to the magic, 'f' = relative to the file. Prints a JSON object of canonical keys.
# usage: bash layoutq_oracle.sh <fixture.bin> "<oracle_args>"
f=$1; set -- $2; m=$1; mode=$2; shift 2
sz=$(stat -c %s "$f")
o=$(grep -obaF "$m" "$f" | tail -1 | cut -d: -f1)
if [ -z "$o" ]; then
  for a in "$@"; do echo "\"${a%%:*}\": \"none\""; done | paste -sd, | sed 's/^/{/;s/$/}/'; exit 0
fi
[ "$mode" = f ] && base=0 || base=$o
declare -A V; out="\"overlay_offset\": $o, \"overlay_size\": $((sz - o))"; end=""
for a in "$@"; do
  IFS=: read -r n off ty x <<<"$a"
  if [ "$off" = after ]; then ln=${V[$ty]}; s=$prev; else
  case $ty in
    u8|u16le|u16be|u32le|u32be|u64le|u64be)
      w=${ty//[^0-9]/}; e=little; [[ $ty == *be ]] && e=big
      v=$(od -An -tu$((w / 8)) --endian=$e -j$((base + off)) -N$((w / 8)) "$f" | tr -d ' ')
      V[$n]=$v; out+=", \"$n\": $v"; continue;;
    [0-9]*) v=$(od -An -tx1 -v -j$((base + off)) -N"$ty" "$f" | tr -d ' \n'); out+=", \"$n\": \"$v\""; continue;;
    *) ln=${V[$ty]}; s=$((base + off));;
  esac; fi
  e2=$((s + ln)); prev=$e2; end=$e2
  out+=", \"${n}_offset\": $((s - base)), \"${n}_start\": $s, \"${n}_end\": $e2"
  if [ $e2 -le $sz ]; then
    h=$(dd if="$f" bs=1 skip=$s count=$ln status=none | sha256sum | cut -d' ' -f1)
    out+=", \"${n}_body_size\": $ln, \"${n}_sha256_actual\": \"$h\""
  else out+=", \"${n}_body_size\": \"none\""; fi
done
[ -n "$end" ] && { [ "$end" -eq "$sz" ] && out+=", \"end_bounds_ok\": \"true\"" || out+=", \"end_bounds_ok\": \"false\""; }
echo "{$out}"
