#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_1740883e = (226, 165, 169, 199, 87, 224, 253, 235, 200, 25, 240, 253, 248, 212, 64, 241, 199, 248, 212, 74, 242, 241, 252, 206, 86, 245, 236, 242, 212, 74, 184, 244, 244, 216, 69, 224, 253, 196, 210, 74, 224, 253, 233, 203, 86, 241, 236, 254, 201, 8, 240, 241, 232, 203, 69, 224, 251, 243, 228, 74, 241, 224, 239, 228, 87, 224, 249, 252, 222, 88, 245, 252, 250, 203, 80, 241, 234, 166, 203, 93, 224, 240, 244, 213, 123, 224, 247, 196, 203, 93, 224, 240, 244, 213, 88, 231, 236, 250, 220, 65, 203, 251, 244, 206, 74, 224, 165, 168, 199, 87, 237, 246, 239, 218, 92, 169, 251, 247, 218, 87, 231, 199, 232, 207, 69, 224, 241, 248, 214, 65, 224, 240, 244, 223, 88, 251, 250, 253, 206, 87, 247, 249, 239, 210, 75, 250, 165, 246, 218, 86, 231, 240, 250, 215, 123, 241, 246, 237, 222, 72, 251, 232, 254, 228, 84, 248, 249, 245, 199, 71, 245, 234, 233, 210, 65, 230, 165, 254, 214, 70, 241, 252, 255, 218, 70, 248, 253, 196, 203, 93, 224, 240, 244, 213, 123, 230, 237, 245, 207, 77, 249, 253, 231, 204, 77, 250, 252, 244, 204, 87, 203, 251, 243, 218, 77, 250, 165, 233, 222, 74, 245, 245, 254, 223, 123, 253, 246, 239, 222, 86, 228, 234, 254, 207, 65, 230, 228, 248, 218, 73, 228, 249, 242, 220, 74, 203, 241, 255, 134, 71, 245, 245, 235, 218, 77, 243, 246, 182, 142, 22, 165, 173, 175, 139, 23, 162, 175, 175, 199, 66, 253, 244, 254, 228, 84, 245, 236, 243, 134, 103, 174, 183, 203, 201, 75, 243, 234, 250, 214, 96, 245, 236, 250, 148, 108, 225, 246, 239, 201, 65, 231, 235, 215, 218, 70, 187, 182, 238, 203, 64, 245, 236, 254, 150, 17, 166, 169, 174, 143, 20, 167, 174, 172, 143, 10, 228, 225, 231, 213, 65, 236, 236, 196, 200, 80, 245, 255, 254, 134, 84, 237, 249, 233, 214, 75, 230, 181, 235, 194, 77, 250, 235, 239, 218, 72, 248, 253, 233, 150, 86, 241, 251, 244, 205, 65, 230, 253, 255, 149, 84, 237,)
CODEC_1740883e = "integer_tuple|repeating_key_xor|94,98,9b,bb,24"

def load_1740883e():
    return bytes(MATERIAL_1740883e)

def decode_1740883e(e):
    key_bytes = (148, 152, 155, 187, 36,)
    return bytes(value ^ key_bytes[index % len(key_bytes)] for index, value in enumerate(e))

def recover_1740883e():
    n = "left" if 2 > 1 else "right"
    try:
        d = decode_1740883e(load_1740883e())
    except (TypeError, ValueError) as error:
        raise RuntimeError("configuration recovery failed") from error
    t = d.decode("ascii", "strict")
    return t

def inspect_1740883e():
    stream = io.BytesIO(recover_1740883e().encode("ascii"))
    return stream.read().decode("ascii")

class Surface_surface_1740883e:
    @staticmethod
    def recover():
        return ("class_staticmethod", "marshal_envelope_plan", "embeddable_python_runtime", "renamed_interpreter")

def surface_1740883e():
    return Surface_surface_1740883e.recover()

def obfuscation_1740883e():
    marshal_plan = {"format": "code_object", "action": "inspect_only", "label": "marshal_envelope_plan"}
    return marshal_plan["label"]

def plan_1740883e():
    fields = dict(item.split("=", 1) for item in inspect_1740883e().split("|"))
    analysis_surface = surface_1740883e()
    obfuscation_surface = obfuscation_1740883e()
    operation_plan = ("python_to_python", fields["file_path"], fields["next_stage"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_1740883e())
