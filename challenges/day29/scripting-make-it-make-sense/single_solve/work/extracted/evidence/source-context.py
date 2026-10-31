# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_04a8ae4b = (133, 76, 65, 139, 130, 131, 116, 127, 130, 76, 115, 116, 114, 126, 115, 116, 110, 114, 126, 125, 117, 120, 118, 132, 129, 112, 131, 120, 126, 125, 59, 129, 116, 131, 132, 129, 125, 110, 114, 126, 125, 117, 120, 118, 132, 129, 112, 131, 120, 126, 125, 139, 112, 115, 112, 127, 131, 116, 129, 76, 112, 129, 118, 127, 112, 129, 130, 116, 110, 125, 112, 124, 116, 130, 127, 112, 114, 116, 139, 130, 131, 112, 118, 116, 110, 114, 126, 132, 125, 131, 76, 64, 139, 130, 136, 125, 131, 112, 135, 76, 127, 123, 112, 120, 125, 110, 117, 132, 125, 114, 131, 120, 126, 125, 130, 139, 126, 113, 117, 132, 130, 114, 112, 131, 120, 126, 125, 76, 131, 129, 112, 125, 130, 117, 126, 129, 124, 110, 126, 125, 123, 136, 139, 114, 112, 129, 129, 120, 116, 129, 76, 129, 112, 134, 110, 130, 126, 132, 129, 114, 116, 139, 134, 120, 125, 115, 126, 134, 130, 110, 114, 119, 112, 120, 125, 76, 115, 120, 129, 116, 114, 131, 110, 127, 136, 131, 119, 126, 125, 110, 116, 135, 116, 139, 114, 112, 124, 127, 112, 120, 118, 125, 110, 120, 115, 76, 114, 112, 124, 127, 112, 120, 118, 125, 60, 64, 64, 72, 115, 112, 70, 116, 72, 66, 115, 139, 119, 126, 130, 131, 110, 120, 115, 76, 119, 126, 130, 131, 60, 64, 64, 72, 115, 112, 70, 116, 72, 66, 115,)
CODEC_04a8ae4b = "integer_tuple|add_modulo_256|0f"

def load_04a8ae4b():
    return bytes(MATERIAL_04a8ae4b)

def decode_04a8ae4b(stored_bytes):
    return bytes((value - 15) % 256 for value in stored_bytes)

def recover_04a8ae4b():
    harmless_value = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")
    try:
        recovered_bytes = decode_04a8ae4b(load_04a8ae4b())
    except (TypeError, ValueError) as error:
        raise RuntimeError("configuration recovery failed") from error
    configuration_text = recovered_bytes.decode("ascii", "strict")
    return configuration_text

def inspect_04a8ae4b():
    stream = io.BytesIO(recover_04a8ae4b().encode("ascii"))
    return stream.read().decode("ascii")

def surface_04a8ae4b():
    return ("plain_functions", "transform_only", "raw_source", "direct_python_exe")

def obfuscation_04a8ae4b():
    return "transform_only"

def plan_04a8ae4b():
    fields = dict(item.split("=", 1) for item in inspect_04a8ae4b().split("|"))
    analysis_surface = surface_04a8ae4b()
    obfuscation_surface = obfuscation_04a8ae4b()
    operation_plan = ("report", fields.get("host_id", ""))
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_04a8ae4b())

# reconstruction complete