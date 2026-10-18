#!/bin/bash
# Regenerate ocaml_* fixtures. ocaml is NOT installed: ocamlopt images are imitated with gcc + a hand-written GNU as
# file laid out the way ocamlopt emits module data: per-module caml<Mod>__{data_begin,code_begin,entry,frametable,
# gc_roots,data_end,code_end} + caml<Mod> (module block), function symbols caml<Mod>__<fn>_<stamp>, and structured
# string constants as `.quad <header>` followed by the label caml<Mod>__<n> AT THE PAYLOAD, the bytes, zero padding
# and a final pad-count byte (header = wosize<<10 | color<<8 | 252 String_tag). OCaml 5.1+ uses '.' as separator
# (camlMain.entry) -- emitted via quoted asm symbol names. Runtime: caml_startup/caml_main/caml_program/
# caml_start_program + OCAMLRUNPARAM strings. Blob: printf header + crc32 from the gzip trailer (coreutils).
set -e
cd "$(dirname "$0")"
W=$(mktemp -d)
blob() {  # $1 json -> $W/blob.raw (version 1, key 0x00)
  local P="$1" LEN CRC; LEN=$(printf '%s' "$P" | wc -c)
  CRC=$(printf '%s' "$P" | gzip -c | tail -c8 | head -c4 | od -An -tx4 | tr -d ' ')
  { printf 'HCFG\x01\x00'; printf "\\x$(printf %02x $((LEN&255)))\\x$(printf %02x $((LEN>>8)))"
    printf "\\x${CRC:6:2}\\x${CRC:4:2}\\x${CRC:2:2}\\x${CRC:0:2}"; printf '%s' "$P"; } > "$W/blob.raw"; }
ostr() {  # $1 label, $2 file -> ocamlopt-style string block asm (black header, label at payload)
  local N WO PAD; N=$(stat -c %s "$2"); WO=$(( (N + 8) / 8 )); PAD=$(( WO * 8 - 1 - N ))
  echo "  .quad $(( (WO << 10) | (3 << 8) | 252 ))"; echo "  .globl \"$1\""; echo "\"$1\":"
  od -An -v -tu1 "$2" | sed 's/^ *//; s/  */,/g; /^$/d; s/^/  .byte /'
  [ $PAD -gt 0 ] && echo "  .space $PAD"; echo "  .byte $PAD"; }
mod() {  # $1 module, $2 sep, $3.. fn names -> module boundary + function symbols
  local M=$1 S=$2; shift 2
  echo "  .text"; for x in code_begin; do echo "  .globl \"caml$M$S$x\""; echo "\"caml$M$S$x\":"; done
  for f in entry "$@"; do echo "  .globl \"caml$M$S$f\""; echo "  .type \"caml$M$S$f\",@function"; echo "\"caml$M$S$f\":"; echo "  ret"; done
  echo "  .globl \"caml$M${S}code_end\""; echo "\"caml$M${S}code_end\":"
  echo "  .data"; echo "  .globl \"caml$M${S}data_begin\""; echo "\"caml$M${S}data_begin\":"
  echo "  .quad 1792"; echo "  .globl \"caml$M\""; echo "\"caml$M\":"; echo "  .quad 1"
  echo "  .globl \"caml$M${S}gc_roots\""; echo "\"caml$M${S}gc_roots\":"; echo "  .quad 0"
  echo "  .globl \"caml$M${S}data_end\""; echo "\"caml$M${S}data_end\":"; echo "  .quad 0"
  echo "  .globl \"caml$M${S}frametable\""; echo "\"caml$M${S}frametable\":"; echo "  .quad 0"; }
RT='.text
  .globl caml_start_program
caml_start_program: ret
  .globl caml_program
caml_program: ret
  .globl caml_startup
caml_startup: ret
  .globl caml_main
caml_main: ret
  .globl caml_raise_exn
caml_raise_exn: ret
  .section .rodata
  .asciz "OCAMLRUNPARAM"
  .asciz "CAMLRUNPARAM"
  .asciz "Fatal error: exception %s\n"'
CMAIN='extern void caml_main(char **); extern char HCFG_REF[]; int main(int c, char **v) { (void)c; caml_main(v); return HCFG_REF[0] == 0; }'

# A: OCaml 4.14 dune executable (Dune__exe__ wrapper), unstripped, raw HCFG in a String_tag block (pad 0..7)
blob '{"flag":"HCFG{dune_exe_string_block}","day":18,"lang":"ocaml"}'
{ echo "$RT"; echo '  .asciz "/home/ci/.opam/4.14.1/lib/ocaml"'
  mod Stdlib__Printf __ sprintf_431 fprintf_425; mod Stdlib__Sys __ getenv_opt_211; mod CamlinternalFormat __ make_printf_1220
  mod Stdlib __ print_endline_366; mod Dune__exe__Config __ decode_271; mod Dune__exe__Main __ main_301
  echo "  .data"; echo '  .globl HCFG_REF'; echo 'HCFG_REF = camlDune__exe__Config__3'
  printf 'version' > "$W/s1"; ostr camlDune__exe__Config__2 "$W/s1"; ostr camlDune__exe__Config__3 "$W/blob.raw"
} > "$W/a.s"
echo "$CMAIN" > "$W/a.c"; gcc -O0 -no-pie -o ocaml_dune_414.bin "$W/a.c" "$W/a.s"
# A2: same image strip -s'd (runtime only from raw OCAMLRUNPARAM / CAMLRUNPARAM / Fatal error strings)
strip -s -o ocaml_dune_414_stripped.bin ocaml_dune_414.bin

# B: OCaml 5.2 '.'-separator symbols, plain `ocamlfind ocamlopt` (camlMain), blob length = 7 mod 8 -> pad byte 0
blob '{"flag":"HCFG{ocaml5_dot}","day":18,"ab":1}'
{ echo "$RT"; echo '  .asciz "/usr/lib/ocaml/5.2.0"'
  mod Stdlib__Printf . sprintf_512; mod Stdlib__Bytes . unsafe_to_string_88; mod Stdlib__Domain . spawn_700
  mod Cfg . load_120; mod Main . run_141
  echo "  .data"; echo '  .globl HCFG_REF'; echo 'HCFG_REF = "camlCfg.4"'
  ostr camlCfg.4 "$W/blob.raw"
} > "$W/b.s"
echo "$CMAIN" > "$W/b.c"; gcc -O0 -no-pie -o ocaml_dot_52.bin "$W/b.c" "$W/b.s"

# C (decoy): plain C, symbol table kept, every OCaml cue only as a string literal; no HCFG
{ echo '#include <stdio.h>'
  echo 'static const char *cues[] = {"caml_startup","caml_main","camlStdlib__Printf__sprintf_431","OCAMLRUNPARAM",'
  echo '  "camlDune__exe__Main__entry","camlMain__entry","caml_program","/usr/lib/ocaml/4.14.1"};'
  echo 'int main(int c, char **v) { (void)v; puts(cues[c % 8]); return 0; }'
} > "$W/c.c"
gcc -O0 -no-pie -o ocaml_decoy_cstrings.bin "$W/c.c"

# D (decoy): text impostor -- OCaml cue names in a text file, no executable container
printf 'caml_startup caml_main camlStdlib__Printf camlDune__exe__Main__entry OCAMLRUNPARAM\n' > ocaml_decoy_text.bin
rm -rf "$W"
