"""Generator for the godot_* fixtures (target godot-resource-pck-carrier). Stdlib-only WRITER of the Godot formats as
the engine writes them (independent of lib.codec): text resources per ResourceFormatSaverText (Godot 4 format=3 uses
String.c_escape_multiline -> only \\ and \" escaped, newlines literal; the Godot 3 `.tres` here uses the full C escapes
\\n \\t \\\" that VariantParser also reads), `.pck` per PCKPacker (v1 = Godot 3: GDPC, u32 1, u32 major/minor/patch,
16 x u32 reserved, u32 count, {u32 padded path len, path, u64 abs offset, u64 size, md5[16]}; v2 = Godot 4.0-4.3: +u32
pack_flags, u64 file_base after the version, offsets relative to file_base, + u32 per-file flags), `.gdc` per Godot 3
GDScriptTokenizerBuffer (GDSC, u32 version 13, u32 identifier/constant/line/token counts, identifiers as u32 len +
utf-8 bytes XOR 0xb6 padded to 4, constants as encode_variant (STRING=4: u32 type, u32 len, utf-8, pad 4)).
Run: python3 tests/data/script_fixtures/godot_gen.py  (rewrites the sibling .tscn/.tres/.pck/.gdc files)."""
import hashlib
import struct
import sys
from pathlib import Path

D = Path(__file__).resolve().parent


def plan(hx8, role, attack, nxt):
    return (f"v=3|language=gdscript|role={role}|verdict=suspicious|attack={attack}|adapter=http_client|"
            f"host_profile=standalone|obfuscation_profile=plain_hex|stage_profile=single_descriptor|"
            f"next_language={nxt}|stage_count=2|steps=decode_configuration,return_configuration|"
            f"campaign_id=GDSCRIPT-{hx8}|url=https://gdscript-{hx8}a1.example.invalid/stage|"
            f"file_path=/tmp/huntress-gdscript/.{hx8}{hx8}.stage")


def gd(hx8, p, marker=True):
    h = p.encode().hex()
    return ((f"# HUNTRESS_ANALYSIS_V1:HEX-{h}\n" if marker else "") + "extends RefCounted\n"
            f"const DESCRIPTOR_{hx8.upper()}: String = \"{h}\"\n"
            f"func build_plan_{hx8}() -> Dictionary:\n\treturn {{\"descriptor\": DESCRIPTOR_{hx8.upper()}}}\n")


def esc_multiline(s):                       # Godot String::c_escape_multiline
    return s.replace("\\", "\\\\").replace('"', '\\"')


def esc_full(s):                            # C escapes VariantParser reads
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\t", "\\t")


def tscn4(src):
    return ('[gd_scene load_steps=2 format=3 uid="uid://c8k2q1v0x7y5m"]\n\n'
            '[sub_resource type="GDScript" id="GDScript_7h3kq"]\n'
            f'script/source = "{esc_multiline(src)}"\n\n'
            '[node name="Loader" type="Node"]\nscript = SubResource("GDScript_7h3kq")\n')


def tres3(src):
    return ('[gd_resource type="GDScript" format=2]\n\n[resource]\n'
            f'script/source = "{esc_full(src)}"\n')


def tscn3(src):
    return ('[gd_scene load_steps=2 format=2]\n\n[sub_resource type="GDScript" id=1]\n'
            f'script/source = "{esc_full(src)}"\n\n[node name="Main" type="Node2D"]\nscript = SubResource( 1 )\n')


def pck(files, ver, magic=b"GDPC"):
    pad = lambda n: (4 - n % 4) % 4  # noqa: E731
    paths = [p.encode() for p, _ in files]
    if ver == 1:
        hdr = magic + struct.pack("<4I", 1, 3, 5, 3) + b"\0" * 64 + struct.pack("<I", len(files))
        dsize = sum(4 + len(p) + pad(len(p)) + 32 for p in paths)
        base = len(hdr) + dsize
    else:
        hdr0 = magic + struct.pack("<4I", 2, 4, 2, 1) + struct.pack("<I", 0)
        dsize = sum(4 + len(p) + pad(len(p)) + 36 for p in paths)
        base = len(hdr0) + 8 + 64 + 4 + dsize
        hdr = hdr0 + struct.pack("<Q", base) + b"\0" * 64 + struct.pack("<I", len(files))
    dirb, blob = b"", b""
    for p, (_, data) in zip(paths, files):
        off = (base + len(blob)) if ver == 1 else len(blob)
        dirb += struct.pack("<I", len(p) + pad(len(p))) + p + b"\0" * pad(len(p))
        dirb += struct.pack("<QQ", off, len(data)) + hashlib.md5(data).digest()
        if ver != 1:
            dirb += struct.pack("<I", 0)
        blob += data + b"\0" * pad(len(data))
    return hdr + dirb + blob


def gdc3(idents, strings):
    out = b"GDSC" + struct.pack("<5I", 13, len(idents), len(strings), 0, 0)
    for s in idents:
        b = s.encode() + b"\0"
        b += b"\0" * ((4 - len(b) % 4) % 4)
        out += struct.pack("<I", len(b)) + bytes(c ^ 0xB6 for c in b)
    for s in strings:
        b = s.encode()
        out += struct.pack("<II", 4, len(b)) + b + b"\0" * ((4 - len(b) % 4) % 4)
    return out


P = {k: plan(*a) for k, a in {
    "tscn4": ("4be19c07", "downloader", "T1105", "jscript"),
    "tres3": ("90d2aa31", "launcher", "T1059", "powershell"),
    "pck1": ("5c7e0f12", "staged_chain", "T1059", "vbscript"),
    "pck2": ("e03b6d48", "downloader", "T1105", "bash"),
    "gdc3": ("17ac94fe", "launcher", "T1059", "python")}.items()}
BENIGN = "extends Node\nconst GREETING: String = \"hello \\\"world\\\"\"\nfunc _ready():\n\tprint(GREETING)\n"
PROJECT = b'config_version=4\n\n[application]\n\nconfig/name="Press Start"\nrun/main_scene="res://main.tscn"\n'
OUT = {
    "godot4_tscn_subresource.tscn": tscn4(gd("4be19c07", P["tscn4"], marker=False)).encode(),
    "godot3_tres_escaped.tres": tres3(gd("90d2aa31", P["tres3"])).encode(),
    "godot3_pck_v1.pck": pck([("res://project.godot", PROJECT), ("res://icon.png", b"\x89PNG\r\n\x1a\n" + bytes(40)),
                              ("res://main.tscn", tscn3(gd("5c7e0f12", P["pck1"], marker=False)).encode())], 1),
    "godot4_pck_v2.pck": pck([("res://project.godot", PROJECT),
                              ("res://scripts/loader.gd", gd("e03b6d48", P["pck2"], marker=False).encode())], 2),
    "godot3_gdc_tokenized.gdc": gdc3(["RefCounted", "DESCRIPTOR_17AC94FE", "build_plan_17ac94fe", "descriptor"],
                                     ["# HUNTRESS", P["gdc3"].encode().hex()]),
    "godot_decoy_benign.tscn": tscn4(BENIGN).encode(),
    "godot_decoy_badmagic.pck": pck([("res://project.godot", PROJECT), ("res://main.gd", BENIGN.encode())], 1,
                                    magic=b"GDPK"),
}
if __name__ == "__main__":
    for n, b in OUT.items():
        (D / n).write_bytes(b)
    if "-p" in sys.argv:
        for k, v in P.items():
            print(k, v)
