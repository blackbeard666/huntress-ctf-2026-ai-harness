"""Generator for the split_* fixtures (v=3 SPLIT literal-array carrier, every host syntax). stdlib only (binascii /
base64 / gzip) -- independent of lib.codec. Run: python3 -I tests/data/script_fixtures/split_array_gen.py
Each fixture's oracle_cmd is a shell one-liner (grep/sed/tr + xxd/base64/gunzip) that re-derives expected_plain."""
import base64
import binascii
import gzip
import json
import sys
from pathlib import Path

D = Path(__file__).resolve().parent
PLANS = [  # D17 plans (challenges/day17/scripting-fetch-quest triage, GM-confirmed)
    "v=3|language=javascript|role=downloader|verdict=suspicious|attack=T1105|adapter=http_client|host_profile=hta_jscript|obfuscation_profile=fragmented_hex|stage_profile=cross_language_handoff|next_language=vbscript|stage_count=3|steps=profile_host,decode_configuration,dispatch_language|campaign_id=JAVASCRIPT-8dbe7f0d|url=https://javascript-8dbe7f0d9b.example.invalid/stage|file_path=/tmp/huntress-javascript/.8dbe7f0d9b417a84.stage",
    "v=3|language=jscript|role=launcher|verdict=suspicious|attack=T1059|adapter=process_builder|host_profile=sct_scriptlet|obfuscation_profile=hex_base64|stage_profile=three_stage_decode_write_launch|next_language=jscript|stage_count=3|steps=decode_embedded,write_file,dispatch_process|campaign_id=JSCRIPT-5a93ad01|url=https://jscript-5a93ad0131.example.invalid/stage|file_path=/tmp/huntress-jscript/.5a93ad01316d3fe7.stage",
    "v=3|language=jscript|role=staged_chain|verdict=suspicious|attack=T1059|adapter=operation_graph|host_profile=wsf_jscript|obfuscation_profile=base64|stage_profile=two_stage_download_execute|next_language=jscript|stage_count=2|steps=acquire_remote,dispatch_process|campaign_id=JSCRIPT-3d2d3d0d|url=https://jscript-3d2d3d0db0.example.invalid/stage|file_path=/tmp/huntress-jscript/.3d2d3d0db00119b5.stage",
    "v=3|language=php|role=staged_chain|verdict=suspicious|attack=T1059|adapter=operation_graph|host_profile=php_webshell|obfuscation_profile=plain_hex|stage_profile=single_descriptor|next_language=python|stage_count=2|steps=decode_configuration,return_configuration|campaign_id=PHP-25be44a3|url=https://php-25be44a3ee.example.invalid/stage|file_path=/tmp/huntress-php/.25be44a3ee3f31c2.stage",
    "v=3|language=vbscript|role=staged_chain|verdict=suspicious|attack=T1059|adapter=operation_graph|host_profile=wsf_mixed|obfuscation_profile=hex_base64|stage_profile=three_stage_decode_write_launch|next_language=batch|stage_count=3|steps=decode_embedded,write_file,dispatch_process|campaign_id=VBSCRIPT-79fe0e64|url=https://vbscript-79fe0e646b.example.invalid/stage|file_path=/tmp/huntress-vbscript/.79fe0e646bd8c75c.stage",
]
ENC = {"HEX": lambda b: binascii.hexlify(b).decode(), "B64": lambda b: base64.b64encode(b).decode(),
       "GZB64": lambda b: base64.b64encode(gzip.compress(b, 9, mtime=0)).decode()}
DEC = {"HEX": "xxd -r -p", "B64": "base64 -d", "GZB64": "base64 -d | gunzip"}


def chunks(plan, tag, n=48, tagged=True):
    mat = ENC[tag](plan.encode())
    cs = [mat[i:i + n] for i in range(0, len(mat), n)]
    if tagged:
        cs[0] = f"{tag}-{cs[0]}"
    return cs


def q(cs, quote='"', sep=",\n    "):
    return sep.join(f"{quote}{c}{quote}" for c in cs)


