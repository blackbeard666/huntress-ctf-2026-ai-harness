#!/bin/bash
# Independent facts for a route_*.bin: member order (unzip -Z1), ELF type / INTERP / NEEDED / SONAME / defined dynamic
# exports (readelf), literal dlopen paths (strings), and every HCFG header's crc validity (grep -obUa + python3 binascii).
set -e
Z=$(readlink -f "$1"); D=$(mktemp -d); cd "$D"; unzip -q "$Z"
for m in $(unzip -Z1 "$Z"); do
  echo "== $m"; file -b "$m" | cut -c1-70
  if readelf -h "$m" >/dev/null 2>&1; then
    readelf -hW "$m" | awk '/Type:/{print "  type", $2}'
    readelf -lW "$m" | grep -q INTERP && echo "  interp yes" || echo "  interp no"
    readelf -dW "$m" | awk '/NEEDED|SONAME/{print "  " $2, $NF}'
    readelf --dyn-syms -W "$m" | awk '$7!="UND" && ($4=="FUNC"||$4=="OBJECT") && $5!="LOCAL"{print "  export", $8}' | grep -v '@' || true
    strings -a "$m" | grep -E '^\./lib.*\.so$' | sed 's/^/  dlopen /' || true
  fi
  for o in $(grep -obUa HCFG "$m" | cut -d: -f1); do
    python3 -c "import binascii,struct,sys;b=open(sys.argv[1],'rb').read()[int(sys.argv[2]):];
v,k,n,c=struct.unpack('<BBHI',b[4:12]) if len(b)>=12 else (0,0,0,0);p=bytes(x^k for x in b[12:12+n])
print('  hcfg@%s'%sys.argv[2],'crc_ok' if n and len(p)==n and binascii.crc32(p)==c else 'crc_bad')" "$m" "$o"
  done
done
rm -rf "$D"
