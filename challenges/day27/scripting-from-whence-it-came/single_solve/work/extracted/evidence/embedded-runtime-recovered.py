# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_9ee01f6d = "226,235,181,255,254,233,254,237,244,248,254,233,182,233,254,247,247,250,239,232,245,242,226,235,182,233,244,246,233,250,226,235,166,254,252,250,239,232,196,239,227,254,245,231,226,235,181,175,162,162,163,173,249,169,168,172,174,182,254,239,250,255,235,238,181,180,249,250,215,232,232,254,233,239,245,238,211,180,250,239,250,223,246,250,233,252,244,233,203,180,161,216,166,243,239,250,235,196,254,247,242,253,231,175,162,162,163,173,249,169,168,172,174,182,245,252,242,250,235,246,250,248,166,255,242,196,245,252,242,250,235,246,250,248,231,233,254,239,254,233,235,233,254,239,245,242,196,255,254,246,250,245,254,233,166,245,242,250,243,248,196,232,236,244,255,245,242,236,231,254,246,242,239,245,238,233,196,245,244,243,239,226,235,196,254,247,249,250,255,255,254,249,246,254,166,233,254,242,233,233,250,248,231,245,250,247,235,196,254,235,244,247,254,237,245,254,196,247,250,243,232,233,250,246,166,245,244,242,239,250,248,232,238,253,249,244,231,255,244,243,239,254,246,248,242,239,250,239,232,196,232,232,250,247,248,166,227,250,239,245,226,232,231,168,166,239,245,238,244,248,196,254,252,250,239,232,231,239,235,242,233,248,232,236,196,244,239,196,245,244,243,239,226,235,166,233,254,239,235,250,255,250,231,254,252,250,239,232,196,239,227,254,245,196,243,248,239,250,235,232,242,255,183,233,254,239,254,233,235,233,254,239,245,242,196,254,239,250,248,244,247,183,245,244,242,239,250,233,238,252,242,253,245,244,248,196,254,255,244,248,254,255,166,232,235,254,239,232,231,169,166,237"
CODEC_9ee01f6d = "decimal_csv|reverse_then_xor|9b"

def load_9ee01f6d():
    return bytes(int(item) for item in MATERIAL_9ee01f6d.split(","))

def decode_9ee01f6d(stored_bytes):
    return bytes(value ^ 155 for value in reversed(stored_bytes))

def recover_9ee01f6d():
    harmless_value = 19 * 7 - 133
    _pass = 0
    while _pass < 1:
        recovered_bytes = decode_9ee01f6d(load_9ee01f6d())
        _pass += 1
    configuration_text = recovered_bytes.decode("ascii", "strict")
    return configuration_text

def inspect_9ee01f6d():
    view = memoryview(recover_9ee01f6d().encode("ascii"))
    return bytes(view).decode("ascii")

class Surface_surface_9ee01f6d:
    @staticmethod
    def recover():
        return ("class_staticmethod", "marshal_envelope_plan", "embeddable_python_runtime", "renamed_interpreter")

def surface_9ee01f6d():
    return Surface_surface_9ee01f6d.recover()

def obfuscation_9ee01f6d():
    marshal_plan = {"format": "code_object", "action": "inspect_only", "label": "marshal_envelope_plan"}
    return marshal_plan["label"]

def plan_9ee01f6d():
    fields = dict(item.split("=", 1) for item in inspect_9ee01f6d().split("|"))
    analysis_surface = surface_9ee01f6d()
    obfuscation_surface = obfuscation_9ee01f6d()
    operation_plan = ("python_to_wscript", fields["file_path"], fields["next_stage"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_9ee01f6d())

# reconstruction complete