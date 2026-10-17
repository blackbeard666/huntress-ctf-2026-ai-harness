"""Write pair_arch_*.json from pair_arch_oracle.sh output (readelf -hW / od / unzip / sha256sum) + the generator's
tag -> member table (by construction in pair_arch_gen.sh). Does NOT import lib.binary. usage: python3 pair_arch_mkjson.py"""
import json, pathlib, subprocess
H = pathlib.Path(__file__).resolve().parent
F = ["machine", "machine_num", "bits", "endian", "elf_type", "entry_point"]
A64, X64 = "d17--variant-001-aarch64.elf", "d17--variant-000-x86_64.elf"
FIX = {   # fixture: (decoy, why, {tag: member basename}, extra {field: expected route (None = must not route)})
    "pair_arch_x86_64_aarch64": (False, "`x86_64` puts an underscore inside the qualifier (x86_64_machine): longest "
                                 "multi-token tag first; arm64/amd64 aliases fall back to e_machine 183/62",
                                 {"x86_64": X64, "aarch64": A64, "arm64": A64, "amd64": X64, "x64": X64}, {}),
    "pair_arch_riscv_arm_obj": (False, "clang-18 --target=riscv64/armv7 -c ET_REL members; `arm`/`armhf` aliases "
                                "route by e_machine 40, `riscv` by 243",
                                {"riscv64": "d17--variant-000-riscv64.o", "riscv": "d17--variant-000-riscv64.o",
                                 "armv7": "d17--variant-001-armv7.o", "arm": "d17--variant-001-armv7.o",
                                 "armhf": "d17--variant-001-armv7.o"}, {}),
    "pair_arch_renamed": (False, "no tag in the names: e_machine fallback (62 = x86_64, 183 = aarch64)",
                          {"x86_64": "d17--build-b.elf", "aarch64": "d17--build-a.elf", "arm64": "d17--build-a.elf"},
                          {"riscv64_machine": None}),
    "pair_arch_alias": (False, "names carry arm64/amd64: name match for those tags, e_machine for aarch64/x86_64",
                        {"arm64": "d17--variant-001-arm64.elf", "aarch64": "d17--variant-001-arm64.elf",
                         "amd64": "d17--variant-000-amd64.elf", "x86_64": "d17--variant-000-amd64.elf"}, {}),
    "pair_arch_decoy": (True, "arch-tagged names on a 40-byte truncated ELF and a text file: routed by name, every fact "
                        "\"none\"; alias/untagged fields do not route", {"x86_64": X64, "aarch64": A64},
                        {"arm64_machine": None, "machine": None, "riscv_machine": None}),
}
for stem, (decoy, why, tags, extra) in FIX.items():
    out = subprocess.run(["bash", str(H / "pair_arch_oracle.sh"), str(H / (stem + ".bin"))], capture_output=True,
                         text=True, check=True).stdout
    mem = [json.loads(l) for l in out.splitlines() if l.strip()]
    by = {m["member"].rsplit("/", 1)[-1]: m for m in mem}
    routes = {}
    for tag, base in tags.items():
        m = by[base]
        for f in F:
            routes[f"{tag}_{f}"] = {"member": base, "value": m.get(f, "none") if m["elf"] else "none"}
    routes.update(extra)
    j = {"format": "zip of a cross-arch same-source build pair", "members": [m["member"] for m in mem],
         "expected_sha256": [m["sha256"] for m in mem], "routes": routes,
         "generator_cmd": "bash pair_arch_gen.sh   # gcc / aarch64-linux-gnu-gcc-15 -O2, clang-18 --target=riscv64,armv7 -c, zip -X -j",
         "oracle_cmd": f"bash pair_arch_oracle.sh {stem}.bin   # unzip -Z1 + sha256sum, readelf -hW, od -tu2 -j18 (e_machine)",
         "decoy": decoy}
    j["note" if not decoy else "decoy_why"] = why
    (H / (stem + ".json")).write_text(json.dumps(j, indent=1) + "\n")
    print(stem, len(routes))
