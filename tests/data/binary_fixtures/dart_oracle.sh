#!/bin/bash
# Independent oracle for dart_* fixtures: prints key=value lines from file -b, tail|od (dart2native trailer),
# dd + readelf -W --dyn-syms/-S/-n (snapshot ELF), od at the symbol's file offset (snapshot header), strings -a (Dart
# version banner), grep -obUaP (HCFG raw offset / SENGR base64 offset) + base64 -d / tail -c+13 (config JSON).
F="$1"; T=$(mktemp -d); SZ=$(stat -c %s "$F")
echo "file=$(file -b "$F" | cut -d, -f1)"
TRL=$(tail -c8 "$F" | od -An -tx1 | tr -d ' \n')
if [ "$TRL" = "dcdcf6f600000000" ]; then
  OFF=$(tail -c16 "$F" | head -c8 | od -An -tu8 | tr -d ' '); echo "packaging=appended snapshot_offset=$OFF snapshot_size=$((SZ-16-OFF))"
  dd if="$F" of="$T/s" bs=1 skip=$OFF count=$((SZ-16-OFF)) status=none
else OFF=0; cp "$F" "$T/s"; readelf -W --dyn-syms "$T/s" 2>/dev/null | grep -q _kDart && echo "packaging=standalone snapshot_offset=0 snapshot_size=$SZ"; fi
readelf -W --dyn-syms "$T/s" 2>/dev/null | awk '$8 ~ /^_kDart/ {print $8}' | sort -u | tr '\n' ' ' | sed 's/^/symbols=/; s/$/\n/'
for n in _kDartVmSnapshotData _kDartVmSnapshotInstructions _kDartIsolateSnapshotData _kDartIsolateSnapshotInstructions; do
  L=$(readelf -W --dyn-syms "$T/s" 2>/dev/null | awk -v n=$n '$8==n {print $2, $7; exit}'); [ -z "$L" ] && continue
  V=$((16#${L% *})); NDX=${L#* }
  S=$(readelf -W -S "$T/s" | sed 's/\[ */[/' | awk -v k="[$NDX]" '$1==k {print $4, $5}')
  FO=$(( OFF + 16#${S#* } + V - 16#${S% *} )); echo "$n=$FO"
  case $n in *Data) [ "$n" = _kDartIsolateSnapshotData ] && {
    echo "magic=$(od -An -tx4 -j$FO -N4 "$F" | tr -d ' ') kind=$(od -An -td8 -j$((FO+12)) -N8 "$F" | tr -d ' ')"
    echo "hash=$(dd if="$F" bs=1 skip=$((FO+20)) count=32 status=none)"
    echo "features=$(dd if="$F" bs=1 skip=$((FO+52)) count=400 status=none | tr '\0' '\n' | head -1)"; } ;; esac
done
echo "build_id=$(readelf -n "$T/s" 2>/dev/null | awk '/Build ID/ {print $3; exit}')"
echo "banner=$(strings -a "$F" | grep -m1 -E '^[0-9]+\.[0-9]+\.[0-9]+.* \((stable|beta|dev|main)\) .* on "')"
R=$(grep -obUaP 'HCFG\x01' "$F" | head -1 | cut -d: -f1)
if [ -n "$R" ]; then echo "hcfg_raw_offset=$R"; echo "config=$(tail -c +$((R+13)) "$F" | head -c $(( $(od -An -tu2 -j$((R+6)) -N2 "$F") )))"; fi
B=$(grep -obUa 'SENGR[A-Za-z0-9+/=]*' "$F" | head -1)
if [ -n "$B" ]; then echo "hcfg_b64_offset=${B%%:*}"; echo "config=$(echo "${B#*:}" | base64 -d 2>/dev/null | tail -c +13)"; fi
rm -rf "$T"
