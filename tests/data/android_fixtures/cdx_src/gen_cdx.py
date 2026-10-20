#!/usr/bin/env python3
"""Generate the cdx_* fixtures (coverage atlas row 86: the answer string lives in a compact / optimised dex payload --
CompactDex `cdex001`, a vdex wrapping dex / cdex, an OAT ELF exporting `oatdata` -- that androguard and the classes*.dex
scans do not read). The string pool always comes from a real dex: javac --release 8 + dex2jar d2j-jar2dex compile a
class whose static String is the ENCODED answer (base64 / base32 / hex via coreutils), so no literal ANS- is in any
byte. The containers are written with struct (stdlib writer) from the public ART layouts:
  vdex006   : "vdex" "006\\0" n dex_size deps_size quick_size, checksums[n], dex          (lief.VDEX reads this)
  cdex      : dex header with magic cdex001 + 6 CompactDex u4s (0x88 B), ids/data shifted; string_data_off relative to
              data_off (string-pool-faithful: map_list / code items are not re-encoded)
  vdex019   : "vdex" "019\\0" "002\\0" n deps bcp clc, checksums[n], DexSectionHeader{dex_size, shared_size, quick},
              cdex main section (header + ids) then the shared data section; string_data_off relative to shared begin
  oat       : gcc -shared ELF whose .rodata exports `oatdata` = "oat\\n124\\0" header pad + the dex (.incbin)
usage: gen_cdx.py <vdex006_b64 | cdex_b32 | vdex019_hex | oat_b64 | decoy_vdex006_nearmiss> <out.apk>"""
import json, os, shutil, struct, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TOK = {"vdex006_b64": "ANS-3e8a17c0f94d2b65", "cdex_b32": "ANS-91b4d7e02c6af358", "vdex019_hex": "ANS-c05f2e9a8b13d746",
       "oat_b64": "ANS-6d2a90f1e7c43b58", "decoy_vdex006_nearmiss": "ANS-3e8a17c0f94d2b6"}[variant]
ENC = {"vdex006_b64": "base64 -w0", "cdex_b32": "base32 -w0", "vdex019_hex": "xxd -p -c0",
       "oat_b64": "base64 -w0", "decoy_vdex006_nearmiss": "base64 -w0"}[variant]
enc = subprocess.run(["sh", "-c", ENC], input=f"proof={TOK}".encode(), capture_output=True, check=True).stdout.decode().strip()

tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
src, cls = tmp / "src/com/huntress/mobile/d21/opt", tmp / "cls"
src.mkdir(parents=True)
cls.mkdir()
(src / "Blob.java").write_text("package com.huntress.mobile.d21.opt;\npublic final class Blob {\n"
                               f"  public static final String P = {json.dumps(enc)};\n"
                               "  public static String get() { return P; }\n}\n")
subprocess.run(["javac", "--release", "8", "-d", str(cls), str(src / "Blob.java")], check=True)
shutil.make_archive(str(tmp / "app"), "zip", cls)
subprocess.run([str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(tmp / "classes.dex"), str(tmp / "app.zip")],
               check=True, capture_output=True)
dex = (tmp / "classes.dex").read_bytes()
u32 = lambda b, o: struct.unpack_from("<I", b, o)[0]
n_str, o_str, d_off = u32(dex, 0x38), u32(dex, 0x3C), u32(dex, 0x6C)


def pad4(b):
    return b + bytes(-len(b) % 4)


def to_cdex(shared):
    """dex -> CompactDex: 0x88-byte header, everything after the header shifted by 0x18. shared=False: string_data_off
    relative to the cdex's own data_off; shared=True: main section = header + ids, data moved to a separate block."""
    sh = 0x18
    hdr = bytearray(dex[:0x70])
    hdr[:8] = b"cdex001\0"
    for o in (0x30, 0x34, 0x3C, 0x44, 0x4C, 0x54, 0x5C, 0x64, 0x6C):
        v = u32(hdr, o)
        if v:
            struct.pack_into("<I", hdr, o, v + sh)
    ids = bytearray(dex[0x70:d_off])
    for i in range(n_str):
        old = u32(dex, o_str + 4 * i)
        struct.pack_into("<I", ids, o_str - 0x70 + 4 * i, old - d_off if shared else old + sh - (d_off + sh))
    if shared:
        main = bytes(hdr) + bytes(0x18) + bytes(ids)
        main = bytearray(main)
        struct.pack_into("<I", main, 0x6C, 0)              # data_off: start of the shared section
        struct.pack_into("<I", main, 0x68, len(dex) - d_off)  # data_size
        struct.pack_into("<I", main, 0x20, len(main))       # file_size = main section only
        return bytes(main), dex[d_off:]
    body = bytearray(bytes(hdr) + bytes(0x18) + bytes(ids) + dex[d_off:])
    struct.pack_into("<I", body, 0x20, len(body))
    return bytes(body), b""


entries = {}
if variant in ("vdex006_b64", "decoy_vdex006_nearmiss"):
    d = pad4(dex)
    vdex = b"vdex006\0" + struct.pack("<IIII", 1, len(d), 0, 0) + struct.pack("<I", u32(dex, 8)) + d
    entries["assets/oat/arm64/base.vdex"] = vdex
elif variant == "cdex_b32":
    entries["assets/payload/core.cdex"] = to_cdex(False)[0]
elif variant == "vdex019_hex":
    main, shared = to_cdex(True)
    main = pad4(main)
    vdex = (b"vdex019\0" + b"002\0" + struct.pack("<IIII", 1, 0, 0, 0) + struct.pack("<I", u32(dex, 8))
            + struct.pack("<III", len(main), len(shared), 0) + main + shared)
    entries["assets/oat/arm64/base.vdex"] = vdex
elif variant == "oat_b64":
    (tmp / "p.dex").write_bytes(dex)
    (tmp / "oat.s").write_text(".section .rodata\n.balign 4096\n.globl oatdata\n.type oatdata, @object\noatdata:\n"
                               ".ascii \"oat\\n124\\0\"\n.balign 256\n.incbin \"p.dex\"\n.globl oatlastword\noatlastword:\n"
                               ".long 0\n.size oatdata, . - oatdata\n")
    subprocess.run(["gcc", "-shared", "-nostdlib", "-o", str(tmp / "base.odex"), "oat.s"], cwd=tmp, check=True)
    entries["assets/oat/arm64/base.odex"] = (tmp / "base.odex").read_bytes()
else:
    sys.exit("variant?")

with zipfile.ZipFile(HERE.parent / "skc_decoy_cbc_wrong_key.apk") as zin:
    manifest = zin.read("AndroidManifest.xml")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("AndroidManifest.xml", manifest)
    for n, b in entries.items():
        z.writestr(n, b)
shutil.rmtree(tmp)
print(out, enc)
