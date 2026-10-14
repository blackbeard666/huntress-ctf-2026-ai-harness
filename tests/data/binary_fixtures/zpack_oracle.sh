#!/bin/bash
# usage: zpack_oracle.sh file.bin mode  -> "<offset> <magic> <len> <hdr crc> <crc32(body) via gzip trailer> <body>"
# independent reader: strings/grep -bo + coreutils base64 / xxd -r / gzip / bzip2 / xz / zlib-flate (never lib.binary)
f="$1"
case "$2" in
  b64-*|hex-*) enc=$(strings -n 64 "$f" | grep -v GetConfig | head -1 | sed 's/^cfg=//');
     [[ "$2" == b64-bz2 ]] && enc=$(perl -0777 -ne 'print $1 if /GetConfig\0+([A-Za-z0-9+\/=\n]+)\0/' "$f")
     off=$(grep -boa -F -- "${enc%%$'\n'*}" "$f" | head -1 | cut -d: -f1)
     if [[ "$2" == b64-* ]]; then dec() { printf '%s' "$enc" | base64 -di; }; else dec() { printf '%s' "$enc" | xxd -r -p; }; fi ;;
  raw-*) off=$(perl -0777 -ne 'print $-[0]+12 if /GetConfig\0\0\0/' "$f"); dec() { tail -c +$((off+1)) "$f"; } ;;
esac
case "$2" in
  *-gzip|*-gzipU) un() { gzip -dc 2>/dev/null; } ;; *-zlib) un() { zlib-flate -uncompress 2>/dev/null; } ;;
  *-bz2) un() { bzip2 -dc 2>/dev/null; } ;; *-xz) un() { xz -dc --single-stream 2>/dev/null; } ;; *-lzma) un() { xz --format=lzma --single-stream -dc 2>/dev/null; } ;;
esac
dec | un | perl -0777 -ne '$i=index($_,"HCFG"); exit 1 if $i<0; $_=substr($_,$i); ($m,$v,$k,$l,$c)=unpack("a4CCvV",$_); $b=substr($_,12,$l);
  open(G,"|-","gzip -c | tail -c8 | head -c4 | od -An -tu4 | tr -d \" \\n\" > /tmp/zp_crc.$$"); print G $b; close G; open(R,"/tmp/zp_crc.$$"); $r=<R>; unlink "/tmp/zp_crc.$$";
  print "'"$off"' at+$i $m $l $c $r $b\n"' || echo "$off none"
