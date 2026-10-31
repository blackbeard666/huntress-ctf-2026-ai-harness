#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_af71e14f = [67, 8, 7, 73, 70, 65, 80, 69, 70, 8, 81, 80, 86, 90, 81, 80, 106, 86, 90, 91, 83, 92, 82, 64, 71, 84, 65, 92, 90, 91, 25, 89, 90, 86, 84, 65, 80, 106, 92, 91, 65, 80, 71, 69, 71, 80, 65, 80, 71, 25, 81, 92, 70, 69, 84, 65, 86, 93, 106, 91, 80, 77, 65, 106, 70, 65, 84, 82, 80, 73, 84, 81, 84, 69, 65, 80, 71, 8, 69, 76, 65, 93, 90, 91, 106, 65, 90, 106, 69, 90, 66, 80, 71, 70, 93, 80, 89, 89, 73, 70, 65, 84, 82, 80, 106, 86, 90, 64, 91, 65, 8, 6, 73, 70, 76, 91, 65, 84, 77, 8, 89, 84, 88, 87, 81, 84, 106, 81, 92, 70, 69, 84, 65, 86, 93, 73, 90, 87, 83, 64, 70, 86, 84, 65, 92, 90, 91, 8, 71, 80, 67, 80, 71, 70, 80, 81, 106, 83, 71, 84, 82, 88, 80, 91, 65, 70, 73, 86, 84, 71, 71, 92, 80, 71, 8, 79, 92, 69, 84, 69, 69, 106, 69, 76, 79, 73, 66, 92, 91, 81, 90, 66, 70, 106, 86, 93, 84, 92, 91, 8, 86, 88, 81, 106, 65, 90, 106, 69, 76, 65, 93, 90, 91, 73, 86, 84, 88, 69, 84, 92, 82, 91, 106, 92, 81, 8, 86, 84, 88, 69, 84, 92, 82, 91, 24, 87, 12, 4, 13, 84, 84, 84, 87, 80, 0, 73, 83, 92, 89, 80, 106, 69, 84, 65, 93, 8, 118, 15, 26, 101, 71, 90, 82, 71, 84, 88, 113, 84, 65, 84, 26, 125, 64, 91, 65, 71, 80, 70, 70, 121, 84, 87, 26, 27, 64, 69, 81, 84, 65, 80, 24, 87, 12, 4, 13, 84, 84, 84, 87, 80, 0, 27, 69, 76, 73, 91, 80, 77, 65, 106, 70, 65, 84, 82, 80, 8, 69, 76, 86, 6, 13, 24, 71, 80, 86, 90, 67, 80, 71, 80, 81, 27, 69, 76]
CODEC_af71e14f = "integer_list|single_byte_xor|35"

def load_af71e14f():
    return bytes(MATERIAL_af71e14f)

def decode_af71e14f(e):
    return bytes(value ^ 53 for value in e)

def recover_af71e14f():
    n = (3, 5, 8, 13)[1:3]
    for _pass in range(1):
        d = decode_af71e14f(load_af71e14f())
    t = d.decode("ascii", "strict")
    return t

def inspect_af71e14f():
    stream = io.BytesIO(recover_af71e14f().encode("ascii"))
    return stream.read().decode("ascii")

def surface_af71e14f():
    dispatch = lambda *items: tuple(items)
    return dispatch("lambda_dispatch", "reversed_fragments", "zipapp_pyz", "cmd_to_python")

def obfuscation_af71e14f():
    return "stnemgarf_desrever"[::-1]

def plan_af71e14f():
    fields = dict(item.split("=", 1) for item in inspect_af71e14f().split("|"))
    analysis_surface = surface_af71e14f()
    obfuscation_surface = obfuscation_af71e14f()
    operation_plan = ("python_to_powershell", fields["file_path"], fields["next_stage"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_af71e14f())
