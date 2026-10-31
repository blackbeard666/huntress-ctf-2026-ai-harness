"""Emit the cross-group-campaign-correlation fixture JSONs; `expected` comes from cs_oracle.py (independent reader)."""
import json, subprocess, sys
O = json.loads(subprocess.check_output([sys.executable, "cs_oracle.py", "cs_evidence.zip"]))
INT = {"kind": "integer", "syntax": "base-10 integer with no units, separators, whitespace, or explanatory text"}
HEX64 = {"kind": "pattern", "syntax": "exactly 64 lowercase hexadecimal characters; no prefix, whitespace, or explanatory text"}
TXT = {"kind": "text", "syntax": "exact text"}
U = "In evidence.zip, Use every group d01-- through d05-- in ZIP central-directory order. "
GEN = "python3 cs_gen.py cs_evidence.zip cs_decoy_oneday.zip"
ORA = "python3 cs_oracle.py cs_evidence.zip  # key: "
cases = [
    ("cs_evidence.zip", "capstone_distinct_campaign_count", U + "For each group take the consensus decoded HCFG/HGRF "
     "config (the value most of its members agree on) and count the distinct config.campaign values across all groups. "
     "Submit the count in base 10.", INT, str(O["distinct_campaign_count"]), "distinct_campaign_count"),
    ("cs_evidence.zip", "capstone_member_distinct_campaign_count", U + "Decode every member's own config and count the "
     "distinct config.campaign values per member, across all members. Submit the count in base 10.", INT,
     str(O["distinct_member_campaign_count"]), "distinct_member_campaign_count"),
    ("cs_evidence.zip", "capstone_campaigns_sha256", U + "Take each group's consensus config.campaign, sort the values "
     "in ascending code-unit order, join them with one LF byte and no trailing LF, then compute SHA-256.", HEX64,
     O["sorted_lf_sha256"], "sorted_lf_sha256"),
    ("cs_evidence.zip", "capstone_campaign_order_sha256", U + "Take each group's consensus config.campaign in day order "
     "(d01 first), join them with ASCII colon characters, then compute SHA-256.", HEX64, O["ordered_colon_sha256"],
     "ordered_colon_sha256"),
    ("cs_evidence.zip", "capstone_configless_member_count", U + "Count the members that carry no decodable config "
     "record (role members such as a loader). Submit the count in base 10.", INT, str(O["configless_count"]),
     "configless_count"),
    ("cs_evidence.zip", "capstone_shared_campaign_group_count", U + "Count the groups whose consensus config.campaign "
     "is shared with at least one other group. Submit the count in base 10.", INT, str(len(O["shared_groups"])),
     "shared_groups (length)"),
    ("cs_evidence.zip", "capstone_elf_member_count", U + "Classify every member by magic and parsed container format and "
     "count the members whose format is elf. Submit the count in base 10.", INT, str(O["elf_count"]), "elf_count"),
    ("cs_decoy_oneday.zip", "capstone_distinct_campaign_count", U + "For each group take the consensus decoded config "
     "and count the distinct config.campaign values across all groups. Submit the count in base 10.", INT, None,
     "decoy: the archive holds ONE day group (no cross-group set) -> must stay None"),
]
for member, field, q, af, exp, key in cases:
    d = {"kind": "generic_field", "member": member, "field": field, "question": q, "answer_format": af,
         "expected": exp, "generator_cmd": GEN, "oracle_cmd": ORA + key}
    if exp is None:
        d["decoy"] = True
    json.dump(d, open(f"{member.rsplit('.', 1)[0]}.{field}.json", "w"), indent=1)
    print(field, exp)
