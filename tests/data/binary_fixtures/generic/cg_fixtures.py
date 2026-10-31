#!/usr/bin/env python3
"""Writes the campaign-graph-record-facts fixture jsons; every `expected` comes from cg_oracle.sh (python crc check +
jq), never from lib.binary."""
import hashlib, json, os, subprocess

here = os.path.dirname(os.path.abspath(__file__))
GEN = "python3 cg_gen.py  # d30 members copied from the GM evidence; ELFs: gcc + stdlib struct/zlib record writer"
TXT = {"kind": "exact_text", "syntax": "exact case-sensitive artifact-derived text only; no quotes or explanatory text"}
INT = {"kind": "integer", "syntax": "base-10 integer with no units, separators, whitespace, or explanatory text"}
HEX = {"kind": "pattern", "syntax": "exactly 64 lowercase hexadecimal characters; no prefix, whitespace, or explanatory text"}
LAY = ("Locate the unique CRC32-valid {m} record by scanning backward from the end of the member. Its byte-4 version, "
       "byte-5 XOR key, little-endian length and CRC32 fields, XOR decoding, and UTF-8 JSON payload use the same "
       "12-byte layout as HCFG. ")


def oracle(member, magic, jq):
    out = subprocess.run([os.path.join(here, "cg_oracle.sh"), member, magic, jq], cwd=here, capture_output=True,
                         text=True, check=True).stdout
    return out[:-1] if out.endswith("\n") else out


def emit(member, field, question, af, magic, jq, sha=False, decoy=False):
    v = oracle(member, magic, jq)
    cmd = f"./cg_oracle.sh {member} {magic} '{jq}'"
    if sha:
        v = hashlib.sha256(v.encode()).hexdigest()
        cmd += " | head -c -1 | sha256sum"
    d = {"kind": "generic_field", "member": member, "field": field, "question": question, "answer_format": af,
         "expected": (v if v not in ("", "null") else None), "generator_cmd": GEN, "oracle_cmd": cmd}
    if decoy:
        d["decoy"] = True
    json.dump(d, open(os.path.join(here, f"{member}.{field}.json"), "w"), indent=1, ensure_ascii=False)
    print(member, field, repr(d["expected"]))


H = LAY.format(m="HGRF")
CS = "In evidence.zip, Use the unique d30-- member whose basename ends config.n. "
for key in ("campaign", "mutex", "url"):   # the GM's own D30 wording (config_capsule_graph_config_*)
    emit("cg_d30_config.n", f"config_capsule_graph_config_{key}",
         CS + H + f"Submit the exact JSON string at config.n decoded HGRF JSON property graph.config.{key}, without "
         "JSON quotes.", TXT, "HGRF", f".config.{key}")
LD = ("In evidence.zip, Use loader.n's decoded HGRF graph.config object after confirming all three canonical campaign "
      "graphs match when this_role is omitted. ")
emit("cg_d30_loader.n", "config_domain", LD + H + "Submit the exact JSON string at loader.n decoded HGRF JSON property "
     "graph.config.domain, without JSON quotes.", TXT, "HGRF", ".config.domain")
emit("cg_d30_loader.n", "graph_node_count", "In evidence.zip, Use the unique d30-- member whose basename ends loader.n. "
     + H + "Count the entries of the decoded HGRF graph nodes array. Submit the count in base 10.", INT, "HGRF",
     ".nodes|length")
emit("cg_d30_library.n", "library_this_role", "In evidence.zip, Use the unique d30-- member whose basename ends "
     "library.n. " + H + "Submit the exact JSON string at library.n decoded HGRF JSON property graph.this_role, "
     "without JSON quotes.", TXT, "HGRF", ".this_role")
emit("cg_d30_loader.n", "graph_edges_sha256", "In evidence.zip, Use the unique d30-- member whose basename ends "
     "loader.n. " + H + "Collect the decoded HGRF graph edges strings, sort them by ascending code-unit order, join "
     "with one LF byte and no trailing LF, then SHA-256 those UTF-8 bytes.", HEX, "HGRF", '.edges|sort|join("\\n")',
     sha=True)
emit("cg_d30_library.n", "load_order", "In evidence.zip, Use the unique d30-- member whose basename ends library.n. "
     + H + "Submit the decoded HGRF graph load_order entries in stored order, joined with ASCII comma characters and "
     "no spaces.", TXT, "HGRF", '.load_order|join(",")')
G = LAY.format(m="GRPH")
U = "In evidence.zip, Use the unique d31-- member whose basename ends .elf. "
emit("cg_synth.elf", "graph_edge_count", U + G + "Count the entries of the decoded GRPH graph edges array. Submit the "
     "count in base 10.", INT, "GRPH", ".edges|length")
emit("cg_synth.elf", "graph_node_count", U + "The member ends with a crc32-validated campaign-graph record (12-byte "
     "HCFG layout, unnamed magic). Count the decoded graph nodes. Submit the count in base 10.", INT, "GRPH",
     ".nodes|length")
emit("cg_synth.elf", "graph_edges_sha256", U + G + "Collect the decoded GRPH graph edges strings, sort them by "
     "ascending code-unit order, join with one LF byte and no trailing LF, then SHA-256 those UTF-8 bytes.", HEX,
     "GRPH", '.edges|sort|join("\\n")', sha=True)
emit("cg_synth.elf", "load_order", U + G + "Submit the decoded GRPH graph load_order entries in stored order, joined "
     "with ASCII comma characters and no spaces.", TXT, "GRPH", '.load_order|join(",")')
emit("cg_synth.elf", "graph_leaves", U + G + "Submit the graph's unique leaf node: the node that is the source of no "
     "edge.", TXT, "GRPH", '[.nodes[] as $n | select([.edges[] | split("->")[0]] | index($n) | not) | $n] | .[0]')
emit("cg_synth.elf", "config_graph_config_domain", U + G + "Submit the exact JSON string at the decoded GRPH JSON "
     "property record.config.domain, without JSON quotes.", TXT, "GRPH", ".config.domain")
emit("cg_decoy_badcrc.elf", "graph_node_count", U + G + "Count the entries of the decoded GRPH graph nodes array. "
     "Submit the count in base 10.", INT, "GRPH", ".nodes|length", decoy=True)
emit("cg_decoy_badcrc.elf", "config_graph_config_domain", U + G + "Submit the exact JSON string at the decoded GRPH "
     "JSON property record.config.domain, without JSON quotes.", TXT, "GRPH", ".config.domain", decoy=True)