# name -> (ext, plan index, tag, tagged, builder(cs) -> source, extract one-liner printing the chunks one per line)
LIT = r"""grep -o "[\"'][A-Za-z0-9+/=_-]\{2,\}[\"']" F | tr -d "\"'" """
CASES = {
    "py_join": ("py", 0, "HEX", True, lambda cs: "# HUNTRESS_ANALYSIS_V1:SPLIT\nimport sys\n\nPLAN = \"\".join([\n    " + q(cs) + ",\n])\n\ndef build():\n    return bytes.fromhex(PLAN.split('-', 1)[1])\n", LIT),
    "py_tuple": ("py", 1, "B64", True, lambda cs: "# HUNTRESS_ANALYSIS_V1:SPLIT\nPARTS = (\n    " + q(cs, "'") + ",\n)\nPLAN = ''.join(PARTS)\n", LIT),
    "ps_join": ("ps1", 2, "GZB64", True, lambda cs: "# HUNTRESS_ANALYSIS_V1:SPLIT\n$parts = @(\n    " + q(cs, "'", ",\n    ") + "\n)\n$blob = -join $parts\nWrite-Output $blob.Length\n", LIT),
    "ps_stringjoin": ("ps1", 3, "HEX", True, lambda cs: "<# HUNTRESS_ANALYSIS_V1:SPLIT #>\n$plan = [string]::Join('', @(" + q(cs, '"', ", ") + "))\n", LIT),
    "lua_concat": ("lua", 4, "B64", True, lambda cs: "-- HUNTRESS_ANALYSIS_V1:SPLIT\nlocal parts = {\n  " + q(cs, '"', ";\n  ") + "\n}\nlocal plan = table.concat(parts)\nreturn plan\n", LIT),
    "lua_insert": ("lua", 0, "GZB64", True, lambda cs: "-- HUNTRESS_ANALYSIS_V1:SPLIT\nlocal t = {}\n" + "".join(f'table.insert(t, "{c}")\n' for c in cs) + "local plan = table.concat(t, \"\")\n", LIT),
    "perl_join": ("pl", 1, "HEX", True, lambda cs: "# HUNTRESS_ANALYSIS_V1:SPLIT\nuse strict;\nmy $plan = join('', (\n    " + q(cs, "'") + ",\n));\nprint length($plan), \"\\n\";\n", LIT),
    "perl_qw": ("pl", 2, "B64", True, lambda cs: "# HUNTRESS_ANALYSIS_V1:SPLIT\nmy @p = qw(\n    " + "\n    ".join(cs) + "\n);\nmy $plan = join '', @p;\n",
                "sed -n '/qw(/,/);/p' F | sed '1d;$d' | tr -d ' '"),
    "ruby_join": ("rb", 3, "GZB64", True, lambda cs: "# HUNTRESS_ANALYSIS_V1:SPLIT\nplan = [\n  " + q(cs, '"', ",\n  ") + "\n].join\nputs plan.size\n", LIT),
    "ruby_w_nomarker": ("rb", 4, "HEX", False, lambda cs: "# carrier\nplan = %w[\n  " + "\n  ".join(cs) + "\n].join\nputs [plan].pack('H*')\n",
                        "sed -n '/%w\\[/,/\\]/p' F | sed '1d;$d' | tr -d ' '"),
    "vbs_join": ("vbs", 0, "B64", True, lambda cs: "' HUNTRESS_ANALYSIS_V1:SPLIT\nDim plan\nplan = Join(Array( _\n    " + q(cs, '"', ", _\n    ") + "), \"\")\nWScript.Echo Len(plan)\n", LIT),
    "ahk_loop": ("ahk", 1, "GZB64", True, lambda cs: "; HUNTRESS_ANALYSIS_V1:SPLIT\nparts := [" + q(cs, '"', ", ") + "]\nplan := \"\"\nfor i, p in parts\n    plan .= p\nMsgBox % StrLen(plan)\n", LIT),
    "autoit_join": ("au3", 2, "HEX", True, lambda cs: f"; HUNTRESS_ANALYSIS_V1:SPLIT\n#include <Array.au3>\nLocal $aParts[{len(cs)}] = [ _\n    " + q(cs, '"', ", _\n    ") + "]\nLocal $sPlan = _ArrayToString($aParts, \"\")\n", LIT),
    "applescript_tid": ("applescript", 3, "B64", True, lambda cs: "-- HUNTRESS_ANALYSIS_V1:SPLIT\nset parts to {" + q(cs, '"', ", \u00ac\n    ") + "}\nset AppleScript's text item delimiters to \"\"\nset plan to parts as text\n", LIT),
    "applescript_end_nomarker": ("applescript", 4, "GZB64", False, lambda cs: "set parts to {}\n" + "".join(f'set end of parts to "{c}"\n' for c in cs) + "set AppleScript's text item delimiters to \"\"\nset plan to parts as text\n", LIT),
    "msbuild_chunk": ("proj", 0, "HEX", True, lambda cs: "<Project xmlns=\"http://schemas.microsoft.com/developer/msbuild/2003\">\n  <!-- HUNTRESS_ANALYSIS_V1:SPLIT -->\n  <ItemGroup>\n" + "".join(f"    <Chunk>{c}</Chunk>\n" for c in cs) + "  </ItemGroup>\n  <Target Name=\"Build\"><Message Text=\"@(Chunk, '')\" /></Target>\n</Project>\n",
                      "grep -o '<Chunk>[^<]*</Chunk>' F | sed 's/<[^>]*>//g'"),
    "msbuild_include": ("proj", 1, "B64", True, lambda cs: "<Project>\n  <!-- HUNTRESS_ANALYSIS_V1:SPLIT -->\n  <ItemGroup>\n" + "".join(f"    <Chunk Include=\"{c}\" />\n" for c in cs) + "  </ItemGroup>\n</Project>\n",
                        "grep -o 'Include=\"[^\"]*\"' F | cut -d'\"' -f2"),
    "batch_set": ("bat", 2, "HEX", True, lambda cs: "@echo off\nrem HUNTRESS_ANALYSIS_V1:SPLIT\n" + "".join(f"set c{i + 1}={c}\n" for i, c in enumerate(cs)) + "set plan=" + "".join(f"%c{i + 1}%" for i in range(len(cs))) + "\necho %plan%\n",
                  "grep -o '^set c[0-9]*=.*' F | cut -d= -f2"),
    "batch_append": ("bat", 3, "B64", True, lambda cs: "@echo off\nrem HUNTRESS_ANALYSIS_V1:SPLIT\nset \"p=\"\n" + "".join(f"set \"p=%p%{c}\"\n" for c in cs) + "echo %p%\n",
                     "grep -o '^set \"p=%p%[^\"]*' F | sed 's/.*%p%//'"),
}


