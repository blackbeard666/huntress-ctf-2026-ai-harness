"""Offline oracle for aotimg_* fixtures -> writes each .json. Independent of lib.binary: runtime/sections from
`readelf -SW` / `nm` / `nm -D` / `readelf -d`, HCFG offset from `grep -obUa`, config decoded with stdlib only.
usage: python3 -I aotimg_oracle.py   (from this directory, after aotimg_gen.sh)"""
import base64, json, re, struct, subprocess, zlib, pathlib

here = pathlib.Path(__file__).resolve().parent
sh = lambda c: subprocess.run(c, shell=True, capture_output=True, text=True, cwd=here).stdout
META = {"graal_heap_raw": ("raw", False, "step 1: gcc -no-pie, .svm_heap byte[] + raw blob, __svm_* / IsolateEnterStub_ syms"),
        "graal_heap_b64": ("base64", False, "step 2: gcc PIE, .svm_heap Latin-1 String with base64 blob"),
        "julia_sysimg": ("raw", False, "step 3: gcc -shared sys.so exporting jl_system_image_data (.rodata) + raw blob"),
        "julia_app": ("none", False, "step 4: launcher NEEDing libjulia.so.1 (jl_init_with_image), no blob"),
        "decoy_strings": ("none", True, "step 5: plain C, every cue only a .rodata string literal, decoy blob in .rodata"),
        "decoy_trunc": ("none", True, "step 6: head -c 4096 of step 1 (no section table)")}
for stem, (enc, decoy, note) in META.items():
    f = f"aotimg_{stem}.bin"
    secs = [(m[0], int(m[1], 16), int(m[2], 16)) for m in
            re.findall(r"\]\s+(\S+)\s+\S+\s+[0-9a-f]+\s+([0-9a-f]+)\s+([0-9a-f]+)", sh(f"readelf -SW {f} 2>/dev/null"))]
    syms = set(sh(f"nm {f} 2>/dev/null; nm -D {f} 2>/dev/null").split())
    needed = re.findall(r"\(NEEDED\).*\[(.+)\]", sh(f"readelf -d {f} 2>/dev/null"))
    graal = any(n == ".svm_heap" for n, _, _ in secs) or any(s.startswith(("__svm_", "IsolateEnterStub_")) for s in syms)
    julia = any(s.startswith("jl_") for s in syms) or any(n.startswith("libjulia") for n in needed)
    rt = "graalvm" if graal else "julia" if julia else "none"
    exp = {"runtime": rt, "has_graalvm": str(graal).lower(), "has_julia": str(julia).lower()}
    if rt != "none":
        heap = ".svm_heap" if graal else None
        if julia and "jl_system_image_data" in syms:   # section of the symbol: nm address -> readelf -S row by addr
            addr = int(sh(f"nm -D {f} | grep ' jl_system_image_data$'").split()[0], 16)
            heap = next(m[0] for m in re.findall(r"\]\s+(\S+)\s+\S+\s+([0-9a-f]+)\s+[0-9a-f]+\s+([0-9a-f]+)",
                                                 sh(f"readelf -SW {f}")) if int(m[1], 16) <= addr < int(m[1], 16) + int(m[2], 16))
        exp["image_section"] = heap or "none"
        pat = "HCFG" if enc == "raw" else "SENGR"   # base64('HCFG\x01') starts 'SENGRw' -> grep its first 5 chars
        g = sh(f"grep -obUa {pat} {f}").split(":")[0] if enc != "none" else ""
        if g:
            off = int(g)
            b = here.joinpath(f).read_bytes()
            blob = b[off:off + 4096] if enc == "raw" else base64.b64decode(re.match(rb"[A-Za-z0-9+/=]+", b[off:]).group())
            ver, key, n, crc = struct.unpack_from("<BBHI", blob, 4)
            plain = bytes(c ^ key for c in blob[12:12 + n])
            assert zlib.crc32(plain) == crc
            exp.update(hcfg_offset=str(off), hcfg_encoding=enc, hcfg_config=json.dumps(json.loads(plain), separators=(",", ":")),
                       hcfg_section=next(n for n, o, s in secs if o <= off < o + s))
        else:
            exp.update(hcfg_offset="none", hcfg_section="none")
        v = re.search(r"GraalVM (\d+(?:\.\d+)+\+[\d.]+)|Julia Version (\d+\.\d+\.\d+)", sh(f"strings -a {f}"))
        exp["graalvm_version" if graal else "julia_version"] = (v.group(1) or v.group(2)) if v else "none"
    else:
        exp.update(image_section="none", hcfg_section="none", hcfg_offset="none")
    here.joinpath(f"aotimg_{stem}.json").write_text(json.dumps({
        "encoding": enc, "expected_offset": int(exp["hcfg_offset"]) if exp.get("hcfg_offset", "none") != "none" else None,
        "expected_config": json.loads(exp["hcfg_config"]) if "hcfg_config" in exp else None, "expected_facts": exp,
        "generator_cmd": f"bash aotimg_gen.sh   # {note.split(':')[0]} (gcc {sh('gcc -dumpversion').strip()}; blob by python3 stdlib struct/zlib/base64)",
        "oracle_cmd": "python3 -I aotimg_oracle.py   # readelf -SW / nm / nm -D / readelf -d / grep -obUa / strings -a + stdlib xor-crc decode",
        "decoy": decoy, "note": note}, indent=1) + "\n")
    print(stem, exp)
