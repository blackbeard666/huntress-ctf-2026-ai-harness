"""Offline generator for the serialization-wrapper fixtures (NOT in-window code). Each fixture's `encoded` comes from
an independent writer (pickle / marshal / msgpack / cbor2 / pymongo bson / google.protobuf / php / java) and its
`oracle_plain` from an independent reader; lib.warmups_codecs is never used here.
Run from the repo root: python3 tests/data/warmups_fixtures/serial_mkfixtures.py"""
import json
import os
import subprocess
from pathlib import Path

D = Path(__file__).resolve().parent
S = "Nice work decoding this warmup! To solve, submit this exact answer to the Game Master: "
PY = "python3 -c "
CASES = [
    ("serial-pickle-p4-amber", "pickle", S + "amber-otter-41",
     PY + "'import pickle,base64,os;print(base64.b64encode(pickle.dumps({\"note\":os.environ[\"plain\"],\"n\":3},protocol=4)).decode())'",
     PY + "'import pickletools,base64,os;b=base64.b64decode(os.environ[\"encoded\"]);print([a for o,a,p in pickletools.genops(b) if isinstance(a,str) and a!=\"note\"][0])'"),
    ("serial-pickle-p0-cobalt", "pickle", S + "cobalt-heron-27",
     PY + "'import pickle,base64,os;print(base64.b64encode(pickle.dumps(os.environ[\"plain\"],protocol=0)).decode())'",
     PY + "'import pickletools,base64,os;b=base64.b64decode(os.environ[\"encoded\"]);print([a for o,a,p in pickletools.genops(b) if isinstance(a,str)][0])'"),
    ("serial-marshal-tuple-clover", "marshal", S + "clover-badger-63",
     PY + "'import marshal,base64,os;print(base64.b64encode(marshal.dumps((1,os.environ[\"plain\"]))).decode())'",
     PY + "'import marshal,base64,os;print(marshal.loads(base64.b64decode(os.environ[\"encoded\"]))[1])'"),
    ("serial-marshal-code-jade", "marshal", S + "jade-falcon-58",
     PY + "'import marshal,base64,os;print(base64.b64encode(marshal.dumps(compile(\"msg = %r\" % os.environ[\"plain\"],\"w\",\"exec\"))).decode())'",
     PY + "'import marshal,base64,os;c=marshal.loads(base64.b64decode(os.environ[\"encoded\"]));print([x for x in c.co_consts if isinstance(x,str)][0])'"),
    ("serial-msgpack-map-maple", "msgpack", S + "maple-lynx-12",
     PY + "'import msgpack,base64,os;print(base64.b64encode(msgpack.packb({\"m\":os.environ[\"plain\"],\"k\":[1,2.5,None]})).decode())'",
     PY + "'import msgpack,base64,os;print(msgpack.unpackb(base64.b64decode(os.environ[\"encoded\"]))[\"m\"])'"),
    ("serial-msgpack-split-ivory", "msgpack", S + "ivory-walrus-85",
     PY + "'import msgpack,base64,os;p=os.environ[\"plain\"];i=p.rindex(\" \");print(base64.b64encode(msgpack.packb([p[:i],p[i+1:]])).decode())'",
     PY + "'import msgpack,base64,os;print(\" \".join(msgpack.unpackb(base64.b64decode(os.environ[\"encoded\"]))))'"),
    ("serial-cbor-map-amber", "cbor", S + "amber-gecko-30",
     PY + "'import cbor2,base64,os;print(base64.b64encode(cbor2.dumps({\"text\":os.environ[\"plain\"],\"v\":-500})).decode())'",
     PY + "'import cbor2,base64,os;print(cbor2.loads(base64.b64decode(os.environ[\"encoded\"]))[\"text\"])'"),
    ("serial-cbor-tag-hex-cobalt", "cbor", S + "cobalt-raven-74",
     PY + "'import cbor2,os;print(cbor2.dumps(cbor2.CBORTag(55799,[os.environ[\"plain\"].encode(),True])).hex())'",
     PY + "'import cbor2,os;x=cbor2.loads(bytes.fromhex(os.environ[\"encoded\"]));print(getattr(x,\"value\",x)[0].decode())'"),
    ("serial-bson-doc-clover", "bson", S + "clover-mantis-19",
     PY + "'import bson,base64,os;print(base64.b64encode(bson.encode({\"_id\":1,\"msg\":os.environ[\"plain\"],\"f\":1.5})).decode())'",
     PY + "'import bson,base64,os;print(bson.decode(base64.b64decode(os.environ[\"encoded\"]))[\"msg\"])'"),
    ("serial-bson-nested-jade", "bson", S + "jade-condor-46",
     PY + "'import bson,os;print(bson.encode({\"a\":{\"b\":[os.environ[\"plain\"]]},\"t\":True}).hex())'",
     PY + "'import bson,os;print(bson.decode(bytes.fromhex(os.environ[\"encoded\"]))[\"a\"][\"b\"][0])'"),
    ("serial-protobuf-struct-maple", "protobuf", S + "maple-bison-67",
     PY + "'import base64,os;from google.protobuf import struct_pb2;m=struct_pb2.Struct();m.update({\"msg\":os.environ[\"plain\"]});print(base64.b64encode(m.SerializeToString()).decode())'",
     PY + "'import base64,os;from google.protobuf import struct_pb2;m=struct_pb2.Struct();m.ParseFromString(base64.b64decode(os.environ[\"encoded\"]));print(m[\"msg\"])'"),
    ("serial-protobuf-any-ivory", "protobuf", S + "ivory-ferret-22",
     PY + "'import base64,os;from google.protobuf import wrappers_pb2,any_pb2;a=any_pb2.Any();a.Pack(wrappers_pb2.StringValue(value=os.environ[\"plain\"]));print(base64.b64encode(a.SerializeToString()).decode())'",
     PY + "'import base64,os;from google.protobuf import wrappers_pb2,any_pb2;a=any_pb2.Any();a.ParseFromString(base64.b64decode(os.environ[\"encoded\"]));v=wrappers_pb2.StringValue();a.Unpack(v);print(v.value)'"),
    ("serial-php-raw-amber", "php", S + "amber-puffin-90",
     "php -r 'echo serialize([\"msg\"=>getenv(\"plain\"),\"n\"=>3,\"ok\"=>true,\"f\"=>1.5]);'",
     "php -r 'echo unserialize(getenv(\"encoded\"), [\"allowed_classes\"=>false])[\"msg\"];'"),
    ("serial-php-object-b64-cobalt", "php", S + "cobalt-marmot-33",
     "php -r '$o=new stdClass; $o->note=getenv(\"plain\"); $o->tags=[\"a\",\"b\"]; echo base64_encode(serialize($o));'",
     "php -r 'echo unserialize(base64_decode(getenv(\"encoded\")), [\"allowed_classes\"=>[\"stdClass\"]])->note;'"),
    ("serial-java-hashmap-clover", "java", S + "clover-jackal-51",
     "java tests/data/warmups_fixtures/SerialFix.java gen",
     "java tests/data/warmups_fixtures/SerialFix.java read"),
    ("serial-java-hashmap-jade", "java", S + "jade-stoat-08",
     "java tests/data/warmups_fixtures/SerialFix.java gen",
     "java tests/data/warmups_fixtures/SerialFix.java read"),
]


