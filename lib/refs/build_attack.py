#!/usr/bin/env python3
"""Build lib/refs/attack_data.json from the official MITRE ATT&CK Enterprise STIX bundle.

Source (authoritative, machine-readable):
  https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json

Usage:
  curl -fsSL -o /tmp/enterprise-attack.json <url above>
  python3 lib/refs/build_attack.py /tmp/enterprise-attack.json

Output: lib/refs/attack_data.json — {"T1105": {"name","tactics":[...],"desc","deprecated"}, ...}
Public reference data ONLY (a candidate generator); never a substitute for GM-verified values.
"""
import json
import re
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent / "attack_data.json"


def build(stix_path):
    bundle = json.loads(Path(stix_path).read_text())
    out = {}
    for obj in bundle.get("objects", []):
        if obj.get("type") != "attack-pattern":
            continue
        ext = next((r for r in obj.get("external_references", [])
                    if r.get("source_name") == "mitre-attack" and r.get("external_id")), None)
        if not ext:
            continue
        tid = ext["external_id"]  # Txxxx or Txxxx.yyy
        if not re.fullmatch(r"T\d{4}(\.\d{3})?", tid):
            continue
        tactics = sorted({p.get("phase_name") for p in obj.get("kill_chain_phases", [])
                          if p.get("kill_chain_name") == "mitre-attack" and p.get("phase_name")})
        desc = (obj.get("description") or "").strip().split("\n")[0][:300]
        out[tid] = {
            "name": obj.get("name", ""),
            "tactics": tactics,
            "desc": desc,
            "deprecated": bool(obj.get("x_mitre_deprecated") or obj.get("revoked")),
        }
    OUT.write_text(json.dumps(out, indent=0, sort_keys=True))
    techs = [k for k in out if "." not in k]
    subs = [k for k in out if "." in k]
    print(f"wrote {OUT} — {len(out)} ids ({len(techs)} techniques, {len(subs)} sub-techniques), "
          f"{sum(1 for v in out.values() if v['deprecated'])} deprecated/revoked")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: build_attack.py <enterprise-attack.json>")
    build(sys.argv[1])
