#!/bin/bash
# Independent oracle for lisp_* fixtures: file -b, readelf -d/-SW, nm, grep -obUaP (SBCL core magic at a page boundary,
# raw HCFG), dd|strings (core build-id), strings -a -t d [-e L = UTF-32LE] | base64 -d (HCFG text literals).
f="$1"; file -b "$f"
echo "== NEEDED"; readelf -d "$f" 2>/dev/null | grep NEEDED
echo "== runtime symbols"; { nm "$f"; nm -D "$f"; } 2>/dev/null | grep -wE "C_toplevel|CHICKEN_main|C_decode_literal|cl_boot|ecl_init_module" | sort -u
echo "== .symtab"; readelf -SW "$f" 2>/dev/null | grep -c "\.symtab"
echo "== SBCL core magic (page-aligned)"
for o in $(grep -obUaP 'LCBS\x00\x00\x00\x00' "$f" | cut -d: -f1); do [ $((o % 4096)) = 0 ] && { echo "core @ $o";
  dd if="$f" bs=1 skip=$o count=128 2>/dev/null | strings -n 8 | head -1 | sed 's/^/build-id /'; }; done
strings -a "$f" | grep -B1 -x 'SBCL %s' | head -1 | grep -E '^[0-9]+\.[0-9]+\.[0-9]+' | sed 's/^/sbcl version /'
echo "== HCFG"
grep -obUaP 'HCFG\x01' "$f" | head -1 | sed 's/:.*//;s/^/raw @ /'
for e in s L; do strings -a -t d -e $e -n 16 "$f" | grep -E 'SENGR[A-Za-z0-9+/=]+$' | while read o s; do
  p=${s%%SENGR*}; w=$([ $e = L ] && echo 4 || echo 1); s=${s#"$p"}
  echo "text(-e $e) @ $((o + ${#p} * w))"; printf '%s' "$s" | base64 -d 2>/dev/null | tail -c +13; echo; done; done
