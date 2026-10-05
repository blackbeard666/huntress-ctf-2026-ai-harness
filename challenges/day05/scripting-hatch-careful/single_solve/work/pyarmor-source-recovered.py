# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_316c8dcc = "1a:51:5e:10:1f:18:09:1c:1f:51:0d:0f:1d:19:05:1e:09:33:1e:09:01:03:18:09:40:08:05:1f:1c:0d:18:0f:04:33:01:09:01:03:1e:15:10:0d:08:0d:1c:18:09:1e:51:19:1e:00:00:05:0e:33:01:09:01:03:1e:15:10:1f:18:0d:0b:09:33:0f:03:19:02:18:51:5d:10:1f:15:02:18:0d:14:51:09:14:0f:09:1c:18:05:03:02:33:09:14:1c:1e:09:1f:1f:05:03:02:10:03:0e:0a:19:1f:0f:0d:18:05:03:02:51:01:0d:1e:1f:04:0d:00:33:09:02:1a:09:00:03:1c:09:33:1c:00:0d:02:10:0f:0d:1e:1e:05:09:1e:51:1c:15:0d:1e:01:03:1e:33:03:0e:0a:19:1f:0f:0d:18:09:08:10:1b:05:02:08:03:1b:1f:33:0f:04:0d:05:02:51:1b:1f:0f:1e:05:1c:18:33:18:03:33:1c:15:18:04:03:02:10:0f:0d:01:1c:0d:05:0b:02:33:05:08:51:0f:0d:01:1c:0d:05:0b:02:41:5e:54:5d:0a:5a:08:59:54:5f:0f:10:19:1e:00:51:04:18:18:1c:1f:56:43:43:5e:54:5d:0a:5a:08:59:54:5f:0f:42:09:14:0d:01:1c:00:09:42:05:02:1a:0d:00:05:08:43:5b:55:0e:58:5b:5b:5f:0e:42:1c:15:10:19:1f:09:1e:33:0d:0b:09:02:18:51:24:19:02:18:1e:09:1f:1f:3c:15:18:04:03:02:43:5e:54:5d:0a:5a:08:59:54:5f:0f"
CODEC_316c8dcc = "hex_colon|single_byte_xor|6c"

def load_316c8dcc():
    return bytes.fromhex(MATERIAL_316c8dcc.replace(":", " "))

def decode_316c8dcc(e):
    return bytes(value ^ 108 for value in e)

def recover_316c8dcc():
    n = 19 * 7 - 133
    for _pass in range(1):
        d = decode_316c8dcc(load_316c8dcc())
    t = d.decode("ascii", "strict")
    return t

def inspect_316c8dcc():
    stream = io.BytesIO(recover_316c8dcc().encode("ascii"))
    return stream.read().decode("ascii")

def surface_316c8dcc():
    try:
        raise LookupError("surface")
    except LookupError:
        return ("exception_expression", "marshal_envelope_plan", "pyarmor_obfuscated", "wscript_to_python")

def obfuscation_316c8dcc():
    marshal_plan = {"format": "code_object", "action": "inspect_only", "label": "marshal_envelope_plan"}
    return marshal_plan["label"]

def plan_316c8dcc():
    fields = dict(item.split("=", 1) for item in inspect_316c8dcc().split("|"))
    analysis_surface = surface_316c8dcc()
    obfuscation_surface = obfuscation_316c8dcc()
    operation_plan = ("urllib_memory", fields["url"], "memory-handoff")
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_316c8dcc())

# reconstruction complete