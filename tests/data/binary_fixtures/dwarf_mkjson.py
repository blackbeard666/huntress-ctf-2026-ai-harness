"""Writes dwarf_<name>.json from the llvm-dwarfdump oracle (dwarf_oracle.py) + spot lookups derived from it.
usage: python3 dwarf_mkjson.py   (after bash dwarf_gen.sh)"""
import json, pathlib, subprocess, sys
here = pathlib.Path(__file__).parent
for b in sorted(here.glob("dwarf_*.bin")):
    facts = json.loads(subprocess.run([sys.executable, str(here / "dwarf_oracle.py"), str(b)], capture_output=True,
                                      text=True, check=True).stdout)
    decoy = facts["has_dwarf"] != "true"
    if not decoy:   # per-entity lookups, values copied from the oracle's own tables
        fn = facts["functions"][0]
        facts.update({f"low_pc:{fn['name']}": fn["low_pc"], f"high_pc:{fn['name']}": fn["high_pc"],
                      f"size:{fn['name']}": str(fn["size"]), "fields:beacon_config": facts["struct_fields"]["beacon_config"],
                      "params:beacon_send": facts["params"]["beacon_send"], "locals:main": facts["locals"]["main"],
                      "fields:nosuch_struct": "none", "low_pc:nosuch_fn": "none"})
    else:
        facts.update({"low_pc:main": "none", "fields:beacon_config": "none"})
    j = {"family": "dwarf", "encoding": "none", "expected_offset": None, "expected_config": None,
         "expected_facts": facts, "decoy": decoy,
         "file_b": subprocess.run(["file", "-b", str(b)], capture_output=True, text=True).stdout.strip(),
         "generator_cmd": "bash dwarf_gen.sh   # gcc 15.2 -g -gdwarf-4 / -gdwarf-5 + objcopy --compress-debug-sections=zstd;"
                          " clang-18 -g (DWARF5 strx/addrx) + objcopy --compress-debug-sections=zlib-gnu (.zdebug_*);"
                          " strip --strip-debug decoy; printf text decoy",
         "oracle_cmd": f"python3 dwarf_mkjson.py -> python3 dwarf_oracle.py {b.name}   # objcopy --decompress-debug-sections"
                       " + llvm-dwarfdump-18 --debug-info / --debug-line text parse",
         "note": "lib.binary.dwarf_field(data, key) per expected_facts key; key vocabulary SPECULATIVE (no GM label seen)"}
    b.with_suffix(".json").write_text(json.dumps(j, indent=1) + "\n")
    print(b.stem, "decoy" if decoy else "ok")
