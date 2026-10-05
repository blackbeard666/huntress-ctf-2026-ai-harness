#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_f8d19db6 = "7b:30:3f:71:7e:79:68:7d:7e:30:6c:6e:7c:78:64:7f:68:52:7f:68:60:62:79:68:21:7a:7f:64:79:68:52:6b:64:61:68:71:6c:69:6c:7d:79:68:7f:30:65:79:79:7d:52:6e:61:64:68:63:79:52:79:62:52:7d:6c:79:65:71:7e:79:6c:6a:68:52:6e:62:78:63:79:30:3c:71:7e:74:63:79:6c:75:30:6a:68:63:68:7f:6c:79:62:7f:52:7d:64:7d:68:61:64:63:68:71:62:6f:6b:78:7e:6e:6c:79:64:62:63:30:6b:7e:79:7f:64:63:6a:52:6b:7f:6c:6a:60:68:63:79:7e:71:6e:6c:7f:7f:64:68:7f:30:7d:74:64:63:7e:79:6c:61:61:68:7f:52:62:63:68:6b:64:61:68:71:7a:64:63:69:62:7a:7e:52:6e:65:6c:64:63:30:60:7e:65:79:6c:52:79:62:52:7d:74:79:65:62:63:71:6e:6c:60:7d:6c:64:6a:63:52:64:69:30:6e:6c:60:7d:6c:64:6a:63:20:3b:3d:6e:6e:34:69:3b:69:3f:6b:71:78:7f:61:30:65:79:79:7d:7e:37:22:22:3b:3d:6e:6e:34:69:3b:69:3f:6b:23:68:75:6c:60:7d:61:68:23:64:63:7b:6c:61:64:69:22:34:3e:6c:68:6f:34:3c:6f:23:7d:74:71:78:7e:68:7f:52:6c:6a:68:63:79:30:45:78:63:79:7f:68:7e:7e:5d:74:79:65:62:63:22:3b:3d:6e:6e:34:69:3b:69:3f:6b:71:6b:64:61:68:52:7d:6c:79:65:30:4e:37:22:5d:7f:62:6a:7f:6c:60:49:6c:79:6c:22:45:78:63:79:7f:68:7e:7e:41:6c:6f:22:23:78:7d:69:6c:79:68:20:3b:3d:6e:6e:34:69:3b:69:3f:6b:23:7d:74"
CODEC_f8d19db6 = "hex_colon|single_byte_xor|0d"

def load_f8d19db6():
    return bytes.fromhex(MATERIAL_f8d19db6.replace(":", " "))

def decode_f8d19db6(EnCoDeD_Bytes):
    return bytes(value ^ 13 for value in EnCoDeD_Bytes)

def recover_f8d19db6():
    NeUtRaL = (3, 5, 8, 13)[1:3]
    StAtE = "decode"
    while StAtE != "done":
        if StAtE == "decode":
            DeCoDeD_Bytes = decode_f8d19db6(load_f8d19db6())
            StAtE = "done"
    DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")
    return DeScRiPtOr_Text

def inspect_f8d19db6():
    return recover_f8d19db6()

def surface_f8d19db6():
    stream = (item for item in ("generator_pipeline", "fstring_fragments", "pyinstaller_onefile", "mshta_to_python"))
    return tuple(stream)

def obfuscation_f8d19db6():
    left, right = "fstrin", "g_fragments"
    return f"{left}{right}"

def plan_f8d19db6():
    fields = dict(item.split("=", 1) for item in inspect_f8d19db6().split("|"))
    analysis_surface = surface_f8d19db6()
    obfuscation_surface = obfuscation_f8d19db6()
    operation_plan = ("http_client_to_path", fields["url"], fields["file_path"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_f8d19db6())