def main():
    for name, (ext, pi, tag, tagged, build, extract) in CASES.items():
        plan = PLANS[pi]
        src = build(chunks(plan, tag, tagged=tagged))
        f = D / f"split_{name}.{ext}"
        f.write_text(src, encoding="utf-8")
        strip = " | sed 's/^[A-Za-z0-9_]*-//'" if tagged else ""
        oracle = f"{extract.replace('F', f.name)} | tr -d '\\n'{strip} | {DEC[tag]}"
        (D / f"split_{name}.json").write_text(json.dumps({
            "expected_plain": plan, "decoy": False,
            "generator_cmd": f"python3 -I tests/data/script_fixtures/split_array_gen.py  ({name}: stdlib {tag} of D17 plan #{pi}, 48-char chunks{', first tagged ' + tag + '-' if tagged else ', untagged'})",
            "oracle_cmd": f"cd tests/data/script_fixtures && {oracle}"}, indent=1) + "\n")
    # decoys: SPLIT marker + chunk arrays that are not a plan (truncated hex, benign word list)
    bad = [f"HEX-{c}" if i == 0 else c for i, c in enumerate(
        binascii.hexlify(b"Quarterly report builder|owner=finance|schedule=monthly|output=/srv/reports/q3.pdf").decode()[i:i + 48]
        for i in range(0, 168, 48))]
    (D / "split_decoy_benign_hex.js").write_text("// HUNTRESS_ANALYSIS_V1:SPLIT\nconst P = [\n  " + q(bad, '"', ",\n  ") + "\n].join(\"\");\n")
    (D / "split_decoy_benign_hex.json").write_text(json.dumps({
        "expected_plain": None, "decoy": True,
        "generator_cmd": "python3 -I tests/data/script_fixtures/split_array_gen.py  (SPLIT marker + HEX chunks of a benign k=v report config, no v= plan)",
        "oracle_cmd": "cd tests/data/script_fixtures && grep -o '\"[^\"]*\"' split_decoy_benign_hex.js | tr -d '\"\\n' | sed 's/^HEX-//' | xxd -r -p | grep -c '^v='  # 0: decodes, but to no plan"}, indent=1) + "\n")
    (D / "split_decoy_words.lua").write_text("-- HUNTRESS_ANALYSIS_V1:SPLIT\nlocal parts = {\n  \"alpha-bravo\",\n  \"charlie\",\n  \"delta\",\n  \"echo\",\n  \"foxtrot\",\n}\nprint(table.concat(parts, \"\"))\n")
    (D / "split_decoy_words.json").write_text(json.dumps({
        "expected_plain": None, "decoy": True,
        "generator_cmd": "python3 -I tests/data/script_fixtures/split_array_gen.py  (benign word list behind the SPLIT marker)",
        "oracle_cmd": "cd tests/data/script_fixtures && grep -o '\"[a-z-]*\"' split_decoy_words.lua | tr -d '\"\\n' | grep -c 'v=3'  # 0: no plan"}, indent=1) + "\n")


if __name__ == "__main__":
    sys.exit(main())
