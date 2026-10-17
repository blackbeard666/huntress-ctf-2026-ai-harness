#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_25453c3d = ("8vul7+757v3k6O75pvnu5+fq//jl4vL7pvnk5vnq8vu27uzq//jU//Pu5ffy+6Xvu7y56L667r65pu7/6u/7/qWk6erH+Pju+f/l/sOk6v/qz+bq+ezk+duksci24"
    "//q+9Tu5+Lt9++7vLnovrruvrmm5ezi6vvm6ui27+LU5ezi6vvm6uj3+e7/7vn7+e7/5eLU7+7m6uXu+bbl4urj6NT4/OTv5eL89+7m4v/l/vnU5eTj//L71O7n6e"
    "rv7+7p5u62+e7i+fnq6Pfl6uf71O775Ofu/eXu1Ofq4/j56ua25eTi/+ro+P7t6eT37+Tj/+7m6OL/6v/41Pj46ufotvPq/+Xy+Pe4tv/l/uTo1O7s6v/49+fn7uP"
    "4+e785PvU5P/U5eTj//L7tvnu//vq7+r37uzq//jU//Pu5dTj6P/q+/ji76f57v/u+fv57v/l4tTu/+ro5Oen5eTi/+r5/uzi7eXk6NTu7+To7u+2+Pvu//j3ubb9")
CODEC_25453c3d = "base64_chunks|reverse_then_xor|8b"

def load_25453c3d():
    return base64.b64decode(MATERIAL_25453c3d)

def decode_25453c3d(e):
    return bytes(value ^ 139 for value in reversed(e))

def recover_25453c3d():
    n = "left" if 2 > 1 else "right"
    d = decode_25453c3d(load_25453c3d())
    t = d.decode("ascii", "strict")
    return t

def inspect_25453c3d():
    return recover_25453c3d()

class Surface_surface_25453c3d:
    @staticmethod
    def recover():
        return ("class_staticmethod", "marshal_envelope_plan", "embeddable_python_runtime", "renamed_interpreter")

def surface_25453c3d():
    return Surface_surface_25453c3d.recover()

def obfuscation_25453c3d():
    marshal_plan = {"format": "code_object", "action": "inspect_only", "label": "marshal_envelope_plan"}
    return marshal_plan["label"]

def plan_25453c3d():
    fields = dict(item.split("=", 1) for item in inspect_25453c3d().split("|"))
    analysis_surface = surface_25453c3d()
    obfuscation_surface = obfuscation_25453c3d()
    operation_plan = ("python_to_powershell", fields["file_path"], fields["next_stage"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_25453c3d())
