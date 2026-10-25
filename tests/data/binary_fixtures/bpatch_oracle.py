"""Independent oracle for bpatch_* fixtures (never lib.binary): apply with bsdiff4.patch / python-ips `ips.apply`
(tools/pypatch), BPS/UPS targets = the gcc B build (no third-party BPS/UPS reader; crc32 footers checked with zlib),
changed bytes = `cmp -l`, sections = `readelf -SW`, functions = `nm -S --defined-only`.
usage (from this dir): PYTHONPATH=../../../tools/pypatch python3 bpatch_oracle.py   # writes bpatch_*.json"""
import hashlib, json, os, shutil, struct, subprocess, sys, tempfile, zlib
import bsdiff4, ips

A = open("bpatch_base.bin", "rb").read()
B = open("bpatch_target_flip.elf", "rb").read()
tmp = tempfile.mkdtemp()

def write(p, b):
    open(p, "wb").write(b); return p

def facts(fmt, t):
    pa, pt = write(f"{tmp}/a", A), write(f"{tmp}/t", t)
    f = {"patch_format": fmt, "target_size": str(len(t)), "target_sha256": hashlib.sha256(t).hexdigest()}
    if len(t) == len(A):
        diff = [int(l.split()[0]) - 1 for l in subprocess.run(["cmp", "-l", pa, pt], capture_output=True, text=True).stdout.split("\n") if l.strip()]
        f["changed_byte_count"] = str(len(diff))
        secs = []
        for l in subprocess.run(["readelf", "-SW", pt], capture_output=True, text=True).stdout.splitlines():
            l = l.replace("[ ", "[").split()
            if len(l) > 6 and l[0].startswith("[") and l[1].startswith(".") and l[2] != "NOBITS":
                secs.append((l[1], int(l[4], 16), int(l[5], 16), int(l[3], 16)))
        sn, va = [], []
        for o in diff:
            for nm, so, sz, sa in secs:
                if so <= o < so + sz:
                    sn.append(nm) if nm not in sn else None
                    if sa: va.append(sa + o - so)
        f["changed_sections"] = json.dumps(sn, separators=(",", ":"))
        fn = []
        for l in subprocess.run(["nm", "-S", "--defined-only", pt], capture_output=True, text=True).stdout.splitlines():
            p = l.split()
            if len(p) == 4 and p[2] in "Tt" and any(int(p[0], 16) <= v < int(p[0], 16) + int(p[1], 16) for v in va):
                fn.append(p[3])
        f["changed_symbol"] = fn[0] if len(fn) == 1 else "?"
    return f

def crc(p, t):
    s, tc, c = struct.unpack("<III", p[-12:])
    return str(zlib.crc32(A) == s and zlib.crc32(t) == tc and zlib.crc32(p[:-4]) == c).lower()

cases = {}
for nm in ("bpatch_bsdiff_flip", "bpatch_bsdiff_grow"):
    cases[nm] = (facts("bsdiff40", bsdiff4.patch(A, open(nm + ".bin", "rb").read())), "bsdiff4.diff(A, B) (pip bsdiff4, C ext)", "bsdiff4.patch(A, patch)")
for nm in ("bpatch_ips_flip", "bpatch_ips_rle"):
    t = shutil.copy("bpatch_base.bin", f"{tmp}/ipsbase"); ips.apply(nm + ".bin", t)
    f = facts("ips", open(t, "rb").read()); cases[nm] = (f, "stdlib IPS writer in bpatch_gen.sh (RLE for runs >= 4 equal bytes)", "python-ips ips.apply(patch, copy_of_base)")
for nm, fmt in (("bpatch_bps_flip", "bps"), ("bpatch_ups_flip", "ups"), ("bpatch_bps_badcrc", "bps")):
    p = open(nm + ".bin", "rb").read(); f = facts(fmt, B)
    f["crc_valid"] = crc(p, B)
    cases[nm] = (f, f"stdlib {fmt.upper()} writer in bpatch_gen.sh" + (" + one target-crc bit flipped" if "bad" in nm else ""), "target = gcc B build (bpatch_target_flip.elf); crc32 footer via zlib")
for k, (f, g, o) in cases.items():
    if "flip" in k or "badcrc" in k:
        assert f["target_sha256"] == hashlib.sha256(B).hexdigest(), k
    if "changed_symbol" in f and f["changed_symbol"] == "?":
        del f["changed_symbol"]
    json.dump({"family": "binary_patch_file", "encoding": "none", "expected_offset": None, "expected_config": None,
               "base": "bpatch_base.bin", "expected_facts": f, "generator_cmd": "bash bpatch_gen.sh   # " + g,
               "oracle_cmd": "PYTHONPATH=../../../tools/pypatch python3 bpatch_oracle.py   # " + o + "; cmp -l / readelf -SW / nm -S",
               "decoy": False}, open(k + ".json", "w"), indent=1)
for k, why in (("bpatch_decoy_magic", "IPS body behind a 'PATCX' magic (renamed impostor)"),
               ("bpatch_decoy_trunc", "bsdiff40 cut in half: bz2 stream truncated (bsdiff4.patch raises)")):
    p = open(k + ".bin", "rb").read()
    try:
        bsdiff4.patch(A, p); raise SystemExit(k + " applied?!")
    except SystemExit: raise
    except Exception: pass
    json.dump({"family": "binary_patch_file", "encoding": "none", "expected_offset": None, "expected_config": None,
               "base": "bpatch_base.bin", "expected_facts": {"patch_format": "none", "target_sha256": "none"},
               "generator_cmd": "bash bpatch_gen.sh   # " + why, "oracle_cmd": "PYTHONPATH=../../../tools/pypatch python3 bpatch_oracle.py   # bsdiff4.patch rejects it; magic not BSDIFF40/PATCH/BPS1/UPS1",
               "decoy": True}, open(k + ".json", "w"), indent=1)
print("\n".join(sorted(cases)))
