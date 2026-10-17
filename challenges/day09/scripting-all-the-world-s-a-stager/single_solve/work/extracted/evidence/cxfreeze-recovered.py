# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_be5fcdb8 = "88:4f:44:8e:85:86:77:82:85:4f:85:77:7e:77:75:86:71:78:7b:8a:86:87:84:77:71:78:7b:7e:77:85:3e:86:84:73:80:85:78:81:84:7f:71:75:81:82:8b:3e:89:84:7b:86:77:71:84:77:75:81:88:77:84:8b:71:80:81:86:77:8e:73:76:73:82:86:77:84:4f:81:85:71:89:73:7e:7d:71:75:81:82:8b:71:82:7e:73:80:8e:85:86:73:79:77:71:75:81:87:80:86:4f:43:8e:85:8b:80:86:73:8a:4f:76:77:75:81:84:73:86:81:84:71:89:84:73:82:82:77:84:8e:81:74:78:87:85:75:73:86:7b:81:80:4f:74:8b:86:77:85:71:86:84:73:80:85:7e:73:86:7b:81:80:8e:75:73:84:84:7b:77:84:4f:75:8a:71:78:84:77:77:8c:77:71:77:8a:77:75:87:86:73:74:7e:77:8e:89:7b:80:76:81:89:85:71:75:7a:73:7b:80:4f:85:75:7a:77:76:87:7e:77:76:71:86:73:85:7d:71:76:77:85:75:84:7b:82:86:81:84:8e:75:73:7f:82:73:7b:79:80:71:7b:76:4f:75:73:7f:82:73:7b:79:80:3f:48:48:45:48:4b:48:49:44:76:42:8e:77:8a:86:77:80:85:7b:81:80:4f:40:48:48:45:48:4b:48:49:44:76:42:40:7e:81:75:7d:77:76:8e:80:81:86:77:71:80:73:7f:77:4f:64:57:55:61:68:57:64:3f:48:48:45:48:4b:48:49:44:76:42:40:86:8a:86:8e:86:73:84:79:77:86:71:84:81:81:86:4f:55:4c:41:5a:87:80:86:84:77:85:85:5e:73:74:41:48:48:45:48:4b:48:49:44:76:42"
CODEC_be5fcdb8 = "hex_colon|add_modulo_256|12"

def load_be5fcdb8():
    return bytes.fromhex(MATERIAL_be5fcdb8.replace(":", " "))

def decode_be5fcdb8(EnCoDeD_Bytes):
    return bytes((value - 18) % 256 for value in EnCoDeD_Bytes)

def recover_be5fcdb8():
    NeUtRaL = 19 * 7 - 133
    StAtE = "decode"
    while StAtE != "done":
        if StAtE == "decode":
            DeCoDeD_Bytes = decode_be5fcdb8(load_be5fcdb8())
            StAtE = "done"
    DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")
    return DeScRiPtOr_Text

def inspect_be5fcdb8():
    return recover_be5fcdb8()

def decorate_surface_be5fcdb8(function):
    def wrapped():
        return tuple(function())
    return wrapped

@decorate_surface_be5fcdb8
def surface_be5fcdb8():
    return ("decorator_wrapper", "bytes_translation", "cx_freeze_executable", "scheduled_task_descriptor")

def obfuscation_be5fcdb8():
    return bytes((98, 121, 116, 101, 115, 95, 116, 114, 97, 110, 115, 108, 97, 116, 105, 111, 110)).decode("ascii")

def plan_be5fcdb8():
    fields = dict(item.split("=", 1) for item in inspect_be5fcdb8().split("|"))
    analysis_surface = surface_be5fcdb8()
    obfuscation_surface = obfuscation_be5fcdb8()
    operation_plan = ("os_walk_copy_plan", fields["target_root"], fields["extension"], fields["note_name"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_be5fcdb8())

# reconstruction complete