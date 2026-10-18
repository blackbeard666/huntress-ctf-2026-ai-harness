#!/bin/bash
# Independent oracle for ocaml_* fixtures: file -b, nm --defined-only (module = caml<M> with a <sep>entry symbol,
# sep '__' or '.'), readelf -SW (section of the HCFG symbol, vaddr->file offset), od (block header word before the
# payload: wosize/color/tag, last payload byte = pad), dd + od of the HCFG length field, grep -a for runtime strings.
F="$1"; file -b "$F"; case "$(file -b "$F")" in ELF*) ;; *) echo "not ELF"; exit 0;; esac
echo "runtime symbols: $(nm --defined-only "$F" | awk '{print $3}' | grep -E '^caml_(startup|main|program|start_program)$' | sort | tr '\n' ' ')"
echo "modules: $(nm --defined-only "$F" | awk '{print $3}' | perl -ne 'print "$1\n" if /^caml([A-Z]\w*?)(?:__|\.)entry$/' | sort | tr '\n' ' ')"
echo "functions: $(nm --defined-only "$F" | awk '$2=="T"{print $3}' | grep -E '^caml[A-Z]' | grep -vE '(__|\.)(entry|code_begin|code_end)$' | grep -cE '_[0-9]+$')"
echo "runtime strings: $(grep -aoE 'OCAMLRUNPARAM|CAMLRUNPARAM|Fatal error: exception' "$F" | sort -u | tr '\n' ',')"
echo "version strings: $(grep -aoE '(opam/|ocaml/)[0-9]+\.[0-9]+\.[0-9]+' "$F" | tr '\n' ' ')"
H=$(grep -aob 'HCFG' "$F" | head -1 | cut -d: -f1); [ -z "$H" ] && { echo "no HCFG"; exit 0; }
echo "HCFG file offset: $H"
nm --defined-only "$F" | while read -r a t n; do
  read -r sec saddr soff < <(readelf -SW "$F" | awk -v A=$((16#$a)) '/^ *\[ *[0-9]+\]/{sub(/^ *\[ *[0-9]+\] */,""); a=strtonum("0x"$3); s=strtonum("0x"$5); if ($2!="NOBITS" && a<=A && A<a+s) print $1, a, strtonum("0x"$4)}')
  [ -n "$sec" ] && [ $(( 16#$a - saddr + soff )) -eq $H ] && echo "symbol at HCFG: $n ($sec)"
done
HDR=$(od -An -tu8 -j $((H-8)) -N8 "$F" | tr -d ' '); WO=$((HDR>>10)); echo "header word $HDR: wosize $WO color $(((HDR>>8)&3)) tag $((HDR&255))"
LEN=$(od -An -tu2 -j $((H+6)) -N2 "$F" | tr -d ' '); PAD=$(od -An -tu1 -j $((H+WO*8-1)) -N1 "$F" | tr -d ' ')
echo "blob len $((12+LEN)) pad byte $PAD (wosize*8-1-len = $((WO*8-1-12-LEN)))"
dd if="$F" bs=1 skip=$((H+12)) count=$LEN status=none; echo
