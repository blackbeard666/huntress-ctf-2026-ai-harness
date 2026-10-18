#!/bin/bash
# Regenerate ghc_* fixtures. ghc is NOT installed (apt ghc ~1 GB): GHC images are imitated with gcc -O0
# -fno-toplevel-reorder C programs whose OBJECT/FUNC symbols carry real GHC z-encoded names (z-encoding only uses
# [A-Za-z0-9_], so they are valid C identifiers): <unit>_<Module>_<name>_{closure,info,con_info,bytes}, main-unit
# symbols without the unit prefix (Main_main_closure, ZCMain_main_closure), rts hs_main/hs_init_ghc/stg_ap_0_fast, the
# rts --info pairs ("GHC version", "<ver>"), info-table con_desc strings ("<pkg>:<Module>.<Con>") and the HCFG blob as
# Addr# ByteString literal(s) `<Mod>_<name>N_bytes`. Blob: printf header + crc32 from the gzip trailer (coreutils);
# text: coreutils base64 | fold; raw bytes: xxd -i.
set -e
cd "$(dirname "$0")"
W=$(mktemp -d)
blob() {  # $1 json -> $W/blob.raw (version 1, key 0x00)
  local P="$1" LEN CRC; LEN=$(printf '%s' "$P" | wc -c)
  CRC=$(printf '%s' "$P" | gzip -c | tail -c8 | head -c4 | od -An -tx4 | tr -d ' ')
  { printf 'HCFG\x01\x00'; printf "\\x$(printf %02x $((LEN&255)))\\x$(printf %02x $((LEN>>8)))"
    printf "\\x${CRC:6:2}\\x${CRC:4:2}\\x${CRC:2:2}\\x${CRC:0:2}"; printf '%s' "$P"; } > "$W/blob.raw"; }
U='__attribute__((used))'
CC="gcc -O0 -fno-toplevel-reorder -no-pie"

# A: unstripped, base64 ByteString literal split over three Config_hcfgBlobN_bytes closures (.rodata), GHC 9.6.6
blob '{"flag":"HCFG{z_encoded_closures}","day":18,"lang":"haskell"}'
{ base64 -w0 "$W/blob.raw" | fold -w 48; echo; } > "$W/ch.txt"
{ echo '#include <stdio.h>'
  echo "$U const char rts_info[][24] = {\"GHC RTS\",\"YES\",\"GHC version\",\"9.6.6\",\"RTS way\",\"rts_thr\",\"Host platform\",\"x86_64-unknown-linux\"};"
  echo "$U const char con_desc_cfg[] = \"main:Config.Config\";"
  echo "$U const char con_desc_bs[] = \"bytestring-0.11.5.3:Data.ByteString.Internal.Type.BS\";"
  n=0; while read -r c; do n=$((n+1)); echo "$U const char Config_hcfgBlob${n}_bytes[] = \"$c\";"; done < "$W/ch.txt"
  for s in Config_hcfgBlob_closure Config_decodeCfg_info Config_zdwdecodeCfg_info Main_main_closure Main_main_info \
           ZCMain_main_closure base_GHCziBase_zd_closure base_GHCziShow_zdfShowInt_closure \
           ghczmprim_GHCziTypes_ZC_con_info ghczmprim_GHCziTypes_Izh_con_info \
           bytestringzm0zi11zi5zi3_DataziByteStringziInternalziType_BS_con_info \
           textzm2zi0zi2_DataziTextziEncoding_decodeUtf8_closure; do echo "$U const void *$s[2] = {0, 0};"; done
  echo "$U void stg_ap_0_fast(void) {} $U void hs_init_ghc(int *c, char ***v) { (void)c; (void)v; }"
  echo "$U int hs_main(int c, char **v) { hs_init_ghc(&c, &v); puts(Config_hcfgBlob1_bytes); return 0; }"
  echo 'int main(int c, char **v) { return hs_main(c, v); }'
} > "$W/a.c"
$CC -o ghc_split_b64.bin "$W/a.c"

# B: strip -s'd, raw ByteString literal (embedded NULs: unsafePackAddressLen) Main_hcfg1_bytes, GHC 9.4.8
blob '{"flag":"HCFG{stripped_bytestring}","day":18}'
(cd "$W" && xxd -i -n Main_hcfg1_bytes blob.raw > b.h)
{ echo '#include <stdio.h>'; sed "s/^unsigned char/$U const unsigned char/; s/^unsigned int/$U const unsigned int/" "$W/b.h"
  echo "$U const char rts_info[][24] = {\"GHC RTS\",\"YES\",\"GHC version\",\"9.4.8\",\"RTS way\",\"rts_v\"};"
  echo "$U const char usage[] = \"Usage: <prog> <args> [+RTS <rtsopts> | -RTS <args>] ... --RTS <args>\";"
  echo "$U const char cd1[] = \"ghc-prim:GHC.Types.:\"; $U const char cd2[] = \"base:GHC.Maybe.Just\"; $U const char cd3[] = \"main:Main.Cfg\";"
  echo 'int main(int c, char **v) { (void)v; if (c > 5) puts(usage); return Main_hcfg1_bytes[c]; }'
} > "$W/b.c"
$CC -o ghc_raw_stripped.bin "$W/b.c" && strip -s ghc_raw_stripped.bin

# C (decoy): plain C, symbol table kept, every GHC cue only as a string literal; no HCFG
{ echo '#include <stdio.h>'
  echo 'static const char *cues[] = {"ghczmprim_GHCziTypes_ZC_con_info","base_GHCziBase_zd_closure","hs_main","GHC RTS",'
  echo '  "GHC version","9.4.7","RTS way","rts_thr","+RTS","ghc-prim:GHC.Types.:","main:Main.Cfg","Main_hcfg1_bytes"};'
  echo 'int main(int c, char **v) { (void)v; puts(cues[c % 12]); return 0; }'
} > "$W/c.c"
$CC -o ghc_decoy_cstrings.bin "$W/c.c"

# D (decoy): text impostor -- GHC cue names + base64 HCFG in a text file, no executable container
blob '{"flag":"HCFG{not_an_elf}","day":18}'
{ printf 'GHC version 9.6.6 hs_main ghczmprim_GHCziTypes_ZC_con_info base:GHC.Maybe.Just\n'; } > ghc_decoy_text.bin
rm -rf "$W"
