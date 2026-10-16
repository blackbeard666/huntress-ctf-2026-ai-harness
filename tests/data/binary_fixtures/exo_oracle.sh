#!/bin/bash
# usage: exo_oracle.sh file.bin mode -> "<offset> at+N <magic> <len> <hdr crc> <crc32(body) via gzip trailer> <body>"
# independent reader: perl offset of the stored form + coreutils base64 -d / xxd -r + binary-refinery units
# (zstd = refinery zstd unit on pyzstd, lz4 = system liblz4 LZ4F_decompress via exo_lz4dec.py) -- never lib.binary
H=/home/testpwn/huntress-2026
f="$1"
off=$(perl -0777 -ne 'print $-[0]+12 if /GetConfig\0\0\0/' "$f")
case "$2" in
  b64-*) dec() { tail -c +$((off+1)) "$f" | tr -d '\0' | head -c 200000 | grep -ao '^[A-Za-z0-9+/=]*' | head -1 | base64 -d; } ;;
  hex-*) dec() { tail -c +$((off+1)) "$f" | grep -ao '^[0-9a-f]*' | head -1 | xxd -r -p; } ;;
  raw-*) dec() { tail -c +$((off+1)) "$f"; } ;;
esac
case "$2" in *-zstd) un() { "$H/.venv/bin/zstd" 2>/dev/null; } ;; *-lz4) un() { /usr/bin/python3 -I "$H/tests/data/binary_fixtures/exo_lz4dec.py" 2>/dev/null; } ;; esac
dec | un | perl -0777 -ne '$i=index($_,"HCFG"); exit 1 if $i<0; $_=substr($_,$i); ($m,$v,$k,$l,$c)=unpack("a4CCvV",$_); $b=substr($_,12,$l);
  open(G,"|-","gzip -c | tail -c8 | head -c4 | od -An -tu4 | tr -d \" \\n\" > /tmp/exo_crc.$$"); print G $b; close G; open(R,"/tmp/exo_crc.$$"); $r=<R>; unlink "/tmp/exo_crc.$$";
  print "'"$off"' at+$i $m $l $c $r $b\n"' || echo "$off none"
