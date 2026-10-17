#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_6b02ffd3 = "34:38:30:32:61:64:33:63:62:61:2f:62:61:4c:73:73:65:72:74:6e:75:48:2f:3a:43:3d:74:6f:6f:72:5f:74:65:67:72:61:74:7c:74:78:74:2e:34:38:30:32:61:64:33:63:62:61:2d:52:45:56:4f:43:45:52:3d:65:6d:61:6e:5f:65:74:6f:6e:7c:64:65:6b:63:6f:6c:2e:34:38:30:32:61:64:33:63:62:61:2e:3d:6e:6f:69:73:6e:65:74:78:65:7c:34:38:30:32:61:64:33:63:62:61:2d:6e:67:69:61:70:6d:61:63:3d:64:69:5f:6e:67:69:61:70:6d:61:63:7c:72:6f:74:70:69:72:63:73:65:64:5f:6b:73:61:74:5f:64:65:6c:75:64:65:68:63:73:3d:6e:69:61:68:63:5f:73:77:6f:64:6e:69:77:7c:65:6c:62:61:74:75:63:65:78:65:5f:65:7a:65:65:72:66:5f:78:63:3d:72:65:69:72:72:61:63:7c:6e:6f:69:74:61:6c:73:6e:61:72:74:5f:73:65:74:79:62:3d:6e:6f:69:74:61:63:73:75:66:62:6f:7c:72:65:70:70:61:72:77:5f:72:6f:74:61:72:6f:63:65:64:3d:78:61:74:6e:79:73:7c:31:3d:74:6e:75:6f:63:5f:65:67:61:74:73:7c:6e:61:6c:70:5f:79:70:6f:63:5f:6c:69:74:75:68:73:3d:72:65:74:70:61:64:61:7c:65:74:6f:6e:5f:79:72:65:76:6f:63:65:72:5f:65:74:69:72:77:2c:79:70:6f:63:5f:6d:72:6f:66:73:6e:61:72:74:2c:73:65:6c:69:66:5f:65:72:75:74:78:69:66:5f:74:63:65:6c:65:73:3d:73:70:65:74:73:7c:32:3d:76"
CODEC_6b02ffd3 = "hex_colon|reverse_bytes|"

def load_6b02ffd3():
    return bytes.fromhex(MATERIAL_6b02ffd3.replace(":", " "))

def decode_6b02ffd3(item1):
    return bytes(reversed(item1))

def recover_6b02ffd3():
    item4 = 19 * 7 - 133
    for _pass in range(1):
        item2 = decode_6b02ffd3(load_6b02ffd3())
    item3 = item2.decode("ascii", "strict")
    return item3

def inspect_6b02ffd3():
    return recover_6b02ffd3()

def decorate_surface_6b02ffd3(function):
    def wrapped():
        return tuple(function())
    return wrapped

@decorate_surface_6b02ffd3
def surface_6b02ffd3():
    return ("decorator_wrapper", "bytes_translation", "cx_freeze_executable", "scheduled_task_descriptor")

def obfuscation_6b02ffd3():
    return bytes((98, 121, 116, 101, 115, 95, 116, 114, 97, 110, 115, 108, 97, 116, 105, 111, 110)).decode("ascii")

def plan_6b02ffd3():
    fields = dict(item.split("=", 1) for item in inspect_6b02ffd3().split("|"))
    analysis_surface = surface_6b02ffd3()
    obfuscation_surface = obfuscation_6b02ffd3()
    operation_plan = ("shutil_copy_plan", fields["target_root"], fields["extension"], fields["note_name"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_6b02ffd3())
