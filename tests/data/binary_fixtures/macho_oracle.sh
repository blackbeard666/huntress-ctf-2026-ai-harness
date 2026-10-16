#!/bin/bash
# usage: macho_oracle.sh file
# llvm-lipo-18 -archs + llvm-objdump-18 --macho --universal-headers (fat slice archs / offsets), llvm-readobj-18 --file-headers --sections per slice (CpuType,
# Segment,Name, section Offset), llvm-objcopy-18 --dump-section __DATA,__hcfg, perl unpack (little-endian header) +
# xor, gzip trailer = crc32(body). Prints per slice:
# <arch> | <CpuType> | <slice offset> | <segment,section list> | <abs __hcfg offset or none> | <hdr> <crc32(plain)> | <plain>
set -e
F="$1"; W=$(mktemp -d)
if llvm-lipo-18 -info "$F" 2>/dev/null | grep -q '^Architectures in the fat file'; then
  ARCHS=$(llvm-lipo-18 -archs "$F")
else ARCHS=thin; fi
for A in $ARCHS; do
  if [ $A = thin ]; then cp "$F" "$W/s.o"; BASE=0
  else llvm-lipo-18 -thin $A "$F" -output "$W/s.o"
       BASE=$(llvm-objdump-18 --macho --universal-headers "$F" | awk -v a=$A '$1=="architecture"{c=($2==a)} c&&$1=="offset"{print $2; exit}'); fi
  R=$(llvm-readobj-18 --file-headers --sections "$W/s.o")
  CPU=$(printf '%s\n' "$R" | sed -n 's/^ *CpuType: *//p')
  SECS=$(printf '%s\n' "$R" | awk '$1=="Name:"{n=$2} $1=="Segment:"{printf "%s,%s ", $2, n}')
  OFF=$(printf '%s\n' "$R" | awk '$1=="Name:"{n=$2} $1=="Offset:"&&n=="__hcfg"{print $2; exit}')
  if [ -n "$OFF" ]; then
    llvm-objcopy-18 --dump-section __DATA,__hcfg="$W/sec" "$W/s.o" "$W/junk"
    H=$(perl -e 'local $/; open F, $ARGV[0]; $d = <F>; ($m,$v,$k,$n,$c) = unpack("a4 C C v V", $d);
      $b = join "", map { chr(ord($_) ^ $k) } split //, substr($d, 12, $n); open O, ">$ARGV[1]"; print O $b; print "$m $v $k $n $c"' "$W/sec" "$W/p")
    PC=$(gzip -c < "$W/p" | tail -c8 | head -c4 | od -An -tu4 | tr -d ' ')
    echo "$A | $CPU | $BASE | $SECS| $((BASE + OFF)) | $H $PC | $(cat "$W/p")"
  else echo "$A | $CPU | $BASE | $SECS| none"; fi
done
rm -rf "$W"
