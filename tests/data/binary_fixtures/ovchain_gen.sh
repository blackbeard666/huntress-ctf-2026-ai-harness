#!/bin/bash
# Multi-layer / decoy overlay-chain fixtures (independent writer: gcc + perl pack/Digest::SHA/Compress::Zlib; no lib code).
# usage (repo root): bash tests/data/binary_fixtures/ovchain_gen.sh
set -e
D=$(cd "$(dirname "$0")" && pwd); T=$(mktemp -d)
printf 'int main(void){return 0;}\n' > "$T/h.c"
printf '#include <string.h>\nstatic const char tag[]="PK19";\nint main(int c,char**v){return c>1&&!memcmp(v[1],tag,4);}\n' > "$T/r.c"
gcc -Os -s -o "$T/host.elf" "$T/h.c"; gcc -Os -s -o "$T/rod.elf" "$T/r.c"
hcfg() {  # json key -> HCFG record (magic, ver 1, key, len u16le, crc32 u32le, payload^key)
perl -e 'my ($js,$hk)=@ARGV; $hk=hex $hk;
  my $c=0xFFFFFFFF; for my $ch (unpack("C*",$js)){ $c^=$ch; for(1..8){ $c=($c>>1)^(($c&1)?0xEDB88320:0) } } $c^=0xFFFFFFFF;
  print "HCFG".pack("CCvV",1,$hk,length($js),$c).join("",map{chr(ord($_)^$hk)}split//,$js);' "$@"
}
pk() {  # magic ver k1 k2 badhash < plain -> PK19 block; packed[i] = rol3(plain[i]^k1)^k2; badhash=1 stores a wrong sha256
perl -MDigest::SHA=sha256 -e 'my ($mg,$v,$k1,$k2,$bad)=@ARGV; $_=hex for $k1,$k2; local $/; my $p=<STDIN>;
  my $pk=join("",map{ my $b=ord($_)^$k1; chr(((($b<<3)|($b>>5))&255)^$k2) } split//,$p);
  print $mg.pack("CCCCV",$v,$k1,$k2,0,length($pk)).sha256($bad ? "decoy".$p : $p).$pk;' "$@"
}
zl() { perl -MCompress::Zlib -e 'local $/; print compress(<STDIN>)'; }
hcfg '{"campaign":"DECOY","c2":"decoy.example.invalid"}' 0x10 > "$T/dec.rec"
hcfg '{"campaign":"OC-A","c2":"real-a.example.invalid"}' 0x21 > "$T/a.rec"
hcfg '{"campaign":"OC-B","mutex":"Global\\OCB"}' 0x33 > "$T/b.rec"
hcfg '{"campaign":"OC-C","c2":"inner-elf.example.invalid"}' 0x44 > "$T/c.rec"
hcfg '{"campaign":"OC-D","c2":"nest.example.invalid"}' 0x55 > "$T/d.rec"
hcfg '{"campaign":"OC-E","c2":"zlib.example.invalid"}' 0x66 > "$T/e.rec"
# (a) decoy PK19 with a wrong sha256 first, real PK19 last
{ cat "$T/host.elf"; pk PK19 1 0x5a 0xc3 1 < "$T/dec.rec"; pk PK19 1 0x17 0x99 0 < "$T/a.rec"; } > "$D/ovchain_decoy_first.bin"
# (b) 'PK19' string in .rodata (code compares against it) + the real overlay
{ cat "$T/rod.elf"; pk PK19 1 0x6b 0x2e 0 < "$T/b.rec"; } > "$D/ovchain_rodata_magic.bin"
# (c) unpacked payload = a tiny ELF whose own PK19 overlay holds the HCFG
{ cat "$T/host.elf"; pk PK19 1 0x01 0x80 0 < "$T/c.rec"; } > "$T/inner.elf"
{ cat "$T/host.elf"; pk PK19 1 0x3c 0xa5 0 < "$T/inner.elf"; } > "$D/ovchain_nested_elf.bin"
# (d) overlay inside the overlay
pk PK19 2 0x11 0x22 0 < "$T/d.rec" > "$T/inner.pk"
{ cat "$T/host.elf"; pk PK19 1 0x7e 0x0f 0 < "$T/inner.pk"; } > "$D/ovchain_nested_overlay.bin"
# (e) overlay -> zlib -> overlay -> HCFG, after a bad-hash decoy
pk PK19 1 0x42 0x24 0 < "$T/e.rec" | zl > "$T/inner.z"
{ cat "$T/host.elf"; pk PK19 1 0x99 0x66 1 < "$T/dec.rec"; pk PK19 1 0x5c 0xc5 0 < "$T/inner.z"; } > "$D/ovchain_zlib_nested.bin"
# decoys: only a bad-hash PK19; only the .rodata string (no overlay at all)
{ cat "$T/host.elf"; pk PK19 1 0x5a 0xc3 1 < "$T/dec.rec"; } > "$D/ovchain_decoy_badhash.bin"
cp "$T/rod.elf" "$D/ovchain_decoy_rodata_only.bin"
rm -rf "$T"
