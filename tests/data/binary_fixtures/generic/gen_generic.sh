#!/usr/bin/env bash
# Generic-field fixtures (D28 item 13): members built by gcc/strip/dd, expected values from binutils readelf / grep /
# sha256sum -- never from lib.binary. Each <member>.<field>.json is replayed by tests/test_d28_binary_breadth.py:
#   generic_field(member bytes, field, question, answer_format=...) == expected   (expected null = must stay None).
# Re-run:  bash tests/data/binary_fixtures/generic/gen_generic.sh   (rewrites the .bin members and the .json files)
set -euo pipefail
cd "$(dirname "$0")"
src=gf_events.c
cat > "$src" <<'EOF'
#include <stdio.h>
int event_success(int x) { return x + 1; }
int event_failure(int x) { return x - 1; }
int event_decoy(int x) { return x * 3; }
static const char tag[] = "decoy-branch-marker";
int main(int argc, char **argv) { if (argc > 3) puts(tag); return event_success(argc) + event_failure(argc) + event_decoy(argc); }
EOF
GEN_ELF="gcc -O1 -fno-asynchronous-unwind-tables -o gf_c_events.bin gf_events.c"
GEN_STRIP="strip -s -o gf_c_events_stripped.bin gf_c_events.bin"
GEN_RAND="head -c 4096 /dev/urandom > gf_decoy_random.bin"
gcc -O1 -fno-asynchronous-unwind-tables -o gf_c_events.bin "$src"
strip -s -o gf_c_events_stripped.bin gf_c_events.bin
[ -f gf_decoy_random.bin ] || head -c 4096 /dev/urandom > gf_decoy_random.bin

SYMTAB_NAMES='readelf -W --syms MEMBER | awk '"'"'/Symbol table .\.symtab./{f=1;next} /Symbol table/{f=0} f && $1 ~ /^[0-9]+:$/ && NF>=8 {print $8}'"'"''
U="In evidence.zip, Use all d99-- members in ZIP central-directory order. "
INT='{"kind": "integer", "syntax": "base-10 integer with no units, separators, whitespace, or explanatory text"}'
HEX64='{"kind": "pattern", "syntax": "exactly 64 lowercase hexadecimal characters; no prefix, whitespace, or explanatory text"}'
ENUM='{"kind": "enum", "accepted_values": ["true", "false"]}'

emit() {   # emit MEMBER FIELD QUESTION ANSWER_FORMAT_JSON EXPECTED(json literal) GENERATOR ORACLE [decoy]
  python3 - "$@" <<'PY'
import json, sys
m, f, q, af, exp, gen, orc = sys.argv[1:8]
decoy = len(sys.argv) > 8
out = {"kind": "generic_field", "member": m, "field": f, "question": q, "answer_format": json.loads(af),
       "expected": json.loads(exp), "generator_cmd": gen, "oracle_cmd": orc}
if decoy:
    out["decoy"] = True
open(f"{m.rsplit('.', 1)[0]}.{f}.json", "w").write(json.dumps(out, indent=1) + "\n")
PY
}

o_shnum='readelf -h MEMBER | awk -F: '"'"'/Number of section headers/{gsub(/ /,"",$2); print $2}'"'"''
n=$(readelf -h gf_c_events.bin | awk -F: '/Number of section headers/{gsub(/ /,"",$2); print $2}')
emit gf_c_events.bin section_count "${U}Read ELF e_shnum and count the corresponding section-header-table entries, including section index 0. Submit the count in base 10." "$INT" "\"$n\"" "$GEN_ELF" "${o_shnum//MEMBER/gf_c_events.bin}"

o_cnt="${SYMTAB_NAMES} | wc -l"
n=$(bash -c "${o_cnt//MEMBER/gf_c_events.bin}")
emit gf_c_events.bin symbol_count "${U}Count ELF symbol-table entries whose resolved name is nonempty, across the parsed symbol tables used by the ELF parser. Submit the count in base 10." "$INT" "\"$n\"" "$GEN_ELF" "${o_cnt//MEMBER/gf_c_events.bin}"
n=$(bash -c "${o_cnt//MEMBER/gf_c_events_stripped.bin}")
emit gf_c_events_stripped.bin symbol_count "${U}Count ELF symbol-table entries whose resolved name is nonempty, across the parsed symbol tables used by the ELF parser. Submit the count in base 10." "$INT" "\"$n\"" "$GEN_STRIP" "${o_cnt//MEMBER/gf_c_events_stripped.bin}"

o_h="${SYMTAB_NAMES} | grep -cE 'event_(success|decoy|failure)'"
n=$(bash -c "${o_h//MEMBER/gf_c_events.bin}")
emit gf_c_events.bin handler_symbol_count "${U}Count the nonempty ELF symbol names matching /event_(success|decoy|failure)/." "$INT" "\"$n\"" "$GEN_ELF" "${o_h//MEMBER/gf_c_events.bin}"

o_s="printf %s \"\$(${SYMTAB_NAMES} | grep -E 'event_(success|decoy|failure)' | LC_ALL=C sort)\" | sha256sum | cut -c1-64"
n=$(bash -c "${o_s//MEMBER/gf_c_events.bin}")
emit gf_c_events.bin handler_symbols_sha256 "${U}Collect every nonempty ELF symbol name matching /event_(success|decoy|failure)/, sort strings by ascending code-unit order, join with one LF byte and no trailing LF, then SHA-256 those UTF-8 bytes." "$HEX64" "\"$n\"" "$GEN_ELF" "${o_s//MEMBER/gf_c_events.bin}"

o_d="grep -qa decoy MEMBER && echo true || echo false"
n=$(bash -c "${o_d//MEMBER/gf_c_events.bin}")
emit gf_c_events.bin has_decoy_branch "${U}Evaluate this public predicate and submit lowercase true or false: true exactly when the final bytes interpreted as Latin-1 or UTF-16LE contain the case-sensitive text decoy." "$ENUM" "\"$n\"" "$GEN_ELF" "${o_d//MEMBER/gf_c_events.bin}"

emit gf_decoy_random.bin section_count "${U}Read ELF e_shnum and count the corresponding section-header-table entries, including section index 0. Submit the count in base 10." "$INT" "null" "$GEN_RAND" "file gf_decoy_random.bin  # data: no ELF/PE/Mach-O header -> no section table (None)" decoy
ls -1 *.json

# cross-group-campaign-correlation (prebuild): stdlib zipfile writer, expected from the independent cs_oracle.py reader
python3 cs_gen.py cs_evidence.zip cs_decoy_oneday.zip
python3 cs_fixtures.py

# campaign-graph-record-facts (prebuild): D30 Neko members (GM) + gcc ELFs with a stdlib-written GRPH record and a
# bad-crc decoy; expected from the independent cg_oracle.sh reader (python crc check + jq)
python3 cg_gen.py
python3 cg_fixtures.py
