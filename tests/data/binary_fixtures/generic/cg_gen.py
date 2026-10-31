#!/usr/bin/env python3
"""campaign-graph-record-facts fixtures (writer side, independent of lib.binary): copies the three GM-delivered D30
Neko members and builds gcc ELFs carrying a raw HCFG-layout record under another magic (`GRPH`) written with stdlib
struct/zlib/json: cg_synth.elf = good GRPH record followed (nearer EOF) by a bad-crc GRPH decoy record;
cg_decoy_badcrc.elf = only the bad-crc record.  usage: python3 cg_gen.py [d30_evidence_dir]"""
import json, os, shutil, struct, subprocess, sys, tempfile, zlib

here = os.path.dirname(os.path.abspath(__file__))
src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    here, "../../../../challenges/day30/binary-campaign-trail/single_solve/work/extracted/evidence")
for role in ("loader", "library", "config"):
    shutil.copyfile(os.path.join(src, f"d30--sample-{role}.n"), os.path.join(here, f"cg_d30_{role}.n"))


def rec(magic, obj, key, ver=2, bad_crc=False):
    p = json.dumps(obj, separators=(",", ":")).encode()
    c = zlib.crc32(p) ^ (0x00010000 if bad_crc else 0)
    return magic + struct.pack("<BBHI", ver, key, len(p), c) + bytes(x ^ key for x in p)


graph = {"schema": "huntress.binary.campaign_graph.v1", "campaign_id": "SYN-77",
         "nodes": ["a.bin", "b.bin", "c.bin", "d.bin"],
         "edges": ["c.bin->d.bin", "a.bin->c.bin", "b.bin->d.bin", "a.bin->b.bin"],
         "load_order": ["a.bin", "c.bin", "b.bin", "d.bin"],
         "config": {"campaign": "SYN-77", "domain": "syn77.example.invalid", "mutex": "Global\\Syn77"},
         "this_role": "b.bin", "network": "none", "effects": "fixture_only"}
decoy = dict(graph, campaign_id="DECOY-00", nodes=["x"], edges=[], load_order=["x"], config={"domain": "decoy.invalid"})
with tempfile.TemporaryDirectory() as td:
    c = os.path.join(td, "m.c")
    with open(c, "w") as f:
        f.write('#include <stdio.h>\nint main(void){puts("campaign graph fixture");return 0;}\n')
    exe = os.path.join(td, "m")
    subprocess.run(["gcc", "-O0", "-o", exe, c], check=True)
    host = open(exe, "rb").read()
open(os.path.join(here, "cg_synth.elf"), "wb").write(
    host + rec(b"GRPH", graph, 0x5A) + b"\0" * 7 + rec(b"GRPH", decoy, 0x33, bad_crc=True))
open(os.path.join(here, "cg_decoy_badcrc.elf"), "wb").write(host + rec(b"GRPH", decoy, 0x33, bad_crc=True))
