#!/bin/sh
# Independent reader: restore the scrubbed `UPX!` magic at the PackHeader/l_info positions of the unscrubbed twin,
# undo the section renames, run the REAL `upx -d` on a copy, then readelf -SW / pefile for the `.hcfg` section's file
# offset and a python crc/json parse of the blob there. usage: sh upx_oracle.sh <fixture.bin> [unscrubbed-twin.bin]
set -e; W=$(mktemp -d); cp "$1" "$W/x"; PY=${PY:-python3}
if [ -n "$2" ]; then $PY -c 'import sys;t=open(sys.argv[2],"rb").read();d=bytearray(open(sys.argv[1],"rb").read());i=t.find(b"UPX!")
while i>=0: d[i:i+4]=b"UPX!";i=t.find(b"UPX!",i+1)
d=bytes(d).replace(b".pk0\0",b"UPX0\0").replace(b".pk1\0",b"UPX1\0");open(sys.argv[1],"wb").write(d)' "$W/x" "$2"; fi
upx -d -q "$W/x" >/dev/null 2>&1 || { echo none; rm -rf "$W"; exit 0; }
if head -c4 "$W/x" | grep -q ELF; then
  off=$(readelf -SW "$W/x" | awk '$2==".hcfg"{print strtonum("0x"$5)}')
else
  off=$($PY -c 'import pefile,sys;p=pefile.PE(sys.argv[1]);print(next((s.PointerToRawData for s in p.sections if s.Name.rstrip(b"\0")==b".hcfg"),""))' "$W/x")
fi
[ -n "$off" ] || { echo none; rm -rf "$W"; exit 0; }
$PY -c 'import sys,struct,zlib,json;d=open(sys.argv[1],"rb").read();o=int(sys.argv[2]);v,k,n,c=struct.unpack_from("<BBHI",d,o+4);p=bytes(b^k for b in d[o+12:o+12+n]);print(o,json.dumps(json.loads(p)) if d[o:o+4]==b"HCFG" and zlib.crc32(p)==c else "none")' "$W/x" "$off"
rm -rf "$W"
