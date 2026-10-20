#!/bin/bash
# usage: zsec_oracle.sh file.bin section   -- GNU readelf only (+ xxd/head, python3 json/zlib for the blob body)
# prints: the `readelf -S -W -t` entry (flags 0x800 COMPRESSED, ZLIB|ZSTD, ch_size, ch_addralign; sh_offset, sh_size),
# for a gnu .zdebug the 'ZLIB' magic + u64be size, and the decompressed HCFG blob from `readelf -z -x`
F=$1; S=$2
readelf -S -W -t "$F" | grep -A3 -F "] $S" | tr -s ' \n' ' '; echo
O=$((16#$(readelf -S -W "$F" | grep -F "] $S " | sed 's/^.*] *//' | awk '{print $4}')))
echo "sh_offset=$O"
[ "$(head -c $((O+4)) "$F" | tail -c 4 | tr -d "\0")" = ZLIB ] && echo "gnu ZLIB u64be_size=$((16#$(xxd -p -s $((O+4)) -l 8 "$F")))"
readelf -z -x "$S" "$F" | grep '^  0x' | cut -c14-48 | xxd -r -p > /tmp/zsec_plain.$$
python3 -c 'import sys,json,struct,zlib;d=open(sys.argv[1],"rb").read();i=d.find(b"HCFG");n,c=struct.unpack_from("<HI",d,i+6)
p=d[i+12:i+12+n];print("at+%d"%i,"crc_ok" if zlib.crc32(p)==c else "crc_BAD",p.decode(errors="replace"))' /tmp/zsec_plain.$$
rm -f /tmp/zsec_plain.$$
