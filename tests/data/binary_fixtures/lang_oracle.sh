#!/bin/bash
# Independent oracle for lang_facts: binutils (readelf -SW / -p .comment, nm, nm --demangle=dlang), file, grep -a, perl.
# usage: bash lang_oracle.sh FILE  -> one JSON object of expected values
f="$1"
kind=$(file -b "$f")
case "$kind" in ELF*|PE32*|Mach-O*|WebAssembly*) ;; *) echo '{"facts": null}'; exit 0;; esac
readelf -hW "$f" >/dev/null 2>&1 || { echo '{"facts": null}'; exit 0; }
SEC=$(readelf -SW "$f" 2>/dev/null | sed -n 's/^ *\[ *[0-9]*\] \([^ ]*\) .*/\1/p')
SYM=$(nm -a "$f" 2>/dev/null; nm -D "$f" 2>/dev/null)
DEF=$(nm --defined-only "$f" 2>/dev/null | awk '$2 ~ /^[Tt]$/ {print $3}')
CMT=$(readelf -p .comment "$f" 2>/dev/null)
s(){ grep -qaF -- "$1" "$f"; }
y(){ if eval "$1"; then echo true; else echo false; fi; }
swift=$(y 'grep -q "^_*swift5_" <<<"$SEC" || awk "{print \$NF}" <<<"$SYM" | grep -qE "^_?\\\$[sS](s|[1-9])" || s swift_retain')
objc=$(y 'grep -qE "^(__objc_|\.objc_)" <<<"$SEC" || awk "{print \$NF}" <<<"$SYM" | grep -qE "^(objc_msg|__objc_load|\._OBJC_|_OBJC_CLASS_\\\$_)" || s objc_msg')
nim=$(y 's NimMain')
zig=$(y 'grep -qi zig <<<"$CMT" || s ziglang')
d=$(y 'awk "{print \$NF}" <<<"$SYM" | grep -qE "^_D(4core|2rt|6object)" || s _D4core')
fpc=$(y 'grep -qx .fpcdata <<<"$SEC" || s "FPC 3."')
crystal=$(y 's Crystal::')
gnat=$(y 's __gnat_ || awk "{print \$NF}" <<<"$SYM" | grep -qE "^(adainit|ada__)"')
go=$(y 'grep -qx .gopclntab <<<"$SEC" || s "Go buildinf:"')
rust=$(y 's /rustc/ || awk "{print \$NF}" <<<"$SYM" | grep -qE "^rust_(panic|begin_unwind)"')
nim_m=$(grep -E '__[A-Za-z0-9]+_u[0-9]+$' <<<"$DEF" | grep -vE '__(system|[A-Za-z0-9]*Z[A-Za-z0-9]*)_u[0-9]+$' | grep -vE '^eq.*___' | sort -u)
d_m=$(grep -E '^_D[1-9]' <<<"$DEF" | grep -vE '^_D(4core|3std|2rt|6object|2gc|3etc|3ldc|3gcc)' | grep -vE '^_D[0-9]+[A-Za-z0-9_]+[0-9]+__' | sort -u)
d_dm=$(for m in $d_m; do echo "$m" | c++filt --format=dlang 2>/dev/null; done | sed 's/(.*//' | sort -u)
sw_m=$(grep -E '^\$s[1-9]' <<<"$DEF" | perl -ne 'chomp; next unless /^\$s(\d+)/; $n=$1; $mod=substr($_, length("\$s$n"), $n); next if $mod =~ /^(_|Foundation|Swift$|Dispatch$|Glibc$|Synchronization$)/; $r=substr($_, length("\$s$n")+$n); print "$_\n" if $r =~ /^[1-9]\d*[A-Za-z]/ && do { ($k)=$r=~/^(\d+)/; substr($r,length($k)+$k,1) !~ /[VCOP]/ }' | sort -u)
cls=$(awk '{print $NF}' <<<"$SYM" | sed -n 's/^\._OBJC_METACLASS_//p' | sort -u)
sel=$(awk '{print $NF}' <<<"$SYM" | sed -n 's/^\.objc_sel_name_//p' | sort -u)
python3 -I - "$swift" "$objc" "$nim" "$zig" "$d" "$fpc" "$crystal" "$gnat" "$go" "$rust" "$nim_m" "$d_m" "$d_dm" "$sw_m" "$cls" "$sel" <<'PY'
import json, sys
a = sys.argv[1:]
L = lambda s: [x for x in s.split("\n") if x]
keys = ["swift", "objc", "nim", "zig", "d", "fpc", "crystal", "gnat", "go", "rust"]
out = {f"has_{k}_runtime": v for k, v in zip(keys, a[:10])}
out.update({"nim_procs_mangled": L(a[10]), "d_functions_mangled": L(a[11]), "d_functions": L(a[12]),
            "swift_functions_mangled": L(a[13]), "objc_classes": L(a[14]), "objc_selectors": L(a[15])})
print(json.dumps({"facts": out}))
PY
