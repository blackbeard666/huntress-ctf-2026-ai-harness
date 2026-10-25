"""Generator for the renpy_* fixtures (target game-archive-carriers). Stdlib-only WRITER (independent of lib.codec):
`.rpa` as Ren'Py's archiver / rpatool write it -- header `RPA-3.0 %016x %08x\\n` (RPA-2.0: `RPA-2.0 %016x\\n`, no key),
member data stored raw, then the index = zlib.compress(pickle.dumps({path: [(offset ^ key, length ^ key, b"")]}, proto))
(stdlib pickle, protocol 2 writes the py3 bytes prefix as `_codecs.encode` REDUCE); `.rpyc` as Ren'Py 8 writes it --
`RENPY RPC2`, slot table {u32 slot, u32 start, u32 len} ended by slot 0, slot 1 = zlib(pickle((data, [ast nodes]), 2))
with stand-in classes registered under renpy.ast (pickle stores module/class names + __dict__ state like the engine).
Run: python3 -I tests/data/script_fixtures/renpy_gen.py  (rewrites the sibling .json fixtures)."""
import base64
import json
import pickle
import struct
import sys
import types
import zlib
from pathlib import Path

D = Path(__file__).resolve().parent
ast = types.ModuleType("renpy.ast")
sys.modules["renpy"] = types.ModuleType("renpy")
sys.modules["renpy.ast"] = ast


def _cls(name):
    c = type(name, (object,), {"__module__": "renpy.ast"})
    setattr(ast, name, c)
    return c


Python, PyCode, Say, Label = (_cls(n) for n in ("Python", "PyCode", "Say", "Label"))


def node(cls, **kw):
    o = cls()
    o.__dict__.update(kw)
    return o


def plan(hx8, role, attack, nxt):
    return (f"v=3|language=renpy|role={role}|verdict=suspicious|attack={attack}|adapter=http_client|"
            f"host_profile=standalone|obfuscation_profile=plain_hex|stage_profile=single_descriptor|"
            f"next_language={nxt}|stage_count=2|steps=decode_configuration,return_configuration|"
            f"campaign_id=RENPY-{hx8}|url=https://renpy-{hx8}a1.example.invalid/stage|"
            f"file_path=/tmp/huntress-renpy/.{hx8}{hx8}.stage")


def rpy(hx8, p):
    return (f"# HUNTRESS_ANALYSIS_V1:HEX-{p.encode().hex()}\n"
            f"init python:\n    DESCRIPTOR_{hx8.upper()} = \"{p.encode().hex()}\"\n"
            "label start:\n    \"Welcome back.\"\n    return\n")


def rpyc(hx8, p, benign=False):
    src = ("persistent.volume = 0.8\n" if benign else f"DESCRIPTOR_{hx8.upper()} = \"{p.encode().hex()}\"\n")
    stmts = [node(Label, name="start", block=[], filename="game/script.rpy", linenumber=1),
             node(Python, code=node(PyCode, source=src, location=("game/script.rpy", 2), mode="exec"),
                  filename="game/script.rpy", linenumber=2, store="store"),
             node(Say, who=None, what="Welcome back.", filename="game/script.rpy", linenumber=4)]
    body = zlib.compress(pickle.dumps(({"version": 5003000, "key": "unlocked"}, stmts), 2))
    slots = struct.pack("<III", 1, 10 + 24, len(body)) + struct.pack("<III", 0, 0, 0)
    return b"RENPY RPC2" + slots + body


def rpa(files, ver="3.0", key=0x42424242, proto=2, magic=None):
    hdr_len = 34 if ver == "3.0" else 25
    out, idx = bytearray(b"\x00" * hdr_len), {}
    for name, data in files:
        k = key if ver != "2.0" else 0
        idx[name] = [(len(out) ^ k, len(data) ^ k, b"")]
        out += data
    off = len(out)
    out += zlib.compress(pickle.dumps(idx, proto))
    h = (f"RPA-3.0 {off:016x} {key:08x}\n" if ver == "3.0" else f"RPA-2.0 {off:016x}\n").encode()
    if magic:
        h = magic + h[len(magic):]
    out[:hdr_len] = h
    return bytes(out)


def emit(stem, desc, blob, exp, rep, decoy=False):
    json.dump({"description": desc, "material": base64.b64encode(blob).decode(), "rep": rep,
               "transform": "identity", "key": "", "expected": exp, "decoy": decoy,
               "generator_cmd": f"python3 -I tests/data/script_fixtures/renpy_gen.py  (stdlib pickle/zlib/struct writer of "
                                f"the Ren'Py format -> {stem}.json material, base64)",
               "oracle_cmd": f"python3 -I tests/data/script_fixtures/renpy_oracle.py tests/data/script_fixtures/{stem}.json"
                             f"  (stdlib pickle.loads index / pickletools.genops strings, hex -> plan; prints "
                             f"{str(exp)[:40]!r}...)"},
              open(D / f"{stem}.json", "w"), indent=1)


if __name__ == "__main__":
    p1 = plan("3f9a1c02", "launcher", "T1059", "python")
    emit("renpy_rpa3_script_rpy", "RPA-3.0 (key 0x42424242, pickle protocol 2 index with _codecs.encode bytes prefix) "
         "carrying game/script.rpy with a marker line + init python descriptor, plus options.rpy and a png",
         rpa([("game/options.rpy", b"define config.name = \"Night Shift\"\n"), ("game/gui/logo.png", b"\x89PNG\r\n\x1a\n" + b"\x00" * 40),
              ("game/script.rpy", rpy("3f9a1c02", p1).encode())]), p1, "rpa")
    p2 = plan("b71e0d54", "downloader", "T1105", "powershell")
    emit("renpy_rpa3_rpyc_proto4", "RPA-3.0 (key 0x0badf00d, pickle protocol 4 index) carrying game/script.rpyc "
         "(RENPY RPC2) whose python block source holds the descriptor hex",
         rpa([("game/script.rpyc", rpyc("b71e0d54", p2))], key=0x0BADF00D, proto=4), p2, "rpa")
    p3 = plan("c5d20e9a", "staged_chain", "T1059", "bash")
    emit("renpy_rpyc_rpc2", "standalone Ren'Py 8 .rpyc (RENPY RPC2 slot 1, zlib pickle protocol 2 of renpy.ast "
         "nodes): the python block source string carries the descriptor hex", rpyc("c5d20e9a", p3), p3, "rpyc")
    p4 = plan("19e4a7b3", "launcher", "T1059", "jscript")
    emit("renpy_rpa2_script_rpy", "RPA-2.0 (no key) carrying game/script.rpy", rpa([("game/script.rpy", rpy("19e4a7b3", p4).encode())],
         ver="2.0"), p4, "rpa")
    emit("renpy_decoy_badmagic", "DECOY: renamed impostor (`RPX-3.0` magic) of an RPA carrying a plan-bearing script.rpy",
         rpa([("game/script.rpy", rpy("77aa0b1c", plan("77aa0b1c", "launcher", "T1059", "python")).encode())],
             magic=b"RPX-"), None, "rpa", decoy=True)
    emit("renpy_decoy_benign_rpyc", "DECOY: valid RENPY RPC2 .rpyc whose python block is benign (no descriptor)",
         rpyc("00000000", "", benign=True), None, "rpyc", decoy=True)
