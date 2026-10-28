"""Fixture generator for descriptor-decode-call-wrapper: the descriptor literal sits inside the host language's own
decode call (HCL base64decode / jsondecode, Tcl `binary decode base64 {..}`, zsh `$(print -r -- .. | base64 -d)`,
Kotlin `String(Base64.getDecoder().decode(".."))`), with a tag-only LYR marker, no marker, or a full marker that must win.
The plan is encoded with stdlib codecs only (base64 / binascii / gzip / codecs.rot13); `expected_plain` comes from the
oracle command recorded in each json (terraform console, tclsh, coreutils base64/rev/tr/xxd/gunzip pipelines).
Run:  python3 -I tests/data/script_fixtures/dcall_gen.py
"""
import base64
import codecs
import gzip
import json
from pathlib import Path

D = Path(__file__).resolve().parent


def plan(lang, role, obf, cid):
    return (f"v=3|language={lang}|role={role}|verdict=suspicious|attack=T1059|adapter=process_spawn|"
            f"host_profile=standalone|obfuscation_profile={obf}|stage_profile=single_stage|next_language=powershell|"
            f"campaign_id={lang.upper()}-{cid}|url=https://{lang}-{cid}4e.example.invalid/stage")


def b64(x):
    return base64.b64encode(x if isinstance(x, bytes) else x.encode()).decode()


CASES = []


def case(name, ext, src, plan_text, gen, oracle, decoy=False, note=""):
    CASES.append((name, ext, src, plan_text, gen, oracle, decoy, note))


TF_ORACLE = ("sed -n 's/.*= \\(base64decode(\"[^\"]*\")\\).*/\\1/p' {f} | (cd $(mktemp -d) && terraform console) "
             "| tr -d '\"\\n'")

# 1 Terraform: tag-only LYR marker + base64decode("..") around the LYR material (gz_b64_rev_hex)
p = plan("terraform_hcl", "launcher", "gz_b64_rev_hex", "5e1c09aa")
inner = b64(gzip.compress(p.encode(), mtime=0))[::-1].encode().hex()
f = "tests/data/script_fixtures/dcall_tf_lyr_marker.tf"
case("dcall_tf_lyr_marker", "tf",
     '# HUNTRESS_ANALYSIS_V1:LYR-gz_b64_rev_hex\nterraform {\n  required_version = ">= 1.0"\n}\n\nlocals {\n'
     f'  huntress_descriptor_5e1c09aa = base64decode("{b64(inner)}")\n}}\n\noutput "inert_analysis_5e1c09aa" {{\n'
     '  value = local.huntress_descriptor_5e1c09aa\n}\n', p,
     "python3 -I tests/data/script_fixtures/dcall_gen.py (stdlib gzip -> base64 -> reverse -> hexlify, wrapped in base64)",
     TF_ORACLE.format(f=f) + " | xxd -r -p | rev | base64 -d | gunzip")

# 2 Tcl: no marker, `set huntress_descriptor_x [binary decode base64 {..}]` around hex(rev(b64(gzip(plan))))
p = plan("tcl", "downloader", "gz_b64_rev_hex", "a07e33d1")
inner = b64(gzip.compress(p.encode(), mtime=0))[::-1].encode().hex()
f = "tests/data/script_fixtures/dcall_tcl_nomarker.tcl"
case("dcall_tcl_nomarker", "tcl",
     '#!/usr/bin/env tclsh\n# inert analysis fixture\n'
     f'set huntress_descriptor_a07e33d1 [binary decode base64 {{{b64(inner)}}}]\n'
     'proc build_plan_a07e33d1 {} {\n    global huntress_descriptor_a07e33d1\n'
     '    return [dict create descriptor $huntress_descriptor_a07e33d1]\n}\n', p,
     "python3 -I tests/data/script_fixtures/dcall_gen.py (stdlib gzip -> base64 -> reverse -> hexlify, wrapped in base64)",
     f"printf 'source {f}\\nputs $huntress_descriptor_a07e33d1\\n' | tclsh | xxd -r -p | rev | base64 -d | gunzip")

