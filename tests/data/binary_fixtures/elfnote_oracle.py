"""Independent oracle for the elfnote_* fixtures: GNU readelf (-nW notes, -SW sections) + the raw file bytes.
Owners/types come from readelf's note listing (named types mapped back to their numbers), the HCFG desc offset is
the file position of readelf's printed "description data" bytes inside the note's section / segment range.
usage: python3 elfnote_oracle.py <file.bin> [owner ...]  -> expected_facts JSON on stdout"""
import json, re, subprocess, sys

NT = {"NT_GNU_ABI_TAG": 1, "NT_GNU_HWCAP": 2, "NT_GNU_BUILD_ID": 3, "NT_GNU_GOLD_VERSION": 4,
      "NT_GNU_PROPERTY_TYPE_0": 5, "NT_VERSION": 1, "NT_ARCH": 2, "NT_GO_BUILDID": 4}
path, owners = sys.argv[1], sys.argv[2:]
data = open(path, "rb").read()
r = subprocess.run(["readelf", "-nW", path], capture_output=True, text=True)
facts = {k: "none" for k in ("note_owners", "note_types", "note_count", "hcfg_note_offset", "hcfg_note_owner",
                             "hcfg_note_type", "hcfg_note_section", "has_hcfg_note")}
if r.returncode == 0 and "Not an ELF" not in r.stderr:
    secs = {}
    for ln in subprocess.run(["readelf", "-SW", path], capture_output=True, text=True).stdout.splitlines():
        m = re.match(r"\s*\[\s*\d+\]\s+(\S+)\s+\S+\s+[0-9a-f]+\s+([0-9a-f]+)\s+([0-9a-f]+)", ln)
        if m:
            secs[m.group(1)] = (int(m.group(2), 16), int(m.group(3), 16))
    notes, cur, rng = [], "none", None
    for ln in r.stdout.splitlines():
        m = re.match(r"Displaying notes found in: (\S+)", ln)
        if m:
            cur, rng = m.group(1), secs[m.group(1)]
        m = re.match(r"Displaying notes found at file offset 0x([0-9a-f]+) with length 0x([0-9a-f]+)", ln)
        if m:
            cur, rng = "none", (int(m.group(1), 16), int(m.group(2), 16))
        m = re.match(r"  (\S+)\s+0x([0-9a-f]+)\t(\S+)(?: [^:]*)?(?::\s*\(0x([0-9a-f]+)\))?(.*)", ln)
        if m and m.group(1) != "Owner":
            typ = int(m.group(4), 16) if m.group(4) else NT[m.group(3)]
            dm = re.search(r"description data: ((?:[0-9a-f]{2} ?)+)", ln, re.I)
            desc = bytes.fromhex(dm.group(1)) if dm else b""
            notes.append((m.group(1), typ, cur, desc, rng))
    facts.update(note_owners=[n[0] for n in notes], note_types=[n[1] for n in notes], note_count=str(len(notes)),
                 has_hcfg_note="false")
    for own, typ, sec, desc, (o, n) in notes:
        if desc[:4] == b"HCFG":
            facts.update(hcfg_note_offset=str(data.index(desc, o, o + n)), hcfg_note_owner=own,
                         hcfg_note_type=str(typ), hcfg_note_section=sec, has_hcfg_note="true")
            break
    for w in owners:
        facts[f"has_{w.lower()}_note"] = "true" if w in facts["note_owners"] else "false"
else:
    for w in owners:
        facts[f"has_{w.lower()}_note"] = "none"
print(json.dumps(facts))
