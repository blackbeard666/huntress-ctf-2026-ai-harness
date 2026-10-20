#!/usr/bin/env bash
# Offline generator for the jsexe_* fixtures (JS-runtime single executables). Real writers:
#   Node SEA: tools/node `node --experimental-sea-config` (v24) writes the SEA blob; it is injected into a small gcc host
#             ELF as postject's ELF note (owner NODE_SEA_BLOB, type 0; via objcopy) and the sentinel fuse ':0'->':1'.
#   Bun:      tools/npm-bun (npm install bun@1.2.23) bun 1.2.23 `bun build --compile` (~100 MB); the fixture keeps the gcc host ELF + the LAST
#             4096 bytes of the real executable (payload + Offsets + "\n---- Bun! ----\n" + u64) byte-for-byte.
# usage (repo root): bash tests/data/binary_fixtures/jsexe_gen.sh
set -euo pipefail
R=$(cd "$(dirname "$0")/../../.." && pwd); F="$R/tests/data/binary_fixtures"; W=${TMPDIR:-/tmp}/jsexe_gen; rm -rf "$W"; mkdir -p "$W"; cd "$W"
NODE="$R/tools/node/bin/node"; BUN=$(ls "$R"/tools/npm-bun/node_modules/@oven/*/bin/bun | head -1); PY="$R/.venv/bin/python"
FUSE=NODE_SEA_FUSE_fce680ab2cc467b6e072b8b5df1996b2
printf '#include <stdio.h>\nvolatile const char fuse[] = "%s:0";\nint main(void){ puts((const char*)fuse); return 0; }\n' "$FUSE" > host.c
gcc -Os -s -o host host.c
inject() {  # $1 blob  $2 out: an ELF note owner NODE_SEA_BLOB type 0 desc=blob (postject's note; LIEF 1.0 refuses to
            # write an unknown note, so GNU objcopy adds it as SHT_NOTE section .note.node_sea) + postject's fuse flip
  python3 -c "import struct,sys; d=open(sys.argv[1],'rb').read(); nm=b'NODE_SEA_BLOB\\0'; p=lambda b: b+b'\\0'*(-len(b)%4); open(sys.argv[2],'wb').write(struct.pack('<III',len(nm),len(d),0)+p(nm)+p(d))" "$1" "$1.note"
  objcopy --add-section .note.node_sea="$1.note" host "$2"
  perl -pi -e "s/${FUSE}:0/${FUSE}:1/" "$2"
}
# 1. Node SEA, plain main script (exec-argv ext default, warning disabled)
mkdir -p n1 && cat > n1/greeter.js <<'JS'
// sea greeter
const who = process.argv[2] || "huntress";
console.log("hello " + who + " from a single executable");
JS
printf '{"main":"n1/greeter.js","output":"n1.blob","disableExperimentalSEAWarning":true}' > n1.json
"$NODE" --experimental-sea-config n1.json; inject n1.blob "$F/jsexe_node_sea_elf.bin"
# 2. Node SEA with two assets + useCodeCache=false, warning enabled
mkdir -p n2 && printf 'module.exports = 1;\nconst { getAsset } = require("node:sea");\nconsole.log(getAsset("motd.txt", "utf8"));\n' > n2/main.js
printf 'welcome to the arena\n' > n2/motd.txt; printf 'k=v\n' > n2/app.cfg
printf '{"main":"n2/main.js","output":"n2.blob","assets":{"motd.txt":"n2/motd.txt","app.cfg":"n2/app.cfg"}}' > n2.json
"$NODE" --experimental-sea-config n2.json; inject n2.blob "$F/jsexe_node_sea_assets.bin"
# 3. decoy: the unflipped host (fuse ':0', no NODE_SEA_BLOB note)
cp host "$F/jsexe_decoy_unfused.bin"
# 4. Bun --compile, 2 modules (ESM import)
mkdir -p b1 && printf 'import { greet } from "./lib.js";\nconsole.log(greet("bun"));\n' > b1/app.js
printf 'export function greet(n) { return "hi " + n; }\n' > b1/lib.js
"$BUN" build --compile b1/app.js --outfile b1.exe >/dev/null
cat host <(tail -c 4096 b1.exe) > "$F/jsexe_bun_elf.bin"
# 5. Bun --compile --minify with an embedded file asset (second module in the graph)
mkdir -p b2 && printf 'import cfg from "./banner.txt" with { type: "file" };\nimport { file } from "bun";\nconsole.log(await file(cfg).text());\n' > b2/cli.ts
printf 'BANNER-TEXT\n' > b2/banner.txt
"$BUN" build --compile --minify b2/cli.ts --outfile b2.exe >/dev/null
cat host <(tail -c 4096 b2.exe) > "$F/jsexe_bun_asset.bin"
# 6. decoy: trailer string present (a Bun-aware tool's .rodata) but no Offsets/module graph before it
printf '#include <stdio.h>\nconst char t[] = "\\n---- Bun! ----\\n";\nint main(void){ return puts(t); }\n' > d.c
gcc -Os -s -o "$F/jsexe_decoy_buntext.bin" d.c
ls -l "$F"/jsexe_*.bin
# 7. Deno 1.x compile layout (SYNTHETIC: no deno writer offline) -- host ELF + bundle JS + metadata JSON + trailer
#    "d3n0l4nd" + u64 BE bundle_pos + u64 BE metadata_pos (python3 struct; Deno's cli/standalone.rs 1.x layout)
python3 - host "$F/jsexe_deno_trailer.bin" <<'PYEOF'
import json, struct, sys
h = open(sys.argv[1], "rb").read()
js = b'console.log("deno compiled");\nDeno.exit(0);\n'
meta = json.dumps({"argv": [], "unstable": False, "seed": None, "location": None, "v8_flags": [],
                   "entrypoint": "file:///work/main.ts"}).encode()
open(sys.argv[2], "wb").write(h + js + meta + b"d3n0l4nd" + struct.pack(">QQ", len(h), len(h) + len(js)))
PYEOF
# 8. decoy: the trailer magic as a .rodata string (a deno-aware scanner), not at EOF
printf '#include <stdio.h>\nconst char t[] = "d3n0l4nd";\nint main(void){ return puts(t); }\n' > dd.c
gcc -Os -s -o "$F/jsexe_decoy_denotext.bin" dd.c