# 3 zsh: tag-only LYR marker + "$(print -r -- .. | base64 -d)" around the LYR material (b64_rot13_rev_b64)
p = plan("zsh", "staged_chain", "b64_rot13_rev_b64", "c4d2f871")
inner = b64(codecs.encode(b64(p), "rot13")[::-1])
f = "tests/data/script_fixtures/dcall_zsh_lyr_marker.zsh"
case("dcall_zsh_lyr_marker", "zsh",
     '#!/usr/bin/env zsh\n# HUNTRESS_ANALYSIS_V1:LYR-b64_rot13_rev_b64\nemulate -L zsh\n'
     f'huntress_descriptor_c4d2f871="$(print -r -- {b64(inner)} | base64 -d)"\n'
     'build_plan_c4d2f871() { print -r -- "descriptor=${huntress_descriptor_c4d2f871}" }\n', p,
     "python3 -I tests/data/script_fixtures/dcall_gen.py (stdlib base64 -> rot13 -> reverse -> base64, wrapped in base64)",
     f"grep -oE 'print -r -- [A-Za-z0-9+/=]+' {f} | cut -d' ' -f4 | base64 -d | base64 -d | rev "
     "| tr 'A-Za-z' 'N-ZA-Mn-za-m' | base64 -d")

# 4 Kotlin: full B64 marker (plan A) AND a decode-call descriptor holding a different plan B -> the marker plan wins
p = plan("kotlin", "launcher", "base64", "9d0b6e12")
other = plan("kotlin", "benign_utility", "base64", "00000000")
f = "tests/data/script_fixtures/dcall_kts_marker_wins.kts"
case("dcall_kts_marker_wins", "kts",
     f'// HUNTRESS_ANALYSIS_V1:B64-{b64(p)}\nimport java.util.Base64\n\n'
     f'val huntress_descriptor_9d0b6e12 = String(Base64.getDecoder().decode("{b64(b64(other))}"))\n\n'
     'fun buildPlan_9d0b6e12() = mapOf("descriptor" to huntress_descriptor_9d0b6e12)\n', p,
     "python3 -I tests/data/script_fixtures/dcall_gen.py (stdlib base64 marker; descriptor = base64(base64(other plan)))",
     f"head -1 {f} | sed 's/.*:B64-//' | base64 -d", note="marker plan must be the FIRST find_codecs plain")

# 5 HCL jsondecode wrapper, no marker (JSON string escapes inside the HCL string), material = hex(plan)
p = plan("terraform_hcl", "uploader", "hex_json", "77ab21c0")
f = "tests/data/script_fixtures/dcall_hcl_jsondecode.tf"
esc = json.dumps(p.encode().hex()).replace('"', '\\"')
case("dcall_hcl_jsondecode", "tf",
     f'locals {{\n  huntress_descriptor_77ab21c0 = jsondecode("{esc}")\n}}\n', p,
     "python3 -I tests/data/script_fixtures/dcall_gen.py (stdlib hexlify, json.dumps, HCL-escaped)",
     f"sed -n 's/.*= \\(jsondecode(.*)\\)$/\\1/p' {f} | (cd $(mktemp -d) && terraform console) | tr -d '\"\\n' | xxd -r -p")

# 6 DECOY: base64decode around a TRUNCATED gzip stream (no complete plan anywhere)
p = plan("terraform_hcl", "launcher", "gz_b64", "deadbeef")
cut = b64(gzip.compress(p.encode(), mtime=0)[:-14])
f = "tests/data/script_fixtures/dcall_decoy_trunc_gzip.tf"
case("dcall_decoy_trunc_gzip", "tf",
     f'locals {{\n  huntress_descriptor_deadbeef = base64decode("{b64(cut)}")\n}}\n', None,
     "python3 -I tests/data/script_fixtures/dcall_gen.py (gzip stream cut 14 bytes short, base64, base64)",
     TF_ORACLE.format(f=f) + " | base64 -d | gunzip  # -> a cut-off prefix + unexpected end of file, no complete plan", decoy=True)

# 7 DECOY: decode call around a plan-shaped text whose version key is not `v=` (x=3) -> must not be accepted
p = plan("kotlin", "launcher", "base64", "feedface").replace("v=3|", "x=3|", 1)
f = "tests/data/script_fixtures/dcall_decoy_not_v.kts"
case("dcall_decoy_not_v", "kts",
     f'val huntress_descriptor_feedface = String(Base64.getDecoder().decode("{b64(b64(p))}"))\n', None,
     "python3 -I tests/data/script_fixtures/dcall_gen.py (stdlib base64 twice over an x=3 text)",
     f"grep -oE 'decode\\(\"[^\"]+' {f} | cut -d'\"' -f2 | base64 -d | base64 -d  # -> x=3|..., not a v= plan",
     decoy=True)

if __name__ == "__main__":
    for name, ext, src, plan_text, gen, oracle, decoy, note in CASES:
        (D / f"{name}.{ext}").write_text(src)
        fx = {"expected_plain": plan_text, "decoy": decoy, "target": "descriptor-decode-call-wrapper",
              "generator_cmd": gen, "oracle_cmd": oracle}
        if note:
            fx["note"] = note
        (D / f"{name}.json").write_text(json.dumps(fx, indent=1) + "\n")
        print(name)
