#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_6b053453 = "70:69:7a:2e:64:63:35:31:65:37:34:61:64:66:2d:65:68:63:61:63:2f:62:61:4c:73:73:65:72:74:6e:75:48:2f:61:74:61:44:6d:61:72:67:6f:72:50:2f:3a:43:3d:68:74:61:70:5f:65:76:69:68:63:72:61:7c:64:61:6f:6c:70:75:2f:64:69:6c:61:76:6e:69:2e:65:6c:70:6d:61:78:65:2e:64:63:35:31:65:37:34:61:64:66:2f:2f:3a:73:70:74:74:68:3d:6c:72:75:5f:64:61:6f:6c:70:75:7c:64:63:35:31:65:37:34:61:64:66:2d:6e:67:69:61:70:6d:61:63:3d:64:69:5f:6e:67:69:61:70:6d:61:63:7c:72:6f:73:73:65:63:65:64:65:72:70:5f:32:33:6c:6c:64:6e:75:72:3d:6e:69:61:68:63:5f:73:77:6f:64:6e:69:77:7c:72:69:64:65:6e:6f:5f:72:65:6c:6c:61:74:73:6e:69:79:70:3d:72:65:69:72:72:61:63:7c:6e:6f:69:74:63:65:72:69:64:6e:69:5f:61:64:62:6d:61:6c:3d:6e:6f:69:74:61:63:73:75:66:62:6f:7c:68:63:74:61:70:73:69:64:5f:79:72:61:6e:6f:69:74:63:69:64:3d:78:61:74:6e:79:73:7c:31:3d:74:6e:75:6f:63:5f:65:67:61:74:73:7c:6e:61:6c:70:5f:6d:61:65:72:74:73:5f:74:65:6b:63:6f:73:3d:72:65:74:70:61:64:61:7c:65:74:6f:6d:65:72:5f:74:69:6d:73:6e:61:72:74:2c:65:76:69:68:63:72:61:5f:65:64:6f:63:6e:65:2c:6c:61:63:6f:6c:5f:74:63:65:6c:6c:6f:63:3d:73:70:65:74:73:7c:32:3d:76"
CODEC_6b053453 = "hex_colon|reverse_bytes|"

def load_6b053453():
    return bytes.fromhex(MATERIAL_6b053453.replace(":", " "))

def decode_6b053453(stored_bytes):
    return bytes(reversed(stored_bytes))

def recover_6b053453():
    harmless_value = 19 * 7 - 133
    _pass = 0
    while _pass < 1:
        recovered_bytes = decode_6b053453(load_6b053453())
        _pass += 1
    configuration_text = recovered_bytes.decode("ascii", "strict")
    return configuration_text

def inspect_6b053453():
    view = memoryview(recover_6b053453().encode("ascii"))
    return bytes(view).decode("ascii")

def surface_6b053453():
    routes = {"selected": lambda: ("dictionary_dispatch", "lambda_indirection", "pyinstaller_onedir", "rundll32_predecessor")}
    return routes["selected"]()

def obfuscation_6b053453():
    recover = lambda value: value
    return recover("lambda_indirection")

def plan_6b053453():
    fields = dict(item.split("=", 1) for item in inspect_6b053453().split("|"))
    analysis_surface = surface_6b053453()
    obfuscation_surface = obfuscation_6b053453()
    operation_plan = ("socket_stream_plan", fields["archive_path"], fields["upload_url"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_6b053453())
