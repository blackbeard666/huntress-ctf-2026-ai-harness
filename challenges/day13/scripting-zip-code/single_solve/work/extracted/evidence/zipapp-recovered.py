# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_2e74010c = "76:3d:32:7c:73:74:65:70:73:3d:64:65:63:6f:64:65:5f:63:6f:6e:66:69:67:75:72:61:74:69:6f:6e:2c:6c:6f:63:61:74:65:5f:69:6e:74:65:72:70:72:65:74:65:72:2c:64:69:73:70:61:74:63:68:5f:6e:65:78:74:5f:73:74:61:67:65:7c:61:64:61:70:74:65:72:3d:70:79:74:68:6f:6e:5f:74:6f:5f:70:6f:77:65:72:73:68:65:6c:6c:7c:73:74:61:67:65:5f:63:6f:75:6e:74:3d:33:7c:73:79:6e:74:61:78:3d:6c:61:6d:62:64:61:5f:64:69:73:70:61:74:63:68:7c:6f:62:66:75:73:63:61:74:69:6f:6e:3d:72:65:76:65:72:73:65:64:5f:66:72:61:67:6d:65:6e:74:73:7c:63:61:72:72:69:65:72:3d:7a:69:70:61:70:70:5f:70:79:7a:7c:77:69:6e:64:6f:77:73:5f:63:68:61:69:6e:3d:63:6d:64:5f:74:6f:5f:70:79:74:68:6f:6e:7c:63:61:6d:70:61:69:67:6e:5f:69:64:3d:63:61:6d:70:61:69:67:6e:2d:39:39:39:38:63:38:35:36:64:61:7c:66:69:6c:65:5f:70:61:74:68:3d:43:3a:2f:50:72:6f:67:72:61:6d:44:61:74:61:2f:48:75:6e:74:72:65:73:73:4c:61:62:2f:2e:75:70:64:61:74:65:2d:39:39:39:38:63:38:35:36:64:61:2e:70:79:7c:6e:65:78:74:5f:73:74:61:67:65:3d:70:79:63:33:38:2d:72:65:63:6f:76:65:72:65:64:2e:70:79"
CODEC_2e74010c = "hex_colon|identity|"

def load_2e74010c():
    return bytes.fromhex(MATERIAL_2e74010c.replace(":", " "))

def decode_2e74010c(e):
    return bytes(e)

def recover_2e74010c():
    n = ":".join(("north", "south"))
    _pass = 0
    while _pass < 1:
        d = decode_2e74010c(load_2e74010c())
        _pass += 1
    t = d.decode("ascii", "strict")
    return t

def inspect_2e74010c():
    stream = io.BytesIO(recover_2e74010c().encode("ascii"))
    return stream.read().decode("ascii")

def surface_2e74010c():
    dispatch = lambda *items: tuple(items)
    return dispatch("lambda_dispatch", "reversed_fragments", "zipapp_pyz", "cmd_to_python")

def obfuscation_2e74010c():
    return "stnemgarf_desrever"[::-1]

def plan_2e74010c():
    fields = dict(item.split("=", 1) for item in inspect_2e74010c().split("|"))
    analysis_surface = surface_2e74010c()
    obfuscation_surface = obfuscation_2e74010c()
    operation_plan = ("python_to_powershell", fields["file_path"], fields["next_stage"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_2e74010c())

# reconstruction complete