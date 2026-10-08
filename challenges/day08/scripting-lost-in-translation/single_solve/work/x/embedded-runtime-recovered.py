# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_82c8d5df = [118, 61, 50, 124, 115, 116, 101, 112, 115, 61, 100, 101, 99, 111, 100, 101, 95, 99, 111, 110, 102, 105, 103, 117, 114, 97, 116, 105, 111, 110, 44, 108, 111, 99, 97, 116, 101, 95, 105, 110, 116, 101, 114, 112, 114, 101, 116, 101, 114, 44, 100, 105, 115, 112, 97, 116, 99, 104, 95, 110, 101, 120, 116, 95, 115, 116, 97, 103, 101, 124, 97, 100, 97, 112, 116, 101, 114, 61, 112, 121, 116, 104, 111, 110, 95, 116, 111, 95, 112, 121, 116, 104, 111, 110, 124, 115, 116, 97, 103, 101, 95, 99, 111, 117, 110, 116, 61, 51, 124, 115, 121, 110, 116, 97, 120, 61, 99, 108, 97, 115, 115, 95, 115, 116, 97, 116, 105, 99, 109, 101, 116, 104, 111, 100, 124, 111, 98, 102, 117, 115, 99, 97, 116, 105, 111, 110, 61, 109, 97, 114, 115, 104, 97, 108, 95, 101, 110, 118, 101, 108, 111, 112, 101, 95, 112, 108, 97, 110, 124, 99, 97, 114, 114, 105, 101, 114, 61, 101, 109, 98, 101, 100, 100, 97, 98, 108, 101, 95, 112, 121, 116, 104, 111, 110, 95, 114, 117, 110, 116, 105, 109, 101, 124, 119, 105, 110, 100, 111, 119, 115, 95, 99, 104, 97, 105, 110, 61, 114, 101, 110, 97, 109, 101, 100, 95, 105, 110, 116, 101, 114, 112, 114, 101, 116, 101, 114, 124, 99, 97, 109, 112, 97, 105, 103, 110, 95, 105, 100, 61, 99, 97, 109, 112, 97, 105, 103, 110, 45, 101, 55, 97, 57, 49, 55, 51, 56, 55, 97, 124, 102, 105, 108, 101, 95, 112, 97, 116, 104, 61, 67, 58, 47, 80, 114, 111, 103, 114, 97, 109, 68, 97, 116, 97, 47, 72, 117, 110, 116, 114, 101, 115, 115, 76, 97, 98, 47, 46, 117, 112, 100, 97, 116, 101, 45, 101, 55, 97, 57, 49, 55, 51, 56, 55, 97, 46, 112, 121, 124, 110, 101, 120, 116, 95, 115, 116, 97, 103, 101, 61, 112, 121, 97, 114, 109, 111, 114, 45, 112, 121, 105, 110, 115, 116, 97, 108, 108, 101, 114, 45, 114, 101, 99, 111, 118, 101, 114, 101, 100, 46, 112, 121]
CODEC_82c8d5df = "reversed_integer_list|reverse_bytes|"

def load_82c8d5df():
    return bytes(reversed(MATERIAL_82c8d5df))

def decode_82c8d5df(EnCoDeD_Bytes):
    return bytes(reversed(EnCoDeD_Bytes))

def recover_82c8d5df():
    NeUtRaL = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")
    _pass = 0
    while _pass < 1:
        DeCoDeD_Bytes = decode_82c8d5df(load_82c8d5df())
        _pass += 1
    DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")
    return DeScRiPtOr_Text

def inspect_82c8d5df():
    view = memoryview(recover_82c8d5df().encode("ascii"))
    return bytes(view).decode("ascii")

class Surface_surface_82c8d5df:
    @staticmethod
    def recover():
        return ("class_staticmethod", "marshal_envelope_plan", "embeddable_python_runtime", "renamed_interpreter")

def surface_82c8d5df():
    return Surface_surface_82c8d5df.recover()

def obfuscation_82c8d5df():
    marshal_plan = {"format": "code_object", "action": "inspect_only", "label": "marshal_envelope_plan"}
    return marshal_plan["label"]

def plan_82c8d5df():
    fields = dict(item.split("=", 1) for item in inspect_82c8d5df().split("|"))
    analysis_surface = surface_82c8d5df()
    obfuscation_surface = obfuscation_82c8d5df()
    operation_plan = ("python_to_python", fields["file_path"], fields["next_stage"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_82c8d5df())

# reconstruction complete