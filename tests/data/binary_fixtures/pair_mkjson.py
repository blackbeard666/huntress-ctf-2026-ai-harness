"""Write pair_*.json from pair_oracle.sh output (readelf/unzip/sha256sum/upx -t) + the generator's tag -> member
table (by construction in pair_gen.sh). Does NOT import lib.binary. usage: python3 pair_mkjson.py"""
import json, pathlib, subprocess
H = pathlib.Path(__file__).resolve().parent
F = ["elf_type", "entry_point", "has_symtab", "section_names", "imports", "has_interp", "has_debug_info", "is_packed",
     "needed"]
FIX = {   # fixture: (decoy, why, {tag: member basename}, extra {field: expected route (None = must not route)})
    "pair_opt_o0_o2": (False, "", {"o0": "d17--variant-000-O0.elf", "o2": "d17--variant-001-O2.elf"}, {}),
    "pair_pie_nopie": (False, "`pie` must not match the `no-pie` member; `no_pie` == name tokens no,pie",
                       {"pie": "d17--variant-000-pie.elf", "no_pie": "d17--variant-001-no-pie.elf",
                        "nopie": "d17--variant-001-no-pie.elf"}, {}),
    "pair_debug_stripped": (False, "CD order (stripped first) differs from variant numbering",
                            {"debug": "d17--variant-000-debug.elf", "stripped": "d17--variant-001-stripped.elf"}, {}),
    "pair_static_dynamic": (False, "", {"static": "d17--variant-000-static.elf",
                                        "dynamic": "d17--variant-001-dynamic.elf"}, {}),
    "pair_packed_unpacked": (False, "`packed` must not match `unpacked`; UPX member has no section headers",
                             {"packed": "d17--variant-000-packed.elf", "unpacked": "d17--variant-001-unpacked.elf"}, {}),
    "pair_renamed_pie": (False, "no tag in the names: structural fallback (ET_DYN+INTERP = pie, ET_EXEC = nopie)",
                         {"pie": "d17--variant-001.elf", "nopie": "d17--variant-000.elf"}, {}),
    "pair_renamed_opt": (False, "no tag in the names: structural fallback (larger code = O0, smaller = O2/Os)",
                         {"o0": "d17--build-b.elf", "o2": "d17--build-a.elf", "os": "d17--build-a.elf"}, {}),
    "pair_decoy": (True, "tagged names but a 40-byte truncated ELF and a text file: routed, every fact \"none\"; "
                   "untagged fields do not route", {"pie": "d17--variant-000-pie.elf",
                                                   "no_pie": "d17--variant-001-no-pie.elf"},
                   {"entry_point": None, "config_domain": None, "elf_type": None, "has_symtab": None}),
}
for stem, (decoy, why, tags, extra) in FIX.items():
    out = subprocess.run(["bash", str(H / "pair_oracle.sh"), str(H / (stem + ".bin"))], capture_output=True,
                         text=True, check=True).stdout
    mem = [json.loads(l) for l in out.splitlines() if l.strip()]
    by = {m["member"].rsplit("/", 1)[-1]: m for m in mem}
    routes = {}
    for tag, base in tags.items():
        m = by[base]
        for f in F:
            routes[f"{tag}_{f}"] = {"member": base, "value": m.get(f, "none") if m["elf"] else "none"}
    routes.update(extra)
    j = {"format": "zip of a same-source build pair", "members": [m["member"] for m in mem],
         "expected_sha256": [m["sha256"] for m in mem], "routes": routes,
         "generator_cmd": "bash pair_gen.sh   # gcc -O0/-O2/-Os/-static -nostdlib/-pie/-no-pie/-g, strip, upx -9, zip -X -j",
         "oracle_cmd": f"bash pair_oracle.sh {stem}.bin   # unzip -Z1 + sha256sum, readelf -hW/-SW/-lW/--dyn-syms/-dW, upx -t",
         "decoy": decoy}
    if why:
        j["note" if not decoy else "decoy_why"] = why
    (H / (stem + ".json")).write_text(json.dumps(j, indent=1) + "\n")
    print(stem, len(routes))
