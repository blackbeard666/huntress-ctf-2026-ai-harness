#!/bin/bash
# Evidence 1: clusters 001/002/003 with delivery manifests; 003 copies 001's alpha and lies about one sha256 + one size
set -e
mk() { # dir id path content producer
  :
}
manifest() { # dir then lines "id|path|producer|sha_override|size_override"
  d=$1; shift; echo -n '{"schema":"huntress.artifact_delivery_manifest.v1","artifacts":[' > $d/delivery-manifest.json; first=1
  for l in "$@"; do IFS='|' read id p prod sha sz <<<"$l"
    [ -z "$sha" ] && sha=$(sha256sum "$d/$p" | cut -d' ' -f1); [ -z "$sz" ] && sz=$(stat -c%s "$d/$p")
    [ $first = 1 ] || echo -n , >> $d/delivery-manifest.json; first=0
    echo -n "{\"id\":\"$id\",\"filename\":\"$(basename $p)\",\"path\":\"$p\",\"content_type\":\"text/plain\",\"family\":\"text\",\"producer_id\":\"$prod\",\"size_bytes\":$sz,\"sha256\":\"$sha\"}" >> $d/delivery-manifest.json
  done; echo ']}' >> $d/delivery-manifest.json; }
rm -rf e1 e2 e3 out; mkdir -p e1/c1/artifacts e1/c2/artifacts e1/c3/artifacts e2 e3 out
printf 'Get-Process | Out-File procs.txt\n' > e1/c1/artifacts/alpha-01.txt
printf 'Get-Process | Out-File procs.txt\n' > e1/c1/artifacts/bravo-02.txt
printf 'whoami /all\n' > e1/c1/artifacts/charlie-03.txt
manifest e1/c1 "ev1-alpha|artifacts/alpha-01.txt|text_template||" "ev1-bravo|artifacts/bravo-02.txt|duplicate_ref||" "ev1-charlie|artifacts/charlie-03.txt|text_template||"
printf 'net user /domain\n' > e1/c2/artifacts/delta-01.txt
printf 'net user /domain\n' > e1/c2/artifacts/echo-02.txt
printf 'ipconfig /all\n' > e1/c2/artifacts/foxtrot-03.txt
manifest e1/c2 "ev2-delta|artifacts/delta-01.txt|text_template||" "ev2-echo|artifacts/echo-02.txt|duplicate_ref||" "ev2-foxtrot|artifacts/foxtrot-03.txt|text_template||"
cp e1/c1/artifacts/alpha-01.txt e1/c3/artifacts/golf-01.txt
printf 'arp -a\n' > e1/c3/artifacts/hotel-02.txt
printf 'route print\n' > e1/c3/artifacts/india-03.txt
manifest e1/c3 "ev3-golf|artifacts/golf-01.txt|text_template||" "ev3-hotel|artifacts/hotel-02.txt|text_template|0000000000000000000000000000000000000000000000000000000000000000|" "ev3-india|artifacts/india-03.txt|text_template||99"
for i in 1 2 3; do (cd e1/c$i && TZ=UTC zip -q -r -X ../cluster-00$i.zip delivery-manifest.json artifacts); done
(cd e1 && zip -q -X ../out/evidence-mc1.zip cluster-001.zip cluster-002.zip cluster-003.zip)
# Evidence 2: no manifests (D30 timed style); 011 holds an inner zip whose stored CRC is zeroed + entries dated 2031
for n in 010 011 012; do mkdir -p e2/c$n/artifacts; printf "echo $n-a\n" > e2/c$n/artifacts/kilo-$n.txt; printf "echo $n-b\n" > e2/c$n/artifacts/lima-$n.txt
  printf "inner $n payload text\n" > e2/c$n/note.txt; (cd e2/c$n && zip -q -0 -X artifacts/mike-$n.zip note.txt && rm note.txt); done
python3 - <<'PY'
import struct
p='e2/c011/artifacts/mike-011.zip'; b=bytearray(open(p,'rb').read())
b[14:18]=b'\0\0\0\0'          # LFH crc32
o=b.rfind(b'PK\x01\x02'); b[o+16:o+20]=b'\0\0\0\0'   # CD crc32
open(p,'wb').write(bytes(b))
PY
touch -d '2026-09-01 10:00:00' e2/c010/artifacts/* e2/c012/artifacts/*
touch -d '2031-05-05 12:00:00' e2/c011/artifacts/*
for n in 010 011 012; do (cd e2/c$n && TZ=UTC zip -q -r -X ../cluster-$n.zip artifacts); done
touch -d '2026-10-01 08:00:00' e2/cluster-*.zip
(cd e2 && zip -q -X ../out/evidence-mc2.zip cluster-010.zip cluster-011.zip cluster-012.zip)
# Decoy 3: one cluster only; decoy 4: a PNG renamed .zip
cp e1/cluster-001.zip e3/; (cd e3 && zip -q -X ../out/evidence-mc-single.zip cluster-001.zip)
python3 -c "from PIL import Image; Image.new('RGB',(4,4)).save('out/evidence-mc-png.zip','PNG')"
