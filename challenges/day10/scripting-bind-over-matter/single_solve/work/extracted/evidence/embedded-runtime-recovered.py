#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_3e778bc8 = [159, 212, 219, 149, 154, 157, 140, 153, 154, 212, 141, 140, 138, 134, 141, 140, 182, 138, 134, 135, 143, 128, 142, 156, 155, 136, 157, 128, 134, 135, 197, 133, 134, 138, 136, 157, 140, 182, 128, 135, 157, 140, 155, 153, 155, 140, 157, 140, 155, 197, 141, 128, 154, 153, 136, 157, 138, 129, 182, 135, 140, 145, 157, 182, 154, 157, 136, 142, 140, 149, 136, 141, 136, 153, 157, 140, 155, 212, 153, 144, 157, 129, 134, 135, 182, 157, 134, 182, 138, 132, 141, 149, 154, 157, 136, 142, 140, 182, 138, 134, 156, 135, 157, 212, 218, 149, 154, 144, 135, 157, 136, 145, 212, 138, 133, 136, 154, 154, 182, 154, 157, 136, 157, 128, 138, 132, 140, 157, 129, 134, 141, 149, 134, 139, 143, 156, 154, 138, 136, 157, 128, 134, 135, 212, 132, 136, 155, 154, 129, 136, 133, 182, 140, 135, 159, 140, 133, 134, 153, 140, 182, 153, 133, 136, 135, 149, 138, 136, 155, 155, 128, 140, 155, 212, 140, 132, 139, 140, 141, 141, 136, 139, 133, 140, 182, 153, 144, 157, 129, 134, 135, 182, 155, 156, 135, 157, 128, 132, 140, 149, 158, 128, 135, 141, 134, 158, 154, 182, 138, 129, 136, 128, 135, 212, 155, 140, 135, 136, 132, 140, 141, 182, 128, 135, 157, 140, 155, 153, 155, 140, 157, 140, 155, 149, 138, 136, 132, 153, 136, 128, 142, 135, 182, 128, 141, 212, 138, 136, 132, 153, 136, 128, 142, 135, 196, 216, 222, 218, 208, 216, 218, 141, 140, 217, 138, 149, 143, 128, 133, 140, 182, 153, 136, 157, 129, 212, 170, 211, 198, 185, 155, 134, 142, 155, 136, 132, 173, 136, 157, 136, 198, 161, 156, 135, 157, 155, 140, 154, 154, 165, 136, 139, 198, 199, 156, 153, 141, 136, 157, 140, 196, 216, 222, 218, 208, 216, 218, 141, 140, 217, 138, 199, 153, 144, 149, 135, 140, 145, 157, 182, 154, 157, 136, 142, 140, 212, 153, 144, 136, 155, 132, 134, 155, 196, 153, 144, 128, 135, 154, 157, 136, 133, 133, 140, 155, 196, 155, 140, 138, 134, 159, 140, 155, 140, 141, 199, 153, 144]
CODEC_3e778bc8 = "reversed_integer_list|reverse_then_xor|e9"

def load_3e778bc8():
    return bytes(reversed(MATERIAL_3e778bc8))

def decode_3e778bc8(e):
    return bytes(value ^ 233 for value in reversed(e))

def recover_3e778bc8():
    n = "left" if 2 > 1 else "right"
    f = decode_3e778bc8
    d = f(load_3e778bc8())
    t = d.decode("ascii", "strict")
    return t

def inspect_3e778bc8():
    view = memoryview(recover_3e778bc8().encode("ascii"))
    return bytes(view).decode("ascii")

class Surface_surface_3e778bc8:
    @staticmethod
    def recover():
        return ("class_staticmethod", "marshal_envelope_plan", "embeddable_python_runtime", "renamed_interpreter")

def surface_3e778bc8():
    return Surface_surface_3e778bc8.recover()

def obfuscation_3e778bc8():
    marshal_plan = {"format": "code_object", "action": "inspect_only", "label": "marshal_envelope_plan"}
    return marshal_plan["label"]

def plan_3e778bc8():
    fields = dict(item.split("=", 1) for item in inspect_3e778bc8().split("|"))
    analysis_surface = surface_3e778bc8()
    obfuscation_surface = obfuscation_3e778bc8()
    operation_plan = ("python_to_cmd", fields["file_path"], fields["next_stage"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_3e778bc8())