def sh(cmd, **env):
    return subprocess.run(["bash", "-c", cmd], capture_output=True, text=True, check=True,
                          env=dict(os.environ, **env)).stdout.strip()


def put(name, fx):
    (D / f"{name}.json").write_text(json.dumps(fx, indent=1) + "\n")


enc = {}
for name, form, plain, gen, orc in CASES:
    e = sh(gen, plain=plain)
    o = sh(orc, encoded=e)
    assert o == plain, (name, o)
    enc[name] = e
    put(name, {"codec": f"serialization-wrapper[{form}]", "plain": plain, "encoded": e, "generator_cmd": gen,
               "oracle_cmd": orc, "oracle_plain": o, "expected": "match"})


def decoy(name, form, e, gen, orc):
    r = subprocess.run(["bash", "-c", orc], capture_output=True, text=True, env=dict(os.environ, encoded=e))
    put(name, {"codec": f"serialization-wrapper[{form}]", "plain": None, "encoded": e, "generator_cmd": gen,
               "oracle_cmd": orc, "oracle_plain": None, "oracle_rc": r.returncode,
               "oracle_err": r.stderr.strip().splitlines()[-1][:200] if r.stderr.strip() else "", "decoy": True,
               "expected": "none"})


import base64  # noqa: E402

pk = base64.b64decode(enc["serial-pickle-p4-amber"])
decoy("serial-decoy-pickle-no-stop", "pickle", base64.b64encode(pk[:-1]).decode(),
      "serial-pickle-p4-amber bytes with the final STOP opcode cut, base64",
      PY + "'import pickletools,base64,os;list(pickletools.genops(base64.b64decode(os.environ[\"encoded\"])))'")
ph = sh(CASES[12][3], plain=CASES[12][2])
bad = ph.replace(f's:{len(CASES[12][2])}:', f's:{len(CASES[12][2]) + 2}:', 1)
decoy("serial-decoy-php-bad-length", "php", bad, "serial-php-raw-amber text with the msg s:N: length +2",
      "php -r 'var_dump(unserialize(getenv(\"encoded\")));' | grep -q '^bool(false)' && exit 1")
jv = base64.b64decode(enc["serial-java-hashmap-clover"])
decoy("serial-decoy-java-bad-magic", "java", base64.b64encode(b"\xac\xed\x00\x06" + jv[4:]).decode(),
      "serial-java-hashmap-clover bytes with STREAM_VERSION 5 -> 6, base64", "java tests/data/warmups_fixtures/SerialFix.java read")
bs = bytearray(base64.b64decode(enc["serial-bson-doc-clover"]))
bs[0] += 1
decoy("serial-decoy-bson-bad-length", "bson", base64.b64encode(bytes(bs)).decode(),
      "serial-bson-doc-clover bytes with the document int32 length +1, base64",
      PY + "'import bson,base64,os;bson.decode(base64.b64decode(os.environ[\"encoded\"]))'")
decoy("serial-decoy-base64-prose", "msgpack", base64.b64encode(S.encode() + b"none-here-00").decode(),
      "printf %s \"$plain\" | base64 -w0  (plain prose, no serialization)",
      PY + "'import msgpack,base64,os;msgpack.unpackb(base64.b64decode(os.environ[\"encoded\"]))'")
print("ok", len(CASES), "fixtures + 5 decoys")
