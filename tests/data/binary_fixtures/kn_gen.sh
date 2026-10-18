#!/bin/bash
# Regenerate kn_* fixtures (Kotlin/Native). konanc is NOT installed: konanc images are imitated with gcc + asm-label
# symbols named the konanc way (kfun:<owner>#<name>(<params>){}<ret>, kclass:<fq>, ktype:<fq>) and the Konan runtime
# entry points (Konan_main, Kotlin_initRuntimeIfNeeded). The HCFG is stored as a static KString: ArrayHeader
# {TypeInfo* -> ktype:kotlin.String, uint32 count, pad to 16 = sizeof(ArrayHeader) on x86-64} + the base64 text as UTF-16LE code units
# (gcc u"" literal = the independent UTF-16 encoder; base64 = coreutils). Blob: printf header + gzip-trailer crc32.
set -e
cd "$(dirname "$0")"
W=$(mktemp -d)
blob() {  # $1 json -> $W/blob.raw (version 1, key 0x00)
  local P="$1" LEN CRC; LEN=$(printf '%s' "$P" | wc -c)
  CRC=$(printf '%s' "$P" | gzip -c | tail -c8 | head -c4 | od -An -tx4 | tr -d ' ')
  { printf 'HCFG\x01\x00'; printf "\\x$(printf %02x $((LEN&255)))\\x$(printf %02x $((LEN>>8)))"
    printf "\\x${CRC:6:2}\\x${CRC:4:2}\\x${CRC:2:2}\\x${CRC:0:2}"; printf '%s' "$P"; } > "$W/blob.raw"; }
fn() {  # $1 konanc symbol -> C function with that asm name
  local C="f$RANDOM$RANDOM"; echo "int $C(void) __asm__(\"\\\"$1\\\"\"); int $C(void) { return ${#1}; }"; }
obj() {  # $1 konanc symbol -> data object with that asm name
  local C="o$RANDOM$RANDOM"; echo "const char $C[] __asm__(\"\\\"$1\\\"\") = \"$1\";"; }
kstr() {  # $1 symbol, $2 text -> static KString {ktype:kotlin.String*, count, UTF-16 chars}
  echo "extern const char KT_STRING[] __asm__(\"\\\"ktype:kotlin.String\\\"\");"
  echo "__attribute__((used, aligned(8))) const struct { const void *ti; unsigned count, pad; char16_t c[${#2}]; } ks$RANDOM"
  echo "  __asm__(\"\\\"$1\\\"\") = { KT_STRING, ${#2}, 0, u\"$2\" };"; }
RT='#include <uchar.h>
int Kotlin_initRuntimeIfNeeded(void) { return 0; }
int Konan_main(int c, char **v) { (void)v; return Kotlin_initRuntimeIfNeeded() + c; }
int main(int c, char **v) { return Konan_main(c, v); }'

# A: unstripped x86-64 non-PIE konanc-style image, HCFG = UTF-16LE base64 KString (count 16 bytes before payload)
blob '{"flag":"HCFG{konan_kstring_utf16}","day":18,"lang":"kotlin-native"}'
B64=$(base64 -w0 "$W/blob.raw")
{ echo "$RT"; obj "ktype:kotlin.String"; obj "kclass:kotlin.String"; obj "ktype:com.huntress.cfg.Config"
  obj "kclass:com.huntress.cfg.Config"; obj "ktype:kotlin.native.internal.Ref"
  fn "kfun:#main(){}"; fn "kfun:com.huntress.cfg#decode(kotlin.String){}kotlin.ByteArray"
  fn "kfun:com.huntress.cfg.Config#<init>(){}"; fn "kfun:com.huntress.cfg.Config#<get-flag>(){}kotlin.String"
  fn "kfun:kotlin.io#println(kotlin.Any?){}"; fn "kfun:kotlin.text#decodeToString__at__kotlin.ByteArray(){}kotlin.String"
  fn "kfun:kotlin.native.internal#ThrowNullPointerException(){}"
  kstr "kvar:com.huntress.cfg#CONFIG" "$B64"
} > "$W/a.c"
gcc -O0 -no-pie -o kn_utf16_b64.bin "$W/a.c"

# B: PIE, strip -s'd: no symbols -> runtime only from raw cues (UTF-16LE TypeInfo name + ASCII runtime string);
#    TypeInfo pointer is a relocation (0 in the file) -> kstring_type none; root-package config
blob '{"flag":"HCFG{stripped_konan}","ab":2}'
B64=$(base64 -w0 "$W/blob.raw")
{ echo "$RT"; echo 'const char16_t TI_NAME[] = u"kotlin.native.internal.NativePtr";'
  echo 'const char RT_MSG[] = "Kotlin_initRuntimeIfNeeded: runtime already initialised";'
  echo 'const char16_t *keep(void) { return TI_NAME; }'
  obj "ktype:kotlin.String"; fn "kfun:#main(){}"; fn "kfun:#cfg(){}kotlin.String"; kstr "kvar:#CFG" "$B64"
} > "$W/b.c"
gcc -O0 -fPIE -pie -o "$W/b.bin" "$W/b.c"; strip -s -o kn_stripped_pie.bin "$W/b.bin"

# C (decoy): plain C, symbol table kept, every Kotlin/Native cue only as a string literal; no HCFG
{ echo '#include <stdio.h>'
  echo 'static const char *cues[] = {"kfun:#main(){}","Konan_main","Kotlin_initRuntimeIfNeeded","kclass:kotlin.String",'
  echo '  "kotlin.native.internal.Ref","ktype:com.x.Config"};'
  echo 'int main(int c, char **v) { (void)v; puts(cues[c % 6]); return 0; }'
} > "$W/c.c"
gcc -O0 -no-pie -o kn_decoy_cstrings.bin "$W/c.c"

# D (decoy): text impostor -- K/N cue names + a UTF-16LE base64 HCFG with a corrupted crc, no ELF container
blob '{"flag":"HCFG{not_an_elf}"}'
{ printf 'kfun:#main(){} Konan_main Kotlin_initRuntimeIfNeeded kotlin.native.internal\n'
  base64 -w0 "$W/blob.raw" | sed 's/^\(.\{12\}\)..../\1AAAA/' | iconv -f ASCII -t UTF-16LE; } > kn_decoy_text.bin
rm -rf "$W"
