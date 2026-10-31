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

# backfill-spec-grammar-extensions (prebuild): import / DT_NEEDED / export sets; gcc + zig cc members, binutils oracles
# (IE_REBUILD=1 rebuilds the members; needs tools/ziglang)
bash ie_gen.sh

# theme-backfill-d18-d28-fields: D27 per-role toolchain fingerprints (debug_format / hash_style / dwarf_producer);
# gcc + GNU as --gstabs members, binutils readelf oracles
sh tc_gen.sh
python3 tc_fixtures.py

# optimization-equivalence-facts (prebuild): gcc -O0/-O3 -g twins + the D29 Fraternal Twins pair; readelf / objcopy /
# sha256sum oracles (pair facts: ot_pair_check.sh vs cmp -l)
sh ot_gen.sh
python3 ot_fixtures.py

# behavior-profile-from-trace-templates (prebuild): complete huntress.binary.dynamic_trace.v1 JSON records embedded by gcc
# (char + -fshort-wchar UTF-16LE literals) and javac/jar, a template-only decoy, plus the D28 family-a / false-friend
# members (GM artifacts, copied verbatim); expected = strings [-el] | grep | jq oracles (bp_src/mkfx.py runs them)
(cd bp_src && gcc -O0 -o ../bp_trace_records.elf tr.c && gcc -O0 -fshort-wchar -o ../bp_trace_wide.elf tw.c &&
 gcc -O0 -o ../bp_trace_template.elf tpl.c && javac --release 8 -d . TraceRec.java &&
 jar cfm ../bp_trace_records.jar m.txt TraceRec.class && rm -f TraceRec.class)
python3 bp_src/mkfx.py "$PWD"

# toolchain-attribution-verdicts (prebuild): compiler / compiler_version / linker / libc / linkage / pie / dwarf_version;
# gcc / clang-18 / gcc -static -s / aarch64-linux-gnu-gcc -static / zig cc (musl) / banner-stripped decoy + the two D27
# GM role members; expected = readelf / file / strings oracles (ta_fixtures.py)
sh ta_gen.sh
python3 ta_fixtures.py

# gf-func-body (prebuild): symbol-addressed function bodies (disassembly / recover_code / <sym>_size / <sym>_address);
# gcc -O2 / -O0 / -m32 -c + strip -s members, expected = objdump -M intel / readelf -sW oracles (fb_src/fb_fixtures.py)
bash fb_src/fb_gen.sh
python3 fb_src/fb_fixtures.py
# gf-pe-conventions (prebuild): MinGW-w64 gcc PE members ('/N' long names, raw vs VirtualSize .text extent, COFF
# NumberOfSymbols vs aux-skipped names) + truncated decoy; oracles = mingw objdump -h/-t and pefile one-liners
# (PEC_REBUILD=1 rebuilds the members; needs tools/mingw)
bash "$(dirname "$0")/pec_src/pec_fixtures.sh"

# gf-predicate-grammar (prebuild): spec-grammar conjunction / negation / every / at-least-N clauses and DT_NEEDED /
# imported-DLL / dylib / exported-symbol counts over the gf_c_* (gcc ELF), gf_pe_* (zig PE) and two zig cc Mach-O
# members; expected = readelf / pefile / macholib / lief one-liners (pg_src/pg_fixtures.py), decoys -> null
sh pg_src/pg_gen.sh
python3 pg_src/pg_fixtures.py

# gf-dotnet-counts (prebuild): .NET TypeDef / MethodDef / Field counts (<Module> / nested / compiler-generated
# qualifiers), kind predicates, sorted name-set sha256 and #US user-string predicates over Roslyn C# / VB.NET builds;
# expected = dnc_src/dnc_oracle.sh (System.Reflection.Metadata, not dnfile); decoys: native PE, unnamed absent type
bash dnc_src/dnc_gen.sh
python3 dnc_src/dnc_fixtures.py

# gf-runtime-markers (prebuild): has_zig_runtime (zig 0.17 build-exe PE/ELF + the GM d10 Zig PE twin) and has_v_runtime
# (GM d27 V gcc/tcc builds); decoys: zig-cc C PE, gcc C ELF. expected from binutils strings / nm (RTM_REBUILD=1 rebuilds)
bash rtm_gen.sh

# gf-macho (prebuild): Mach-O segment / load-command / section (per-segment, per-slice, all-slices) / symbol (stabs
# in/out, nsyms, external / undefined) counts, has_<x>_section, fat slice_count / is_fat over zig cc x86_64 / arm64 -g /
# MH_OBJECT / plain members + an llvm-lipo fat member; expected = llvm-otool-18 / llvm-objdump-18 --macho / llvm-nm-18 /
# macholib one-liners (mo_src/mo_fixtures.py); decoys: thin slice_count, ELF ncmds, absent __TEXT,__hctf
sh mo_src/mo_gen.sh
python3 mo_src/mo_fixtures.py "$PWD"
# family-cluster-similarity-facts: pair metrics (<a>_<b>_diff_bytes / first_diff / text_sha256_equal / string_jaccard /
# func_hash_overlap / same_sections), family_members, false_friend, strangers, cluster_count over gcc -O2/-O0/-g builds
# (ms_gcc.zip) and the D28 trio (ms_d28_trio.zip); expected = cmp / objcopy / strings / readelf / objdump / pyelftools
sh ms_src/ms_gen.sh
python3 ms_src/ms_fixtures.py "$PWD"

# false-friend-discriminator (prebuild): partition_family over neutrally named members (sample-1..5 / specimen-a..c /
# member-1..4): family by HCFG config equality, campaign prefix or .text sha256; family_members / family_size /
# stranger_members / false_friend_member / family_config_campaign; decoys: tied 2+2 classes, prefix family without a
# common campaign. expected = pf_src/pf_fixtures.py (stdlib HCFG decoder + objcopy .text sha256, not lib.binary)
sh pf_src/pf_gen.sh
python3 pf_src/pf_fixtures.py "$PWD"

# fuzzy-hash-fields (ssdeep / TLSH / imphash / telfhash / <a>_<b>_ssdeep_score / <a>_<b>_tlsh_distance): one new member
# pair (same C source, different TAG string) zipped as family-a/family-b; the other members are reused. expected =
# fh_fixtures.py: libfuzzy 2.14.1 (tools/ssdeep/ssdeep.sh), py-tlsh, pefile.get_imphash, telfhash 0.9.8 in a throwaway
# venv (pip install py-tlsh pefile pyelftools telfhash) -- never lib.binary
gcc -O0 -o fh-family-a.elf fh_src/fam.c
gcc -O0 -DTAG='"bravo-variant"' -o fh-family-b.elf fh_src/fam.c
rm -f fh_pair.zip && zip -X -q fh_pair.zip fh-family-a.elf fh-family-b.elf && rm -f fh-family-a.elf fh-family-b.elf
"${FH_PY:-python3}" fh_fixtures.py
