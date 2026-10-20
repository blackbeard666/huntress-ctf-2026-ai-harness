#!/bin/bash
# Regenerates the xam_* fixtures. DLLs: tools/pwsh/pwsh -NoProfile -File mk.ps1 (Roslyn via Add-Type).
# XALZ: lz4.block writer; v1 assemblies.blob: `pyxamstore pack`; .NET 8 blob.so: gcc -shared + objcopy --add-section.
set -e
cd "$(dirname "$0")"; ROOT=../../../..; PY=$ROOT/.venv/bin/python; W=$(mktemp -d)
xalz() { $PY -I -c 'import sys,struct,lz4.block;d=open(sys.argv[1],"rb").read();open(sys.argv[2],"wb").write(b"XALZ"+struct.pack("<II",int(sys.argv[3]),len(d))+lz4.block.compress(d,store_size=False))' "$@"; }
# 1. per-assembly XALZ (Xamarin.Android <= 11 assemblies/*.dll)
mkdir -p $W/a/assemblies; xalz gate.dll $W/a/assemblies/HuntressGate.dll 0; cp util.dll $W/a/assemblies/Util.dll
printf 'dex\n035\0' > $W/a/classes.dex; (cd $W/a && zip -qX -r ../xam_xalz_dll.apk .)
# 2. assemblies.blob v1 (pyxamstore pack: XABA header, 24-byte descriptors, hash32/hash64 tables, lz4 XALZ entries)
mkdir -p $W/b && cp gate2.dll util.dll $W/b/ && (cd $W/b && cat > assemblies.json <<'J'
{"stores":[{"assemblies.blob":{"header":{"version":1,"lec":2,"gec":2,"store_id":0}}}],
 "assemblies":[{"name":"Util","file":"util.dll","lz4":false,"lz4_desc_idx":0,"store_id":0,"blob_idx":0,"hash32":"0","hash64":"0"},
               {"name":"HuntressGate2","file":"gate2.dll","lz4":true,"lz4_desc_idx":1,"store_id":0,"blob_idx":1,"hash32":"1","hash64":"1"}]}
J
$ROOT/.venv/bin/pyxamstore pack -c assemblies.json >/dev/null && mkdir -p apk/assemblies && mv assemblies.blob.new apk/assemblies/assemblies.blob \
 && mv assemblies.manifest.new apk/assemblies/assemblies.manifest && printf 'dex\n035\0' > apk/classes.dex && cd apk && zip -qX -r ../../xam_blob_v1.apk .)
# 3. .NET 8 store v2 inside the `payload` section of lib/arm64-v8a/libassemblies.arm64-v8a.blob.so
xalz gate.dll $W/g.xalz 0; $PY -I -c 'import sys,struct
u=open(sys.argv[1],"rb").read(); g=open(sys.argv[2],"rb").read(); n=2; idx=b"".join(struct.pack("<QI",h,i) for i,h in enumerate((0x1111,0x2222)))
names=b"".join(struct.pack("<I",len(s))+s for s in (b"Util.dll",b"HuntressGate.dll")); base=20+len(idx)+28*n+len(names)
desc=struct.pack("<7I",0,base,len(u),0,0,0,0)+struct.pack("<7I",1,base+len(u),len(g),0,0,0,0)
open(sys.argv[3],"wb").write(b"XABA"+struct.pack("<4I",0x80000002,n,n,len(idx))+idx+desc+names+u+g)' util.dll $W/g.xalz $W/store2.bin
echo 'int xa_stub(void){return 0;}' > $W/s.c && gcc -shared -fPIC -o $W/s.so $W/s.c && objcopy --add-section payload=$W/store2.bin $W/s.so $W/blob.so
mkdir -p $W/c/lib/arm64-v8a && cp $W/blob.so $W/c/lib/arm64-v8a/libassemblies.arm64-v8a.blob.so && printf 'dex\n035\0' > $W/c/classes.dex && (cd $W/c && zip -qX -r ../xam_net8_blobso.apk .)
# 4. decoy: near-miss literal (ANS-...ZZ) in an XALZ dll + a truncated XABA impostor
mkdir -p $W/d/assemblies; xalz decoy.dll $W/d/assemblies/HuntressGate.dll 0; head -c 600 $W/b/apk/assemblies/assemblies.blob > $W/d/assemblies/assemblies.blob
printf 'dex\n035\0' > $W/d/classes.dex; (cd $W/d && zip -qX -r ../xam_decoy_nearmiss.apk .)
cp $W/*.apk ..; rm -rf $W
