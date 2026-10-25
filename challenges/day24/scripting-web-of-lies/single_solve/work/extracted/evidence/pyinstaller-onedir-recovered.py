# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_53071291 = "60:2b:24:6a:65:62:73:66:65:2b:75:79:7a:7a:73:75:62:49:7a:79:75:77:7a:3a:73:78:75:79:72:73:49:77:64:75:7e:7f:60:73:3a:62:64:77:78:65:7b:7f:62:49:64:73:7b:79:62:73:6a:77:72:77:66:62:73:64:2b:63:64:7a:7a:7f:74:49:64:73:67:63:73:65:62:49:74:79:72:6f:6a:65:62:77:71:73:49:75:79:63:78:62:2b:27:6a:65:6f:78:62:77:6e:2b:72:7f:75:62:7f:79:78:77:64:6f:49:72:7f:65:66:77:62:75:7e:6a:79:74:70:63:65:75:77:62:7f:79:78:2b:7a:77:7b:74:72:77:49:7f:78:72:7f:64:73:75:62:7f:79:78:6a:75:77:64:64:7f:73:64:2b:66:6f:7f:78:65:62:77:7a:7a:73:64:49:79:78:73:72:7f:64:6a:61:7f:78:72:79:61:65:49:75:7e:77:7f:78:2b:64:63:78:72:7a:7a:25:24:49:66:64:73:72:73:75:73:65:65:79:64:6a:75:77:7b:66:77:7f:71:78:49:7f:72:2b:75:77:7b:66:77:7f:71:78:3b:74:24:70:75:2e:24:23:27:27:73:6a:63:66:7a:79:77:72:49:63:64:7a:2b:7e:62:62:66:65:2c:39:39:74:24:70:75:2e:24:23:27:27:73:38:73:6e:77:7b:66:7a:73:38:7f:78:60:77:7a:7f:72:39:63:66:7a:79:77:72:6a:77:64:75:7e:7f:60:73:49:66:77:62:7e:2b:55:2c:39:46:64:79:71:64:77:7b:52:77:62:77:39:5e:63:78:62:64:73:65:65:5a:77:74:39:75:77:75:7e:73:3b:74:24:70:75:2e:24:23:27:27:73:38:6c:7f:66"
CODEC_53071291 = "hex_colon|single_byte_xor|16"

def load_53071291():
    return bytes.fromhex(MATERIAL_53071291.replace(":", " "))

def decode_53071291(EnCoDeD_Bytes):
    return bytes(value ^ 22 for value in EnCoDeD_Bytes)

def recover_53071291():
    NeUtRaL = "left" if 2 > 1 else "right"
    DeCoDe_Target = decode_53071291
    DeCoDeD_Bytes = DeCoDe_Target(load_53071291())
    DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")
    return DeScRiPtOr_Text

def inspect_53071291():
    view = memoryview(recover_53071291().encode("ascii"))
    return bytes(view).decode("ascii")

def surface_53071291():
    routes = {"selected": lambda: ("dictionary_dispatch", "lambda_indirection", "pyinstaller_onedir", "rundll32_predecessor")}
    return routes["selected"]()

def obfuscation_53071291():
    recover = lambda value: value
    return recover("lambda_indirection")

def plan_53071291():
    fields = dict(item.split("=", 1) for item in inspect_53071291().split("|"))
    analysis_surface = surface_53071291()
    obfuscation_surface = obfuscation_53071291()
    operation_plan = ("urllib_request_body", fields["archive_path"], fields["upload_url"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_53071291())

# reconstruction complete