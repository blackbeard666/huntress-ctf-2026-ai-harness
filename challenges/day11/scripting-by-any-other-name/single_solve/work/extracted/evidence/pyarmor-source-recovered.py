# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_17618467 = "d5d58083808fd483838699d8d9dec2cfe6c5c5d3c4c2d8c3fe8bc2d8d3d1d7e9c4d3c5c3cacfc698828e81d287d2d78499d2dfdad7c0d8df98d3dac6dbd7ced398d5d58083808fd483838699998cc5c6c2c2de8bdac4c3cad5d58083808fd48383869bd8d1dfd7c6dbd7d58bd2dfe9d8d1dfd7c6dbd7d5cad8d9dec2cfc6e9d9c2e9c2c6dfc4d5c5c18bd8dfd7ded5e9c5c1d9d2d8dfc1cad2d3c2d7d5c5c3d0d4d9e9c4d9dbc4d7cfc68bc4d3dfc4c4d7d5cad8d7dac6e9d3c6d9dad3c0d8d3e9dad7dec5c4d7db8bd8d9dfc2d7d5c5c3d0d4d9cad8d9dfc5c5d3c4c6ced3e9d8d9dfc2c6d3d5ced38bced7c2d8cfc5ca878bc2d8c3d9d5e9d3d1d7c2c5cacfc4d9dbd3dbe9d8d7dac6e9c2d3ddd5d9c58bc4d3c2c6d7d2d7cacfc4d9dbd3dbe9ded5c2d7c6c5dfd29ad3c2d9dbd3c4e9d3c4dfc3c7d5d78bc5c6d3c2c5ca848bc0"
CODEC_17618467 = "hex_literal|reverse_then_xor|b6"

def load_17618467():
    return bytes.fromhex(MATERIAL_17618467)

def decode_17618467(stored_bytes):
    return bytes(value ^ 182 for value in reversed(stored_bytes))

def recover_17618467():
    harmless_value = (3, 5, 8, 13)[1:3]
    for _pass in range(1):
        recovered_bytes = decode_17618467(load_17618467())
    configuration_text = recovered_bytes.decode("ascii", "strict")
    return configuration_text

def inspect_17618467():
    stream = io.BytesIO(recover_17618467().encode("ascii"))
    return stream.read().decode("ascii")

def surface_17618467():
    try:
        raise LookupError("surface")
    except LookupError:
        return ("exception_expression", "marshal_envelope_plan", "pyarmor_obfuscated", "wscript_to_python")

def obfuscation_17618467():
    marshal_plan = {"format": "code_object", "action": "inspect_only", "label": "marshal_envelope_plan"}
    return marshal_plan["label"]

def plan_17618467():
    fields = dict(item.split("=", 1) for item in inspect_17618467().split("|"))
    analysis_surface = surface_17618467()
    obfuscation_surface = obfuscation_17618467()
    operation_plan = ("socket_plan_memory", fields["url"], "memory-handoff")
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_17618467())

# reconstruction complete