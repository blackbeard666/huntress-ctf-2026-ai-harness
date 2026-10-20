#!/bin/bash
# Overlay-header fixtures (independent writer: gcc + perl pack/Digest::SHA; no lib.binary code).
# usage (repo root): bash tests/data/binary_fixtures/ovhdr_gen.sh
set -e
D=$(cd "$(dirname "$0")" && pwd); T=$(mktemp -d)
printf 'int main(void){return 0;}\n' > "$T/h.c"
gcc -Os -s -o "$T/host.elf" "$T/h.c"
# PK19: ver, k1, k2, pad, len, sha256(plain), packed[i] = rol3(plain[i]^k1) ^ k2  (inverse of ror8(b^k2,3)^k1)
pack() {  # magic ver k1 k2 json key  -> stdout
perl -MDigest::SHA=sha256 -e '
  my ($mg,$v,$k1,$k2,$js,$hk)=@ARGV; $_=hex for $k1,$k2,$hk;
  # HCFG record: magic, ver 1, key, len u16le, crc32 u32le (crc via perl pure loop), payload^key
  my $c=0xFFFFFFFF; for my $ch (unpack("C*",$js)){ $c^=$ch; for(1..8){ $c=($c>>1)^(($c&1)?0xEDB88320:0) } } $c^=0xFFFFFFFF;
  my $pl=join("",map{chr(ord($_)^$hk)}split//,$js);
  my $rec="HCFG".pack("CCvV",1,$hk,length($js),$c).$pl;
  my $pk=join("",map{ my $b=ord($_)^$k1; chr(((($b<<3)|($b>>5))&255)^$k2) } split//,$rec);
  print $mg.pack("CCCCV",$v,$k1,$k2,0,length($pk)).sha256($rec).$pk;' "$@"
}
{ cat "$T/host.elf"; pack PK19 1 0x5a 0xc3 '{"campaign":"OV-1","domain":"ov1.example.invalid"}' 0x21; } > "$D/ovhdr_pk19_synth.bin"
{ cat "$T/host.elf"; printf 'JUNKPAD!'; pack PK19 4 0x07 0xf0 '{"campaign":"OV-2","mutex":"Global\\OV2"}' 0x44; } > "$D/ovhdr_pk19_v4_gap.bin"
# decoys: plain host (no overlay at all), host + wrong magic PK18 overlay
cp "$T/host.elf" "$D/ovhdr_decoy_nooverlay.bin"
{ cat "$T/host.elf"; pack PK18 1 0x11 0x22 '{"campaign":"X"}' 0x33; } > "$D/ovhdr_decoy_wrongmagic.bin"
# cached D19 member (GM-confirmed overlay_offset 10808 / size 424), same bytes as ovspec_d19_single.bin
cp "$D/ovspec_d19_single.bin" "$D/ovhdr_d19_single.bin"
rm -rf "$T"
