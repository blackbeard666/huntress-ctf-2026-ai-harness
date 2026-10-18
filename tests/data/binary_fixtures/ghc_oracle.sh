#!/bin/bash
# Independent oracle for ghc_* fixtures: file -b, nm --defined-only (+ perl z-decoder of GHC's Encoding.hs table),
# strings -a -t d (rts --info "GHC version" pair, con_desc "<pkg>:<Mod>.<Con>", base64 chunks), readelf -SW, base64 -d.
f="$1"; file -b "$f"
echo "== symbols (z-decoded unit / module)"
nm --defined-only "$f" 2>/dev/null | awk '{print $3}' | perl -ne 'chomp; next unless /^(?:([a-z][A-Za-z0-9]*)_)?([A-Z][A-Za-z0-9]*)_(\w+?)_(closure|info|con_info|bytes|entry)$/;
  my ($u,$m,$n)=($1,$2,$3); next if $m eq "ZCMain";
  my %t=(zi=>".",zm=>"-",zd=>"\$",zu=>"_",zh=>"#",zz=>"z",ZZ=>"Z",ZC=>":",zq=>"\x27",zl=>"<",zg=>">",zp=>"+",zt=>"*",zs=>"/",ze=>"=",zn=>"!",zb=>"|",za=>"&",zc=>"^",zr=>"\\",zv=>"%",ZL=>"(",ZR=>")",ZM=>"[",ZN=>"]");
  for ($u,$m,$n) { next unless defined; s/(z[a-z]|Z[A-Z])/exists $t{$1}?$t{$1}:$1/ge }
  print(($u//"main"), " $m $n\n")' | sort -u
echo "== hs_main / ZCMain"; nm "$f" 2>/dev/null | grep -wE "hs_main|ZCMain_main_closure|hs_init_ghc"
echo "== strings: version pair / con_desc"; strings -a -t d "$f" | grep -A1 -x ' *[0-9]* GHC version'
strings -a "$f" | grep -E '^[a-z][a-z0-9.-]*:([A-Z][A-Za-z0-9_]*\.)+[^ ]+$'
echo "== sections"; readelf -SW "$f" 2>/dev/null | grep -E '\.rodata|\.data '
echo "== HCFG"; s=$(strings -a -n 4 -t d "$f" | awk '/ SENGR/{p=1} p&&$2!~/^[A-Za-z0-9+\/=]+$/{exit} p')
if [ -n "$s" ]; then echo "base64 first chunk @ $(printf '%s\n' "$s" | head -1 | awk '{print $1}')"
  printf '%s\n' "$s" | awk '{printf "%s", $2}' | base64 -d | tail -c +13; echo; fi
python3 -c 'import sys; d=open(sys.argv[1],"rb").read(); i=d.find(b"HCFG\x01"); print("raw HCFG @", i if i >= 0 else "none")' "$f"
