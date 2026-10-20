#!/bin/bash
# Independent oracle for ghcrs20_*.bin: binutils readelf/strings, coreutils od/tail/sha256sum, grep -P. Prints JSON.
# usage: bash ghcrs20_oracle.sh <file>
f=$1; sz=$(stat -c %s "$f")
li=$(readelf -p .debug-ghc-link-info "$f" 2>/dev/null | tr -d '\n')
jarr() { python3 -c 'import json,sys; print(json.dumps([l for l in sys.stdin.read().split("\n") if l]))'; }
q() { grep -oP "$1" <<<"$li" | head -1; }
ver=$(strings -a "$f" | grep -B1 -F '(GHC version %s for %s)' | head -1)
hs=$(q 'hsLibs = \[\K[^]]*' | grep -oP '"[^"]*"' | tr -d '"' | jarr)
ex=$(q 'extraLibs = \[\K[^]]*' | grep -oP '"[^"]*"' | tr -d '"' | jarr)
need=$(readelf -dW "$f" 2>/dev/null | grep -oP 'NEEDED.*\[\K[^]]+' | jarr)
gold=$(readelf -nW "$f" 2>/dev/null | grep -oP 'Version: \Kgold.*')
S=$(mktemp); readelf -sW "$f" 2>/dev/null | awk '$1 ~ /^[0-9]+:$/ && $8 != "" {sub(/@.*/, "", $8); print $8}' > "$S"
fam=$(strings -a "$f" | grep -oP '"family":"\K[^"]+' | head -1); eff=$(strings -a "$f" | grep -oP '"effects":"\K[^"]+' | head -1)
o=$(grep -obUa RS20 "$f" | tail -1 | cut -d: -f1)
rd() { od -An -t"$1" -j "$2" -N "$3" "$f" | tr -d ' '; }
if [ -n "$o" ]; then n=$(rd u4 $((o+8)) 4); s=$(rd u2 $((o+12)) 2); st=$(rd x1 $((o+16)) 32 | tr -d '\n'); act=$(tail -c "$s" "$f" | sha256sum | cut -c1-64); fi
shoff=$(readelf -hW "$f" 2>/dev/null | grep -oP 'Start of section headers:\s+\K\d+'); shn=$(readelf -hW "$f" 2>/dev/null | grep -oP 'Number of section headers:\s+\K\d+')
python3 - "$sz" "$ver" "$hs" "$ex" "$need" "$gold" "$fam" "$eff" "${o:-}" "${n:-}" "${s:-}" "${st:-}" "${act:-}" "${shoff:-}" "${shn:-}" "$f" "$(rd u1 $((${o:-0}+4)) 1)" "$(q 'RtsOpts\w+')" "$S" <<'PY'
import json, re, sys
a = sys.argv[1:]
sz, ver, hs, ex, need, gold, fam, eff, o, n, s, st, act, shoff, shn, path, v, rto, sf = a
syms = [l for l in open(sf).read().split("\n") if l]
hs, ex, need = json.loads(hs), json.loads(ex), json.loads(need)
pv = {m.group(1): m.group(2) for m in (re.match(r"^-lHS(.+?)-(\d+(?:\.\d+)*)(?:-[0-9a-f]{4,64})?$", x) for x in hs) if m}
ms = [x for x in syms if x.startswith(("Main_", "ZCMain_"))]
e = {"ghc_version": ver or "none", "has_ghc_link_info": "true" if hs else "false", "hs_libs": hs, "extra_libs": ex,
     "base_version": pv.get("base", "none"), "ghc_internal_version": pv.get("ghc-internal", "none"),
     "rts_version": pv.get("rts", "none"), "rts_opts_enabled": rto or "none", "needed": need,
     "gold_version": gold or "none", "linker": "gold" if gold else "none", "symbol_count": len(syms),
     "closure_symbol_count": sum(x.endswith("_closure") for x in syms),
     "info_symbol_count": sum(x.endswith("_info") for x in syms), "main_symbols": ms,
     "main_closures": [x for x in ms if x.endswith("_closure")], "trace_family": fam or "none",
     "trace_effects": eff or "none"}
ok = bool(o) and int(o) + 48 + int(n) + int(s) == int(sz) and st == act
img = int(shoff) + int(shn) * 64 if shoff and shn else "none"
r = {"image_end": img}
if ok:
    scr = open(path, "rb").read()[-int(s):].decode("latin-1")
    r.update({"overlay_offset": int(o), "overlay_size": int(sz) - int(o), "overlay_version": int(v),
              "hcfg_resource_size": int(n), "scratch_size": int(s), "scratch_sha256": st, "scratch_text": scr,
              "end_bounds_ok": "true"})
else:
    r.update(dict.fromkeys(("overlay_offset", "overlay_size", "overlay_version", "hcfg_resource_size", "scratch_size",
                            "scratch_sha256", "scratch_text", "end_bounds_ok"), "none"))
print(json.dumps({"ghc": e, "rs20": r}))
PY
rm -f "$S"
