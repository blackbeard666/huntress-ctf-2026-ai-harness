"""Writes the pbwire_* fixture payloads with google.protobuf (dynamic descriptors, no lib.android).
usage: python3 gen.py <outdir>   -> <outdir>/<fixture>/<entry path> files; zip them with `zip -X -r`."""
import base64, os, sys
from google.protobuf import descriptor_pb2, descriptor_pool, message_factory

F = descriptor_pb2.FieldDescriptorProto
fd = descriptor_pb2.FileDescriptorProto(name="cfg.proto", package="hx", syntax="proto3")
def msg(name, fields):
    m = fd.message_type.add(name=name)
    for fname, num, typ, tname in fields:
        f = m.field.add(name=fname, number=num, type=typ, label=F.LABEL_OPTIONAL)
        if tname:
            f.type_name = ".hx." + tname
msg("Secret", [("label", 1, F.TYPE_STRING, None), ("blob", 2, F.TYPE_STRING, None), ("data", 3, F.TYPE_BYTES, None),
               ("key", 4, F.TYPE_STRING, None), ("head", 5, F.TYPE_STRING, None), ("tail", 6, F.TYPE_STRING, None)])
msg("Section", [("id", 1, F.TYPE_INT32, None), ("ts", 2, F.TYPE_FIXED64, None), ("secret", 3, F.TYPE_MESSAGE, "Secret")])
msg("Config", [("app", 1, F.TYPE_STRING, None), ("version", 2, F.TYPE_INT32, None), ("section", 3, F.TYPE_MESSAGE, "Section"),
               ("ratio", 4, F.TYPE_FLOAT, None)])
pool = descriptor_pool.DescriptorPool(); pool.Add(fd)
Config = message_factory.GetMessageClass(pool.FindMessageTypeByName("hx.Config"))

def cfg(**secret):
    c = Config(app="com.huntress.vault", version=7, ratio=0.5)
    c.section.id = 3; c.section.ts = 1760000000
    for k, v in secret.items():
        setattr(c.section.secret, k, v)
    return c.SerializeToString()

out = sys.argv[1]
def put(fx, path, data):
    p = os.path.join(out, fx, path); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "wb").write(data)

T1, T2, T3 = "ANS-7c1e9a04b3d256f8", "ANS-e05b4c92a7d13f61", "ANS-19d4f7a2c6b08e35"
# 1: binary .pb asset, token base64'd in a depth-3 string field
put("pbwire_nested_b64", "assets/config.pb", cfg(label="flag", blob=base64.b64encode(T1.encode()).decode()))
# 2: res/raw text file holding base64 of the message; token xor'd (bytes field) with the sibling `key` string
key = "vaultkey"
x = bytes(c ^ ord(key[i % len(key)]) for i, c in enumerate(T2.encode()))
put("pbwire_b64blob_xorkey", "res/raw/state.txt", b"# cached state\n" + base64.b64encode(cfg(label="flag", data=x, key=key)) + b"\n")
# 3: hex text of the message in assets; token split across two sibling string fields
put("pbwire_hex_split", "assets/session.hex", cfg(label="flag", head=T3[:12], tail=T3[12:]).hex().encode())
# decoy: same layout as 1, near-miss token (15 hex digits) base64'd
put("pbwire_decoy_nearmiss", "assets/config.pb", cfg(label="flag", blob=base64.b64encode(b"ANS-7c1e9a04b3d256f").decode()))
for fx in ("pbwire_nested_b64", "pbwire_b64blob_xorkey", "pbwire_hex_split", "pbwire_decoy_nearmiss"):
    put(fx, "AndroidManifest.xml", b"<manifest package='com.huntress.vault'/>")
