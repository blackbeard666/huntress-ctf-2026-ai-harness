#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_1c6d89a2 = [158, 213, 218, 148, 155, 156, 141, 152, 155, 213, 137, 139, 153, 157, 129, 154, 141, 183, 154, 141, 133, 135, 156, 141, 196, 159, 154, 129, 156, 141, 183, 142, 129, 132, 141, 148, 137, 140, 137, 152, 156, 141, 154, 213, 157, 154, 132, 132, 129, 138, 183, 156, 135, 183, 152, 137, 156, 128, 148, 155, 156, 137, 143, 141, 183, 139, 135, 157, 134, 156, 213, 217, 148, 155, 145, 134, 156, 137, 144, 213, 143, 141, 134, 141, 154, 137, 156, 135, 154, 183, 152, 129, 152, 141, 132, 129, 134, 141, 148, 135, 138, 142, 157, 155, 139, 137, 156, 129, 135, 134, 213, 142, 155, 156, 154, 129, 134, 143, 183, 142, 154, 137, 143, 133, 141, 134, 156, 155, 148, 139, 137, 154, 154, 129, 141, 154, 213, 152, 145, 129, 134, 155, 156, 137, 132, 132, 141, 154, 183, 135, 134, 141, 142, 129, 132, 141, 148, 159, 129, 134, 140, 135, 159, 155, 183, 139, 128, 137, 129, 134, 213, 133, 155, 128, 156, 137, 183, 156, 135, 183, 152, 145, 156, 128, 135, 134, 148, 139, 137, 133, 152, 137, 129, 143, 134, 183, 129, 140, 213, 139, 137, 133, 152, 137, 129, 143, 134, 197, 219, 217, 140, 141, 217, 223, 223, 220, 138, 221, 148, 157, 154, 132, 213, 128, 156, 156, 152, 155, 210, 199, 199, 219, 217, 140, 141, 217, 223, 223, 220, 138, 221, 198, 141, 144, 137, 133, 152, 132, 141, 198, 129, 134, 158, 137, 132, 129, 140, 199, 220, 141, 140, 219, 137, 139, 141, 209, 198, 152, 145, 148, 157, 155, 141, 154, 183, 137, 143, 141, 134, 156, 213, 160, 157, 134, 156, 154, 141, 155, 155, 184, 145, 156, 128, 135, 134, 199, 219, 217, 140, 141, 217, 223, 223, 220, 138, 221, 148, 142, 129, 132, 141, 183, 152, 137, 156, 128, 213, 171, 210, 199, 184, 154, 135, 143, 154, 137, 133, 172, 137, 156, 137, 199, 160, 157, 134, 156, 154, 141, 155, 155, 164, 137, 138, 199, 198, 157, 152, 140, 137, 156, 141, 197, 219, 217, 140, 141, 217, 223, 223, 220, 138, 221, 198, 152, 145]
CODEC_1c6d89a2 = "reversed_integer_list|reverse_then_xor|e8"

def load_1c6d89a2():
    return bytes(reversed(MATERIAL_1c6d89a2))

def decode_1c6d89a2(item1):
    return bytes(value ^ 232 for value in reversed(item1))

def recover_1c6d89a2():
    item4 = (3, 5, 8, 13)[1:3]
    item7 = "decode"
    while item7 != "done":
        if item7 == "decode":
            item2 = decode_1c6d89a2(load_1c6d89a2())
            item7 = "done"
    item3 = item2.decode("ascii", "strict")
    return item3

def inspect_1c6d89a2():
    stream = io.BytesIO(recover_1c6d89a2().encode("ascii"))
    return stream.read().decode("ascii")

def surface_1c6d89a2():
    stream = (item for item in ("generator_pipeline", "fstring_fragments", "pyinstaller_onefile", "mshta_to_python"))
    return tuple(stream)

def obfuscation_1c6d89a2():
    left, right = "fstrin", "g_fragments"
    return f"{left}{right}"

def plan_1c6d89a2():
    fields = dict(item.split("=", 1) for item in inspect_1c6d89a2().split("|"))
    analysis_surface = surface_1c6d89a2()
    obfuscation_surface = obfuscation_1c6d89a2()
    operation_plan = ("urllib_to_path", fields["url"], fields["file_path"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_1c6d89a2())
