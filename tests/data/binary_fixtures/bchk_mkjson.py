"""bchk_mkjson.py: write bchk_<pair>.json expected facts from bchk_oracle.py (objdump/readelf) output -- never lib."""
import json, re, subprocess, sys
PAIRS = {"c_manual": "gcc -O2 table[i] vs if (i < 16)", "ubsan": "gcc -O2 vs gcc -O2 -fsanitize=bounds",
         "fortify": "gcc -O2 _FORTIFY_SOURCE=0 vs =2 (memcpy -> __memcpy_chk)",
         "rust": "rustc -O get_unchecked(i) vs v[i] (panic_bounds_check)", "go": "go build -gcflags='-B -l' vs '-l'",
         "go_index": "gcc asm-label runtime.panicIndex guard (synthetic Go-shaped)",
         "rust_slice": "gcc asm-label core::slice::index::slice_end_index_len_fail guard (synthetic Rust-shaped)",
         "decoy_same": "identical twins (decoy)", "decoy_text": "non-ELF impostor (decoy)"}
for p, gen in PAIRS.items():
    a, b = f"bchk_{p}_a.bin", f"bchk_{p}_b.bin"
    o = json.loads(subprocess.run(["python3", "bchk_oracle.py", a, b], capture_output=True, text=True).stdout or "null")
    if o is None or open(a, "rb").read(4) != b"\x7fELF":
        exp = {"bounds_check_facts": None}
    else:
        hit = [v for v in o.values() if v["bounds_check_twin"] != "none"]
        if not hit:
            exp = {"bounds_check_twin": "none", "bounds_check_added": "false", "bounds_check_function": "none",
                   "bounds_check_kind": "none"}
        else:
            exp = dict(hit[0])
            dm = exp.pop("bounds_check_function_demangled")
            dem = subprocess.run(["nm", "-C", a], capture_output=True, text=True).stdout.split("\n")
            rawl = subprocess.run(["nm", a], capture_output=True, text=True).stdout.split("\n")
            exp["bounds_check_function"] = next((r.split()[-1] for r, d in zip(rawl, dem) if d.split(" ", 2)[-1] == dm), dm)
            exp["bounds_check_added"] = str(exp["bounds_check_twin"] == "b").lower()
    j = {"family": "bounds_check_facts", "encoding": "none", "expected_offset": None, "expected_config": None,
         "file_a": a, "file_b": b, "expected_facts": exp,
         "generator_cmd": f"bash bchk_gen.sh OUT   # {gen}",
         "oracle_cmd": f"python3 bchk_oracle.py {a} {b}   # binutils objdump -d -C -M intel + readelf -sW + nm",
         "decoy": p.startswith("decoy"),
         "note": "lib.binary.bounds_check_field(a, b, key); bounds_check_kind vocabulary SPECULATIVE (no GM label yet)"}
    json.dump(j, open(f"bchk_{p}.json", "w"), indent=1)
    print(p, json.dumps(exp))
