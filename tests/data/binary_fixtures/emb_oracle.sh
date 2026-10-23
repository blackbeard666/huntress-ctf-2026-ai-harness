#!/bin/bash
# Independent oracle for emb_*.bin: .NET = dnfile ManifestResource rows + stdlib zlib (raw deflate) + `file` + sha256sum
# + grep -obUa; MemberRef/TypeRef names from `strings` of dnfile's #Strings; jar = unzip -p + python xor with the key
# read from Loader.class's constant pool (javap -v) + javap on the decoded class + sha256sum + grep -obUa.
# usage: PY=.venv/bin/python bash emb_oracle.sh DIR
set -e; D=$(realpath "${1:-.}"); PY=${PY:-python3}; W=$(mktemp -d); cd "$W"
for f in emb_dotnet_costura emb_decoy_dotnet; do
  echo "== $f"
  $PY -I -c '
import sys, dnfile, zlib
pe = dnfile.dnPE(sys.argv[1]); net = pe.net
lo = pe.get_offset_from_rva(net.struct.ResourcesRva)
for r in net.mdtables.ManifestResource:
    o = lo + r.Offset; n = int.from_bytes(pe.__data__[o:o+4], "little")
    raw = pe.__data__[o+4:o+4+n]
    try: dec = zlib.decompress(raw, -15)
    except zlib.error: dec = b""
    print("resource", r.Name, "data@", o + 4, "inflated", len(dec)); open(str(r.Name), "wb").write(dec)

' "$D/$f.bin"
  for r in costura.*; do file -b "$r" | cut -c1-60; sha256sum "$r" | cut -c1-64; grep -obUa HCFG "$r" || echo "no HCFG"; rm -f "$r"; done
  strings -el "$D/$f.bin" | grep -E 'costura|Payload|^Run$|^go$' | tr '\n' ' '; echo
  strings -a "$D/$f.bin" | grep -xE 'Load|GetManifestResourceStream|add_AssemblyResolve|CreateInstance|GetMethod|Invoke|GetType' | tr '\n' ' '; echo
done
for f in emb_jar_defineclass emb_decoy_jar; do
  echo "== $f"; unzip -Z1 "$D/$f.bin" | tr '\n' ' '; echo
  unzip -o -q "$D/$f.bin" -d "$f"; echo "payload.bin data@ $($PY -I -c '
import sys, zipfile; z = zipfile.ZipFile(sys.argv[1]); i = z.getinfo("payload.bin"); b = open(sys.argv[1], "rb").read()
p = i.header_offset; print(p + 30 + int.from_bytes(b[p+26:p+28], "little") + int.from_bytes(b[p+28:p+30], "little"))' "$D/$f.bin")"
  javap -v "$f/Loader.class" | grep -E 'String k3y|Methodref.*(defineClass|getMethod|invoke|newInstance|getDeclaredConstructor|getResourceAsStream)' | sed 's/^ *//' | cut -c1-90
  $PY -I -c 'import sys; d=open(sys.argv[1],"rb").read(); k=b"k3y"; open("Secret.class","wb").write(bytes(c^k[i%3] for i,c in enumerate(d)))' "$f/payload.bin"
  if javap -v Secret.class > j.txt 2>/dev/null; then grep -E '^ *this_class|major' j.txt; sha256sum Secret.class | cut -c1-64; wc -c < Secret.class; grep -obUa SENGR Secret.class; else echo "xor k3y: not a class"; fi
  rm -rf "$f" Secret.class j.txt
done
rm -rf "$W"
