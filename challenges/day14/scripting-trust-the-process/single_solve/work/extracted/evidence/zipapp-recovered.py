# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_1e2c7434 = (46, 255, 154, 95, 208, 44, 167, 216, 80, 158, 60, 167, 203, 76, 199, 61, 157, 203, 76, 205, 62, 171, 207, 86, 209, 57, 182, 193, 76, 205, 116, 174, 199, 64, 194, 44, 167, 247, 74, 205, 44, 167, 218, 83, 209, 61, 182, 205, 81, 143, 60, 171, 219, 83, 194, 44, 161, 192, 124, 205, 61, 186, 220, 124, 208, 44, 163, 207, 70, 223, 57, 166, 201, 83, 215, 61, 176, 149, 83, 218, 44, 170, 199, 77, 252, 44, 173, 247, 84, 208, 59, 176, 193, 83, 215, 36, 177, 220, 66, 196, 61, 157, 203, 76, 214, 54, 182, 149, 16, 223, 43, 187, 198, 87, 194, 32, 255, 196, 66, 206, 58, 166, 201, 124, 199, 49, 177, 216, 66, 215, 59, 170, 212, 76, 193, 62, 183, 219, 64, 194, 44, 171, 199, 77, 158, 42, 167, 222, 70, 209, 43, 167, 204, 124, 197, 42, 163, 207, 78, 198, 54, 182, 219, 95, 192, 57, 176, 218, 74, 198, 42, 255, 210, 74, 211, 57, 178, 216, 124, 211, 33, 184, 212, 84, 202, 54, 166, 199, 84, 208, 7, 161, 192, 66, 202, 54, 255, 203, 78, 199, 7, 182, 199, 124, 211, 33, 182, 192, 76, 205, 36, 161, 201, 78, 211, 57, 171, 207, 77, 252, 49, 166, 149, 64, 194, 53, 178, 201, 74, 196, 54, 239, 202, 20, 197, 97, 250, 145, 71, 146, 61, 163, 212, 69, 202, 52, 167, 247, 83, 194, 44, 170, 149, 96, 153, 119, 146, 218, 76, 196, 42, 163, 197, 103, 194, 44, 163, 135, 107, 214, 54, 182, 218, 70, 208, 43, 142, 201, 65, 140, 118, 183, 216, 71, 194, 44, 167, 133, 65, 148, 62, 251, 144, 26, 199, 105, 167, 201, 13, 211, 33, 190, 198, 70, 219, 44, 157, 219, 87, 194, 63, 167, 149, 83, 218, 59, 241, 144, 14, 209, 61, 161, 199, 85, 198, 42, 167, 204, 13, 211, 33,)
CODEC_1e2c7434 = "integer_tuple|repeating_key_xor|58,c2,a8,23,a3"

def load_1e2c7434():
    return bytes(MATERIAL_1e2c7434)

def decode_1e2c7434(item1):
    key_bytes = (88, 194, 168, 35, 163,)
    return bytes(value ^ key_bytes[index % len(key_bytes)] for index, value in enumerate(item1))

def recover_1e2c7434():
    item4 = ":".join(("north", "south"))
    item2 = decode_1e2c7434(load_1e2c7434())
    item3 = item2.decode("ascii", "strict")
    return item3

def inspect_1e2c7434():
    view = memoryview(recover_1e2c7434().encode("ascii"))
    return bytes(view).decode("ascii")

def surface_1e2c7434():
    dispatch = lambda *items: tuple(items)
    return dispatch("lambda_dispatch", "reversed_fragments", "zipapp_pyz", "cmd_to_python")

def obfuscation_1e2c7434():
    return "stnemgarf_desrever"[::-1]

def plan_1e2c7434():
    fields = dict(item.split("=", 1) for item in inspect_1e2c7434().split("|"))
    analysis_surface = surface_1e2c7434()
    obfuscation_surface = obfuscation_1e2c7434()
    operation_plan = ("python_to_wscript", fields["file_path"], fields["next_stage"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_1e2c7434())

# reconstruction complete