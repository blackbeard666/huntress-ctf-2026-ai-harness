#!/bin/bash
# Independent oracle for kn_* fixtures: file -b, nm --defined-only (kfun:/kclass:/ktype: + Konan runtime symbols),
# grep -a (ASCII / UTF-16LE runtime cues), grep -aobP for the UTF-16LE base64 of 'HCFG' ("SENG"), od (KString header:
# TypeInfo pointer at -16, uint32 count at -8, pad at -4), readelf -SW (section / symbol at the header), iconv UTF-16LE
# -> ASCII + base64 -d for the config.
F="$1"; file -b "$F"; case "$(file -b "$F")" in ELF*) ;; *) echo "not ELF"; exit 0;; esac
echo "runtime symbols: $(nm --defined-only "$F" 2>/dev/null | awk '{print $3}' | grep -E '^(Konan_main|Konan_start|Kotlin_initRuntimeIfNeeded)$' | sort | tr '\n' ' ')"
echo "kfun: $(nm --defined-only "$F" 2>/dev/null | cut -d' ' -f3- | grep '^kfun:' | LC_ALL=C sort | tr '\n' '|')"
echo "kclass/ktype: $(nm --defined-only "$F" 2>/dev/null | cut -d' ' -f3- | grep -E '^k(class|type):' | LC_ALL=C sort | tr '\n' '|')"
echo "ascii cues: $(grep -aoE 'kotlin\.native\.internal|Kotlin_initRuntimeIfNeeded|Konan_main|kfun:' "$F" | sort -u | tr '\n' ',')"
echo "utf16 cues: $(grep -caP 'k\x00o\x00t\x00l\x00i\x00n\x00\.\x00n\x00a\x00t\x00i\x00v\x00e\x00\.\x00i\x00n\x00t\x00e\x00r\x00n\x00a\x00l\x00' "$F")"
H=$(LC_ALL=C grep -aobP 'S\x00E\x00N\x00G\x00' "$F" | head -1 | cut -d: -f1); [ -z "$H" ] && { echo "no UTF-16 HCFG"; exit 0; }
CNT=$(od -An -tu4 -j $((H-8)) -N4 "$F" | tr -d ' '); PAD=$(od -An -tu4 -j $((H-4)) -N4 "$F" | tr -d ' ')
TI=$(od -An -tx8 -j $((H-16)) -N8 "$F" | tr -d ' ')
echo "UTF-16 HCFG at $H; header at $((H-16)): typeinfo 0x$TI count $CNT pad $PAD"
echo "typeinfo symbol: $(nm --defined-only "$F" 2>/dev/null | awk -v T=$((16#$TI)) 'strtonum("0x"$1)==T && T {print substr($0, index($0,$3))}')"
read -r sec saddr soff < <(readelf -SW "$F" | awk -v O=$H '/^ *\[ *[0-9]+\]/{sub(/^ *\[ *[0-9]+\] */,""); a=strtonum("0x"$3); o=strtonum("0x"$4); s=strtonum("0x"$5); if ($2!="NOBITS" && a && o<=O && O<o+s) print $1, a, o}')
echo "section: $sec; header vaddr 0x$(printf %x $((H-16-soff+saddr)))"
echo "symbol at header: $(nm --defined-only "$F" 2>/dev/null | awk -v A=$((H-16-soff+saddr)) 'strtonum("0x"$1)==A {print substr($0, index($0,$3))}')"
dd if="$F" bs=1 skip=$H count=$((CNT*2)) status=none | iconv -f UTF-16LE -t ASCII | base64 -d | tail -c +13; echo
