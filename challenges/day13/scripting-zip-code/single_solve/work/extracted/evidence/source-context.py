# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_d586475d = (98, 41, 30, 104, 95, 96, 81, 92, 95, 41, 80, 81, 79, 91, 80, 81, 75, 79, 91, 90, 82, 85, 83, 97, 94, 77, 96, 85, 91, 90, 24, 94, 81, 96, 97, 94, 90, 75, 79, 91, 90, 82, 85, 83, 97, 94, 77, 96, 85, 91, 90, 104, 77, 80, 77, 92, 96, 81, 94, 41, 89, 77, 92, 92, 85, 90, 83, 75, 92, 94, 91, 100, 101, 104, 95, 96, 77, 83, 81, 75, 79, 91, 97, 90, 96, 41, 29, 104, 95, 101, 90, 96, 77, 100, 41, 92, 88, 77, 85, 90, 75, 82, 97, 90, 79, 96, 85, 91, 90, 95, 104, 91, 78, 82, 97, 95, 79, 77, 96, 85, 91, 90, 41, 96, 94, 77, 90, 95, 82, 91, 94, 89, 75, 91, 90, 88, 101, 104, 79, 77, 94, 94, 85, 81, 94, 41, 94, 77, 99, 75, 95, 91, 97, 94, 79, 81, 104, 99, 85, 90, 80, 91, 99, 95, 75, 79, 84, 77, 85, 90, 41, 80, 85, 94, 81, 79, 96, 75, 92, 101, 96, 84, 91, 90, 75, 81, 100, 81, 104, 79, 77, 89, 92, 77, 85, 83, 90, 75, 85, 80, 41, 79, 77, 89, 92, 77, 85, 83, 90, 25, 28, 29, 31, 80, 37, 29, 34, 81, 78, 30, 104, 84, 91, 95, 96, 75, 85, 80, 41, 84, 91, 95, 96, 25, 28, 29, 31, 80, 37, 29, 34, 81, 78, 30,)
CODEC_d586475d = "integer_tuple|subtract_modulo_256|14"

def load_d586475d():
    return bytes(MATERIAL_d586475d)

def decode_d586475d(stored_bytes):
    return bytes((value + 20) % 256 for value in stored_bytes)

def recover_d586475d():
    harmless_value = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")
    try:
        recovered_bytes = decode_d586475d(load_d586475d())
    except (TypeError, ValueError) as error:
        raise RuntimeError("configuration recovery failed") from error
    configuration_text = recovered_bytes.decode("ascii", "strict")
    return configuration_text

def inspect_d586475d():
    view = memoryview(recover_d586475d().encode("ascii"))
    return bytes(view).decode("ascii")

def surface_d586475d():
    return ("plain_functions", "transform_only", "raw_source", "direct_python_exe")

def obfuscation_d586475d():
    return "transform_only"

def plan_d586475d():
    fields = dict(item.split("=", 1) for item in inspect_d586475d().split("|"))
    analysis_surface = surface_d586475d()
    obfuscation_surface = obfuscation_d586475d()
    operation_plan = ("report", fields.get("host_id", ""))
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_d586475d())

# reconstruction complete