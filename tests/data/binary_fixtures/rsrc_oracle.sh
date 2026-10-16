#!/bin/bash
# Independent readers for the rsrc_* fixtures: pefile / 7z (PE resources, PE overlay), dnfile (.NET ManifestResource
# table), lief + readelf (ELF overlay), unzip/zipinfo + a struct read of the zip local header (jar entries); the blob is
# parsed by perl (magic ver key len crc) and its crc re-computed by gzip's trailer. usage: bash rsrc_oracle.sh FIXTURE_DIR
PY=${PY:-python3}; case $PY in */*) PY=$(cd "$(dirname "$PY")" && pwd)/$(basename "$PY");; esac; cd "${1:-.}"
parse() { perl -0777 -ne '($m,$v,$k,$l,$c)=unpack("a4CCvV",$_);print "$m v=$v key=$k len=$l crc=$c body=",substr($_,12,$l),"\n"'; }
crc() { local b L; b=$(mktemp); cat > "$b"; L=$(perl -0777 -ne 'print unpack("x6v",$_)' "$b")   # crc32 of the body via gzip
  head -c $((12+L)) "$b" | tail -c "$L" | gzip -c | tail -c8 | head -c4 | od -An -tu4 | tr -d ' '; rm -f "$b"; }
at() { grep -abo HCFG "$1" | head -1 | cut -d: -f1; }
echo "== rsrc_pe_rcdata.bin"; 7z l -slt rsrc_pe_rcdata.bin | grep -E '^Path = .rsrc/RCDATA'
$PY -c 'import pefile,sys;p=pefile.PE(sys.argv[1])
for t in p.DIRECTORY_ENTRY_RESOURCE.entries:
  for n in t.directory.entries:
    for l in n.directory.entries: print(pefile.RESOURCE_TYPE.get(t.id,t.name), n.name or n.id, l.id, "offset", p.get_offset_from_rva(l.data.struct.OffsetToData), "size", l.data.struct.Size)
print("overlay", p.get_overlay_data_start_offset())' rsrc_pe_rcdata.bin
echo "magic@$(at rsrc_pe_rcdata.bin)"; tail -c +$(( $(at rsrc_pe_rcdata.bin)+1 )) rsrc_pe_rcdata.bin | parse
echo "== rsrc_dotnet_manifest.bin"; $PY -c 'import dnfile,sys;p=dnfile.dnPE(sys.argv[1]);c=p.net.struct.ResourcesRva
for r in p.net.mdtables.ManifestResource: print(r.Name, "Offset", r.Offset, "data@", p.get_offset_from_rva(c)+r.Offset+4)' rsrc_dotnet_manifest.bin
echo "magic@$(at rsrc_dotnet_manifest.bin)"; tail -c +$(( $(at rsrc_dotnet_manifest.bin)+1 )) rsrc_dotnet_manifest.bin | parse
echo "== rsrc_pe_overlay.bin"; $PY -c 'import pefile,sys;print("overlay", pefile.PE(sys.argv[1]).get_overlay_data_start_offset())' rsrc_pe_overlay.bin; grep -abo HCFG rsrc_pe_overlay.bin
tail -c +4105 rsrc_pe_overlay.bin | parse; echo "crc(gzip)=$(tail -c +4105 rsrc_pe_overlay.bin | crc)"
for f in rsrc_elf_overlay.bin rsrc_decoy_elf.bin; do echo "== $f"
  $PY -c 'import lief,sys;b=lief.parse(sys.argv[1]);import os;print("lief has_overlay",b.has_overlay,"overlay_offset",os.path.getsize(sys.argv[1])-len(b.overlay) if b.has_overlay else None)' $f
  readelf -hW $f | grep -E 'Start of section headers|Size of section headers|Number of section headers'; stat -c 'size %s' $f; echo "HCFG hits: $(grep -c -a HCFG $f)"; done
tail -c +14345 rsrc_elf_overlay.bin | parse; echo "crc(gzip)=$(tail -c +14345 rsrc_elf_overlay.bin | crc)"
for f in rsrc_jar_config.bin rsrc_decoy_jar.bin; do echo "== $f"; zipinfo $f | grep config.bin
  $PY -c 'import struct,sys;d=open(sys.argv[1],"rb").read();i=d.find(b"PK\x03\x04config.bin"[:4]);i=d.find(b"config.bin")-30;n,m=struct.unpack_from("<HH",d,i+26);print("config.bin local header",i,"data@",i+30+n+m)' $f
  unzip -p $f config.bin | parse; echo "crc(gzip)=$(unzip -p $f config.bin | crc)"; done
echo "== rsrc_jar_b64entry.bin"; zipinfo rsrc_jar_b64entry.bin | grep config.txt
$PY -c 'import struct,sys;d=open(sys.argv[1],"rb").read();i=d.find(b"assets/config.txt")-30;n,m=struct.unpack_from("<HH",d,i+26);print("local header",i,"data@",i+30+n+m)' rsrc_jar_b64entry.bin
unzip -p rsrc_jar_b64entry.bin assets/config.txt | grep -abo SENGR; unzip -p rsrc_jar_b64entry.bin assets/config.txt | sed -n 's/^cfg=//p' | base64 -d | parse
