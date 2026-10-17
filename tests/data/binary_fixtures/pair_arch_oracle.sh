#!/bin/bash
# Independent oracle for pair_arch_*.bin: `unzip -Z1` (CD order) + sha256sum, GNU readelf -hW (Machine/Class/Data/Type/
# Entry), `od` for the raw e_machine u16 (LE: EI_DATA=1 on all four arches). Machine label = readelf spelling, except
# readelf's "Advanced Micro Devices X86-64" -> "x86-64" (the GM-confirmed harness vocabulary). One JSON line per member.
# usage: bash pair_arch_oracle.sh pair_arch_x.bin
set -uo pipefail
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
unzip -q -o -j "$1" -d "$T" 2>/dev/null
unzip -Z1 "$1" | while read -r m; do
  f="$T/$(basename "$m")"; sha=$(sha256sum "$f" | cut -d' ' -f1)
  if ! readelf -h "$f" >/dev/null 2>&1; then
    jq -cn --arg m "$m" --arg s "$sha" '{member:$m, sha256:$s, elf:false}'; continue; fi
  h=$(readelf -hW "$f")
  mach=$(sed -n 's/^  Machine: *//p' <<<"$h"); [ "$mach" = "Advanced Micro Devices X86-64" ] && mach=x86-64
  cls=$(sed -n 's/^  Class: *ELF//p' <<<"$h"); dat=$(sed -n 's/^  Data: *.*, \(little\|big\) endian/\1/p' <<<"$h")
  typ=$(awk '/^  Type:/{print $2}' <<<"$h"); ent=$(awk '/Entry point/{print $4}' <<<"$h")
  num=$(od -An -tu2 -j18 -N2 "$f" | tr -d ' ')
  jq -cn --arg m "$m" --arg s "$sha" --arg ma "$mach" --arg n "$num" --argjson b "$cls" --arg d "$dat" --arg t "$typ" \
     --arg e "$ent" '{member:$m, sha256:$s, elf:true, machine:$ma, machine_num:$n, bits:$b, endian:$d,
                      elf_type:("ET_"+$t), entry_point:$e}'
done
