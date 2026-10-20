#!/bin/bash
# usage: fmap_gen.sh out.bin case json key   (file_map / section-slack-cave fixtures)
# HCFG blob = {"HCFG", u8 ver=1, u8 key, u16 len, u32 crc32(json), json ^ key} (crc32 from the gzip trailer, perl
# pack), written INTO an uncovered gap of a gcc/ld image with dd conv=notrunc at an offset read by readelf/objdump:
#  elf_pretext   gcc -Wl,-z,noseparate-code, main aligned(256) -> .text alignment gap inside the R E PT_LOAD (code cave)
#  elf_postrodata gcc default: blob at the end of the .note.ABI-tag/.rodata PT_LOAD (gap before .init_array, no segment)
#  elf_preshoff  gcc default: blob (padded to 8) inserted before the section header table, e_shoff bumped (perl)
#  elf_clean     gcc default, no blob (all gaps zero)            elf_rodata (decoy) blob as a const in .rodata, no gap
#  pe_slack      gcc -c -> objcopy pe-x86-64 -> ld i386pep: blob in .text raw slack past VirtualSize
#  pe_hdrgap     same PE: blob in the header padding after the section table      decoy_text: printf text file
set -e
OUT="$1"; C="$2"; P="$3"; K=$(( ${4:-0} )); W=$(mktemp -d)
CRC=$(printf '%s' "$P" | gzip -c | tail -c8 | head -c4 | od -An -tx4 | tr -d ' ')
blob() { perl -e 'print "HCFG", pack("CCvV", 1, $ARGV[1], length $ARGV[0], hex $ARGV[2]), join "", map { chr(ord($_) ^ $ARGV[1]) } split //, $ARGV[0]' "$P" "$K" "$CRC"; }
patch() { blob > "$W/b"; dd if="$W/b" of="$OUT" bs=1 seek=$(( $1 )) conv=notrunc status=none; }
secend() { readelf -SW "$OUT" | perl -ne 'if (/\]\s+\Q'"$1"'\E\s+\S+\s+\S+\s+(\S+)\s+(\S+)/) { printf "%d\n", hex($1) + hex($2) }'; }
printf 'int main(void){return 0;}\n' > "$W/m.c"
case "$C" in
  elf_pretext) printf '__attribute__((aligned(256))) int main(void){return 0;}\n' > "$W/m.c"
    gcc -O1 -Wl,-z,noseparate-code -o "$OUT" "$W/m.c"; patch $(secend .plt.got) ;;
  elf_postrodata) gcc -O1 -o "$OUT" "$W/m.c"; patch $(secend .note.ABI-tag) ;;
  elf_preshoff) gcc -O1 -o "$W/a" "$W/m.c"; blob > "$W/b"
    perl -e 'local $/; open A,"<",$ARGV[0]; my $d=<A>; open B,"<",$ARGV[1]; my $b=<B>; $b.="\0" x ((8 - length($b) % 8) % 8);
      my $sh=unpack("Q<", substr($d,40,8)); substr($d,$sh,0)=$b; substr($d,40,8)=pack("Q<",$sh+length $b); print $d' "$W/a" "$W/b" > "$OUT" ;;
  elf_clean) gcc -O1 -o "$OUT" "$W/m.c" ;;
  elf_rodata) B=$(blob | od -An -v -tu1 | tr -s ' \n' ',' | sed 's/^,//;s/,$//')
    printf '__attribute__((used)) static const unsigned char cfg[] = {%s};\nint main(void){return cfg[0];}\n' "$B" > "$W/m.c"
    gcc -O1 -o "$OUT" "$W/m.c" ;;
  pe_slack|pe_hdrgap) printf 'int check(void){return 7;}\n__attribute__((used)) const char tag[] = "fmap";\n' > "$W/m.c"
    gcc -O1 -fno-asynchronous-unwind-tables -fno-pic -c -o "$W/m.o" "$W/m.c"
    objcopy -R .comment -R .note.GNU-stack -O pe-x86-64 "$W/m.o" "$W/m.obj"; ld -m i386pep --entry=check --subsystem=console -o "$OUT" "$W/m.obj"
    if [ "$C" = pe_slack ]; then
      O=$(objdump -h "$OUT" | perl -ne 'if (/^\s+\d+\s+\.text\s+(\S+)\s+\S+\s+\S+\s+(\S+)/) { printf "%d\n", hex($1) + hex($2) }')
    else O=$(python3 -c 'import sys,struct; d=open(sys.argv[1],"rb").read(); p=struct.unpack_from("<I",d,60)[0]; n,o=struct.unpack_from("<H12xH",d,p+6); print(p+24+o+40*n+8)' "$OUT"); fi
    patch "$O" ;;
  decoy_text) printf 'ELF? no: renamed impostor, HCFG mentioned, no image. %s\n' "$P" > "$OUT" ;;
esac
rm -rf "$W"
