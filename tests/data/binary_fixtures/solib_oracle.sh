#!/bin/bash
# usage: solib_oracle.sh file
# ELF: GNU readelf -h (Type / Entry point), readelf -dW (SONAME), readelf -lW (INTERP), nm -D --defined-only (ET_DYN) or
# nm -g --defined-only (ET_REL), LC_ALL=C sorted. PE: GNU objdump -p (Characteristics DLL flag, AddressOfEntryPoint,
# export Name + [Ordinal/Name Pointer] names). HCFG: objdump -h (.hcfg file offset), objcopy --only-section=.hcfg, perl
# unpack + xor, gzip trailer crc32. Prints:
# <type> | <entry> | <soname/dllname> | <interp?> | <exports,> | <.hcfg off> | <ver key len crc crc32(plain)> | <plain>
F="$1"; W=$(mktemp -d); export LC_ALL=C
if readelf -h "$F" >/dev/null 2>&1; then
  T=$(readelf -h "$F" | sed -n 's/^ *Type: *\([A-Z]*\).*/\1/p'); E=$(readelf -h "$F" | sed -n 's/^ *Entry point address: *//p')
  S=$(readelf -dW "$F" 2>/dev/null | sed -n 's/.*(SONAME).*\[\(.*\)\]/\1/p'); I=$(readelf -lW "$F" 2>/dev/null | grep -c 'INTERP')
  [ "$T" = REL ] && NM="nm -g --defined-only" || NM="nm -D --defined-only"
  X=$($NM "$F" 2>/dev/null | awk '$2 ~ /^[TDRBWV]$/ {print $3}' | sort | paste -sd,)
  echo -n "ET_$T | $E | ${S:-none} | $I | ${X:-none} | "
elif objdump -p "$F" 2>/dev/null | grep -q '^Characteristics'; then
  D=$(objdump -p "$F" | grep -A12 '^Characteristics' | grep -c 'DLL'); E=$(objdump -p "$F" | awk '/^AddressOfEntryPoint/{print $2}')
  N=$(objdump -p "$F" | awk '/^Name[ \t]/{print $NF; exit}')
  X=$(objdump -p "$F" | awk '/Ordinal\/Name Pointer\] Table/{f=1; next} f && /^\t\[/ {print $NF} f && /^$/{f=0}' | sort | paste -sd,)
  echo -n "PE dll=$D | 0x$E | ${N:-none} | 0 | ${X:-none} | "
else echo "not ELF/PE: $(file -b "$F")"; rm -rf "$W"; exit 0; fi
OFF=$(objdump -h "$F" | awk '$2==".hcfg"{print $6}')
objcopy -O binary --only-section=.hcfg "$F" "$W/s" 2>/dev/null
H=$(perl -e 'local $/; open F, $ARGV[0]; $d = <F>; ($m,$v,$k,$n,$c) = unpack("a4 C C v V", $d);
  $b = join "", map { chr(ord($_) ^ $k) } split //, substr($d, 12, $n); open O, ">$ARGV[1]"; print O $b; print "$m $v $k $n $c"' "$W/s" "$W/p")
PC=$(gzip -c < "$W/p" | tail -c8 | head -c4 | od -An -tu4 | tr -d ' ')
echo "$((16#$OFF)) | $H $PC | $(cat "$W/p")"
rm -rf "$W"
