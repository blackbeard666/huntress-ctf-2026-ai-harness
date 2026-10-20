#!/bin/bash
# Independent oracle: readelf (image end = max of shoff+shnum*shentsize and phdr/segment ends), grep -b (last magic),
# od (header bytes), dd|sha256sum (packed sha). usage: bash ovhdr_oracle.sh <file.bin> <MAGIC>
f=$1; m=$2; sz=$(stat -c %s "$f")
shoff=$(readelf -hW "$f" | awk -F: '/Start of section headers/{print $2+0}')
shn=$(readelf -hW "$f" | awk -F: '/Number of section headers/{print $2+0}')
she=$(readelf -hW "$f" | awk -F: '/Size of section headers/{print $2+0}')
echo "size=$sz image_end=$((shoff + shn * she))"
o=$(grep -obaF "$m" "$f" | tail -1 | cut -d: -f1)
[ -z "$o" ] && { echo "magic=none"; exit 0; }
read -r v k1 k2 pad <<<"$(od -An -tu1 -j$((o+4)) -N4 "$f")"
n=$(od -An -tu4 --endian=little -j$((o+8)) -N4 "$f" | tr -d ' ')
sha=$(od -An -tx1 -v -j$((o+12)) -N32 "$f" | tr -d ' \n')
psha=$(dd if="$f" bs=1 skip=$((o+44)) count=$n status=none | sha256sum | cut -d' ' -f1)
printf 'offset=%d size=%d version=%d k1=0x%02x k2=0x%02x pad=%d packed_length=%d unpacked_sha256=%s packed_sha256=%s\n' \
  "$o" $((sz-o)) "$v" "$k1" "$k2" "$pad" "$n" "$sha" "$psha"
