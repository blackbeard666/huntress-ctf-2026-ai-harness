# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_4d81e13e = (118, 61, 50, 124, 115, 116, 101, 112, 115, 61, 100, 101, 99, 111, 100, 101, 95, 99, 111, 110, 102, 105, 103, 117, 114, 97, 116, 105, 111, 110, 44, 108, 111, 99, 97, 116, 101, 95, 105, 110, 116, 101, 114, 112, 114, 101, 116, 101, 114, 44, 100, 105, 115, 112, 97, 116, 99, 104, 95, 110, 101, 120, 116, 95, 115, 116, 97, 103, 101, 124, 97, 100, 97, 112, 116, 101, 114, 61, 112, 121, 116, 104, 111, 110, 95, 116, 111, 95, 112, 121, 116, 104, 111, 110, 124, 115, 116, 97, 103, 101, 95, 99, 111, 117, 110, 116, 61, 51, 124, 115, 121, 110, 116, 97, 120, 61, 99, 108, 97, 115, 115, 95, 115, 116, 97, 116, 105, 99, 109, 101, 116, 104, 111, 100, 124, 111, 98, 102, 117, 115, 99, 97, 116, 105, 111, 110, 61, 109, 97, 114, 115, 104, 97, 108, 95, 101, 110, 118, 101, 108, 111, 112, 101, 95, 112, 108, 97, 110, 124, 99, 97, 114, 114, 105, 101, 114, 61, 101, 109, 98, 101, 100, 100, 97, 98, 108, 101, 95, 112, 121, 116, 104, 111, 110, 95, 114, 117, 110, 116, 105, 109, 101, 124, 119, 105, 110, 100, 111, 119, 115, 95, 99, 104, 97, 105, 110, 61, 114, 101, 110, 97, 109, 101, 100, 95, 105, 110, 116, 101, 114, 112, 114, 101, 116, 101, 114, 124, 99, 97, 109, 112, 97, 105, 103, 110, 95, 105, 100, 61, 99, 97, 109, 112, 97, 105, 103, 110, 45, 97, 99, 55, 50, 54, 51, 52, 52, 54, 53, 124, 102, 105, 108, 101, 95, 112, 97, 116, 104, 61, 67, 58, 47, 80, 114, 111, 103, 114, 97, 109, 68, 97, 116, 97, 47, 72, 117, 110, 116, 114, 101, 115, 115, 76, 97, 98, 47, 46, 117, 112, 100, 97, 116, 101, 45, 97, 99, 55, 50, 54, 51, 52, 52, 54, 53, 46, 112, 121, 124, 110, 101, 120, 116, 95, 115, 116, 97, 103, 101, 61, 112, 121, 97, 114, 109, 111, 114, 45, 112, 121, 105, 110, 115, 116, 97, 108, 108, 101, 114, 45, 114, 101, 99, 111, 118, 101, 114, 101, 100, 46, 112, 121,)
CODEC_4d81e13e = "integer_tuple|identity|"

def load_4d81e13e():
    return bytes(MATERIAL_4d81e13e)

def decode_4d81e13e(item1):
    return bytes(item1)

def recover_4d81e13e():
    item4 = ":".join(("north", "south"))
    _pass = 0
    while _pass < 1:
        item2 = decode_4d81e13e(load_4d81e13e())
        _pass += 1
    item3 = item2.decode("ascii", "strict")
    return item3

def inspect_4d81e13e():
    return recover_4d81e13e()

class Surface_surface_4d81e13e:
    @staticmethod
    def recover():
        return ("class_staticmethod", "marshal_envelope_plan", "embeddable_python_runtime", "renamed_interpreter")

def surface_4d81e13e():
    return Surface_surface_4d81e13e.recover()

def obfuscation_4d81e13e():
    marshal_plan = {"format": "code_object", "action": "inspect_only", "label": "marshal_envelope_plan"}
    return marshal_plan["label"]

def plan_4d81e13e():
    fields = dict(item.split("=", 1) for item in inspect_4d81e13e().split("|"))
    analysis_surface = surface_4d81e13e()
    obfuscation_surface = obfuscation_4d81e13e()
    operation_plan = ("python_to_python", fields["file_path"], fields["next_stage"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_4d81e13e())

# reconstruction complete