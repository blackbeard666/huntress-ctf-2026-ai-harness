# Python exec onions (target python-onion-regex-fold), written with stdlib base64/zlib/lzma/marshal only.
# usage: python3 -I py_onion_gen.py <out_dir>
import base64, json, lzma, marshal, os, sys, zlib
D = sys.argv[1]
GEN = "python3 -I tests/data/script_fixtures/py_onion_gen.py tests/data/script_fixtures"
ORACLE = ("python3 -I -c 'import sys; g={}; exec(open(sys.argv[1]).read(), g); print(g.get(\"PLAN\"))' "
          "tests/data/script_fixtures/%s")


def w(name, src, plan, decoy=False, note=""):
    open(os.path.join(D, name + ".py"), "w", newline="\n").write(src)
    json.dump({"expected_plain": plan, "decoy": decoy, "generator_cmd": GEN + "  # " + note,
               "oracle_cmd": ORACLE % (name + ".py")}, open(os.path.join(D, name + ".json"), "w"), indent=1)


def code(plan):
    return ("import os\nPLAN = %r\nif os.name == 'nt':\n    pass\n" % plan).encode()


lam = "_ = lambda __ : __import__('%s').%s(__import__('zlib').decompress(__import__('base64').b64decode(__[::-1])));exec((_)(b'%s'))\n"

# 1: pyobfuscate-style lambda (__import__ + [::-1] + zlib + b64) -> layer 2 getattr(__import__('base64'),'b32decode')
p1 = "v=3|language=python|role=stager|verdict=malicious|attack=T1027|adapter=lambda_onion|stage_count=2|steps=reverse_literal,inflate,b32_stage|campaign_id=PY-3c9d41e0|url=https://py-3c9d41e0.example.invalid/st"
l2 = "exec(getattr(__import__('base64'), 'b32decode')('%s').decode())\n" % base64.b32encode(code(p1)).decode()
w("py_onion_lambda_getattr", "# -*- coding: utf-8 -*-\n" +
  lam % ("builtins", "bytes", base64.b64encode(zlib.compress(l2.encode(), 9)).decode()[::-1]),
  p1, note="lambda __import__ zlib/b64 reversed -> getattr b32decode")

# 2: getattr(..,'b85decode') -> lzma -> bytes.fromhex -> .decode() layer, __import__ with spaces
p2 = "v=3|language=python|role=loader|verdict=suspicious|attack=T1140|adapter=b85_lzma_hex|stage_count=3|steps=b85,unxz,fromhex,exec|campaign_id=PY-a1f00e72|url=https://py-a1f00e72.example.invalid/ld"
l3 = "exec(bytes.fromhex('%s').decode('utf-8'))\n" % code(p2).hex()
l2 = "import base64\nexec(__import__('lzma').decompress(getattr(__import__('base64'), 'b85decode')(%r)))\n" % \
    base64.b85encode(lzma.compress(l3.encode())).decode()
w("py_onion_b85_lzma_hex", "#!/usr/bin/env python3\nexec(__import__('base64').b64decode('%s'))\n" %
  base64.b64encode(l2.encode()).decode(), p2, note="b64 -> getattr b85decode + lzma -> bytes.fromhex")

# 3: lambda onion ending in marshal.loads: the plan is read from the code object's string constants (report only)
p3 = "v=3|language=python|role=dropper|verdict=malicious|attack=T1059.006|adapter=marshal_codeobj|stage_count=2|steps=inflate,unmarshal,exec|campaign_id=PY-6e02b5d8|url=https://py-6e02b5d8.example.invalid/dr"
co = marshal.dumps(compile(code(p3), "<x>", "exec"))
w("py_onion_marshal_codeobj", lam % ("marshal", "loads", base64.b64encode(zlib.compress(co, 9)).decode()[::-1]),
  p3, note="lambda marshal.loads(zlib(b64(rev)))")

# 4: DECOY - same marshal lambda shape, benign code object (no plan constant)
co = marshal.dumps(compile("import sys\nPLAN = None\nprint('telemetry ok', sys.version)\n", "<x>", "exec"))
w("py_onion_decoy_marshal_benign", lam % ("marshal", "loads", base64.b64encode(zlib.compress(co, 9)).decode()[::-1]),
  None, decoy=True, note="decoy: marshal lambda, benign")

# 5: DECOY - lambda onion whose zlib stream is truncated (no end marker) -> no plan, never a partial one
blob = zlib.compress(code("v=3|language=python|role=stager|verdict=malicious|attack=T1027|campaign_id=PY-deadbeef"), 9)[:-9]
w("py_onion_decoy_trunc", lam % ("builtins", "bytes", base64.b64encode(blob).decode()[::-1]),
  None, decoy=True, note="decoy: truncated zlib")
