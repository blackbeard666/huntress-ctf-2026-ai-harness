#!/bin/bash
# usage: storage_gen.sh out.bin case json key   (hcfg_storage fixtures, D17 rule list)
# The HCFG blob = {"HCFG", u8 ver=1, u8 key, u16 len, u32 crc32(json), json ^ key}; crc32 from the gzip trailer
# (coreutils), body xor by perl. Cases: elf_hcfg/elf_data/elf_rodata/elf_text (gcc, blob as a C struct in section
# .hcfg / writable .data / const .rodata / .text), elf_b64 (gcc, base64(blob) via coreutils base64 as a C string),
# elf_overlay (gcc ELF + blob appended by cat: in no section), elf_badcrc (decoy: crc+1), pe_hcfg/pe_rdata/pe_text
# (gcc -c -> objcopy -O pe-x86-64 -> ld -m i386pep), wasm_data (wat2wasm data segment), wasm_custom (wat2wasm module +
# blob in an appended custom section, printf), macho_hcfg/macho_const/macho_text (clang-18 --target=arm64-apple-macos
# -c), jar_b64 (javac + zip, base64 String constant), decoy_text (printf: a text file with a bare "HCFG").
set -e
OUT="$1"; C="$2"; P="$3"; K=$(( ${4:-0} )); W=$(mktemp -d)
LEN=$(printf '%s' "$P" | wc -c)
CRC=$(printf '%s' "$P" | gzip -c | tail -c8 | head -c4 | od -An -tx4 | tr -d ' ')
[ "$C" = elf_badcrc ] && CRC=$(printf '%08x' $(( 0x$CRC ^ 1 )))
BODY=$(perl -e 'print join ",", map { ord($_) ^ $ARGV[1] } split //, $ARGV[0]' "$P" "$K")
blob() { perl -e 'print "HCFG", pack("CCvV", 1, $ARGV[1], length $ARGV[0], hex $ARGV[2]), join "", map { chr(ord($_) ^ $ARGV[1]) } split //, $ARGV[0]' "$P" "$K" "$CRC"; }
cstruct() {   # $1 = attribute text, $2 = const or empty
  cat > "$W/m.c" <<CC
struct hcfg { char m[4]; unsigned char ver, key; unsigned short len; unsigned int crc; unsigned char body[$LEN]; };
$1 $2 struct hcfg hcfg_blob = {{'H','C','F','G'}, 1, $K, $LEN, 0x$CRC, {$BODY}};
int check(const char *s) { int n = 0; while (s[n]) n++; return n == hcfg_blob.len; }
int main(int c, char **v) { return check(v[0]); }
CC
}
case "$C" in
  elf_hcfg|elf_badcrc) cstruct '__attribute__((section(".hcfg"), used))' const; gcc -O1 -o "$OUT" "$W/m.c" ;;
  elf_data) cstruct '__attribute__((used))' ''; gcc -O1 -o "$OUT" "$W/m.c" ;;
  elf_rodata) cstruct '__attribute__((used)) static' const; gcc -O1 -o "$OUT" "$W/m.c" ;;
  elf_text) cstruct '__attribute__((section(".text#"), used))' const; gcc -O1 -o "$OUT" "$W/m.c" ;;
  elf_overlay) cstruct "" const;
    perl -pi -e "s/'H','C','F','G'/'h','c','f','g'/" "$W/m.c"; gcc -O1 -o "$W/a" "$W/m.c"; cat "$W/a" > "$OUT"; blob >> "$OUT" ;;
  elf_b64) B=$(blob | base64 -w0); printf 'const char *cfg = "%s";\nint main(void){return cfg[0];}\n' "$B" > "$W/m.c"
    gcc -O1 -o "$OUT" "$W/m.c" ;;
  pe_hcfg|pe_rdata|pe_text)
    A='__attribute__((section(".hcfg"), used))'; [ "$C" = pe_rdata ] && A='__attribute__((used))'
    [ "$C" = pe_text ] && A='__attribute__((section(".text#"), used))'
    cstruct "$A" const; sed -i '/int main/d' "$W/m.c"
    gcc -O1 -fno-asynchronous-unwind-tables -fno-pic -c -o "$W/m.o" "$W/m.c"
    objcopy -R .comment -R .note.GNU-stack -O pe-x86-64 "$W/m.o" "$W/m.obj"; ld -m i386pep --entry=check --subsystem=console -o "$OUT" "$W/m.obj" ;;
  wasm_data|wasm_custom)
    if [ "$C" = wasm_data ]; then D=$(blob | od -An -v -tx1 | tr -s ' \n' ' ' | sed 's/^ //;s/ $//;s/ /\\/g;s/^/\\/'); else D='\00'; fi
    printf '(module (memory (export "memory") 1) (data (i32.const 1024) "%s") (func (export "f") (result i32) i32.const 1024))\n' "$D" > "$W/m.wat"
    wat2wasm -o "$OUT" "$W/m.wat"
    if [ "$C" = wasm_custom ]; then blob > "$W/b"; N=$(( $(stat -c%s "$W/b") + 5 )); \
      perl -e 'my($n,$b)=@ARGV; open F,"<",$b; local $/; my $d=<F>; my $s="\x04hcfg".$d; my $l=length $s; my $leb=""; do { my $x=$l&0x7f; $l>>=7; $x|=0x80 if $l; $leb.=chr $x } while $l; print "\x00".$leb.$s' "$N" "$W/b" >> "$OUT"; fi ;;
  macho_hcfg|macho_const|macho_text)
    S='__DATA,__hcfg'; [ "$C" = macho_const ] && S='__DATA,__const'; [ "$C" = macho_text ] && S='__TEXT,__text'
    cstruct "__attribute__((section(\"$S\"), used))" const; sed -i '/int main/d' "$W/m.c"
    clang-18 --target=arm64-apple-macos -O2 -c -o "$OUT" "$W/m.c" ;;
  decoy_text) printf "MZ renamed impostor: HCFG magic mentioned, no blob. %s\n" "$P" > "$OUT" ;;
  jar_b64) B=$(blob | base64 -w0)
    printf 'public class Cfg { static final String C = "%s"; public static void main(String[] a) { System.out.println(C.length()); } }\n' "$B" > "$W/Cfg.java"
    (cd "$W" && javac -source 8 -target 8 Cfg.java 2>/dev/null && printf 'Main-Class: Cfg\n' > m.txt && zip -q -X out.jar Cfg.class m.txt)
    cp "$W/out.jar" "$OUT" ;;
esac
rm -rf "$W"
