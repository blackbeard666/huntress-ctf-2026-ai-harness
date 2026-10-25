"""Generator for the unityfs_* fixtures (target game-archive-carriers). WRITER independent of lib.codec: stdlib struct +
the `lz4` package (lz4.block.compress) lay out a UnityFS asset bundle as Unity writes it -- `UnityFS\\0`, u32 BE format
version 7, `5.x.x\\0`, unity revision `\\0`, u64 total size, u32 compressed / uncompressed blocks-info size, u32 flags
(0x43 = LZ4HC blocks info, directly after the 16-aligned header), blocks info = 16-byte hash, u32 block count, {u32
usize, u32 csize, u16 flags (3 = LZ4HC)}, u32 node count, {u64 offset, u64 size, u32 flags, path\\0}, then the blocks.
The CAB node carries a TextAsset-style string (u32 len + utf-8 m_Script) among binary filler.
Run: python3 -I tests/data/script_fixtures/unityfs_gen.py  (rewrites the sibling .json fixtures)."""
import base64
import json
import struct
from pathlib import Path

import lz4.block

D = Path(__file__).resolve().parent


def plan(hx8, role, attack, nxt):
    return (f"v=3|language=csharp|role={role}|verdict=suspicious|attack={attack}|adapter=http_client|"
            f"host_profile=standalone|obfuscation_profile=plain_hex|stage_profile=single_descriptor|"
            f"next_language={nxt}|stage_count=2|steps=decode_configuration,return_configuration|"
            f"campaign_id=UNITY-{hx8}|url=https://unity-{hx8}a1.example.invalid/stage|"
            f"file_path=/tmp/huntress-unity/.{hx8}{hx8}.stage")


def textasset(name, script):
    n, s = name.encode(), script.encode()
    pad = lambda x: x + b"\x00" * (-len(x) % 4)  # noqa: E731
    return pad(struct.pack("<I", len(n)) + n) + pad(struct.pack("<I", len(s)) + s)


def bundle(node_data, node="CAB-5d1f0e2a9c7b4e31a0f2d6c8b9e1a3f4", magic=b"UnityFS\x00", chunk=0x8000):
    blocks, raw = [], node_data
    for i in range(0, len(raw), chunk):
        part = raw[i:i + chunk]
        blocks.append((len(part), lz4.block.compress(part, mode="high_compression", store_size=False)))
    info = b"\x00" * 16 + struct.pack(">I", len(blocks))
    info += b"".join(struct.pack(">IIH", u, len(c), 3) for u, c in blocks)
    info += struct.pack(">I", 1) + struct.pack(">QQI", 0, len(raw), 4) + node.encode() + b"\x00"
    cinfo = lz4.block.compress(info, mode="high_compression", store_size=False)
    head = magic + struct.pack(">I", 7) + b"5.x.x\x00" + b"2022.3.10f1\x00"
    fixed_len = len(head) + 8 + 12
    pad = -fixed_len % 16
    total = fixed_len + pad + len(cinfo) + sum(len(c) for _, c in blocks)
    head += struct.pack(">QIII", total, len(cinfo), len(info), 0x43) + b"\x00" * pad
    return head + cinfo + b"".join(c for _, c in blocks)


def cab(script, name="loader_config"):
    filler = bytes(range(256)) * 8
    return b"\x00\x00\x00\x00" * 4 + filler + textasset(name, script) + filler


def cs(hx8, p):
    return (f"// HUNTRESS_ANALYSIS_V1:HEX-{p.encode().hex()}\nusing UnityEngine;\npublic class Loader{hx8} : "
            f"MonoBehaviour {{\n    const string DESCRIPTOR_{hx8.upper()} = \"{p.encode().hex()}\";\n}}\n")


def emit(stem, desc, blob, exp, decoy=False):
    json.dump({"description": desc, "material": base64.b64encode(blob).decode(), "rep": "unityfs",
               "transform": "identity", "key": "", "expected": exp, "decoy": decoy,
               "generator_cmd": f"python3 -I tests/data/script_fixtures/unityfs_gen.py  (stdlib struct + lz4.block "
                                f"writer of the UnityFS layout -> {stem}.json material, base64)",
               "oracle_cmd": f"PYTHONPATH=tools/unitypy python3 tests/data/script_fixtures/unityfs_oracle.py "
                             f"tests/data/script_fixtures/{stem}.json  (UnityPy BundleFile reader -> node bytes, hex -> "
                             f"plan; prints {str(exp)[:40]!r}...)"},
              open(D / f"{stem}.json", "w"), indent=1)


if __name__ == "__main__":
    p1 = plan("4e8b2d71", "launcher", "T1059", "powershell")
    emit("unityfs_lz4hc_textasset", "UnityFS v7 bundle, LZ4HC blocks info + 2 LZ4HC blocks, CAB node with a TextAsset "
         "m_Script C# source carrying the descriptor", bundle(cab(cs("4e8b2d71", p1) + "// " + "x" * 33000)), p1)
    p2 = plan("a09c3f66", "downloader", "T1105", "python")
    emit("unityfs_decoy_badmagic", "DECOY: renamed impostor (`UnityFX` magic) of a bundle whose TextAsset carries a "
         "plan", bundle(cab(cs("a09c3f66", p2)), magic=b"UnityFX\x00"), None, decoy=True)
