# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_ffa84e90 = "31:73:70:2e:65:6c:70:6d:61:73:2d:65:63:72:75:6f:73:65:72:3d:65:67:61:74:73:5f:74:78:65:6e:7c:30:30:34:38:32:3a:31:2e:30:2e:30:2e:37:32:31:3d:74:6e:69:6f:70:64:6e:65:5f:79:78:6f:72:70:7c:30:62:62:36:64:39:30:32:34:65:2d:65:74:61:64:70:55:6d:65:74:73:79:53:3d:65:6d:61:6e:5f:6b:73:61:74:7c:65:78:65:2e:6e:6f:68:74:79:70:2f:30:62:62:36:64:39:30:32:34:65:2d:6e:6f:68:74:79:50:2f:61:74:61:44:6d:61:72:67:6f:72:50:2f:3a:43:3d:68:74:61:70:5f:72:65:74:65:72:70:72:65:74:6e:69:7c:79:70:2e:30:62:62:36:64:39:30:32:34:65:2d:65:74:61:64:70:75:2e:2f:62:61:4c:73:73:65:72:74:6e:75:48:2f:61:74:61:44:6d:61:72:67:6f:72:50:2f:3a:43:3d:68:74:61:70:5f:65:6c:69:66:7c:30:62:62:36:64:39:30:32:34:65:2f:6e:6f:68:74:79:50:73:73:65:72:74:6e:75:48:3d:74:6e:65:67:61:5f:72:65:73:75:7c:79:70:2e:63:33:30:63:33:62:31:34:2f:64:69:6c:61:76:6e:69:2e:65:6c:70:6d:61:78:65:2e:30:62:62:36:64:39:30:32:34:65:2f:2f:3a:73:70:74:74:68:3d:6c:72:75:7c:30:62:62:36:64:39:30:32:34:65:2d:6e:67:69:61:70:6d:61:63:3d:64:69:5f:6e:67:69:61:70:6d:61:63:7c:72:6f:74:70:69:72:63:73:65:64:5f:65:63:69:76:72:65:73:3d:6e:69:61:68:63:5f:73:77:6f:64:6e:69:77:7c:65:63:69:76:72:65:73:5f:73:77:6f:64:6e:69:77:5f:65:78:65:32:79:70:3d:72:65:69:72:72:61:63:7c:67:6e:69:74:75:6f:72:5f:6e:6f:69:74:70:65:63:78:65:3d:6e:6f:69:74:61:63:73:75:66:62:6f:7c:67:6e:69:64:6e:69:62:5f:73:75:72:6c:61:77:3d:78:61:74:6e:79:73:7c:35:3d:74:6e:75:6f:63:5f:65:67:61:74:73:7c:66:66:6f:64:6e:61:68:5f:6e:6f:68:74:79:70:5f:6c:6c:65:68:73:72:65:77:6f:70:3d:72:65:74:70:61:64:61:7c:73:73:65:63:6f:72:70:5f:68:63:74:61:70:73:69:64:2c:65:6c:69:66:5f:65:74:69:72:77:2c:64:65:64:64:65:62:6d:65:5f:65:64:6f:63:65:64:2c:65:74:6f:6d:65:72:5f:65:72:69:75:71:63:61:2c:74:73:6f:68:5f:65:6c:69:66:6f:72:70:3d:73:70:65:74:73:7c:32:3d:76"
CODEC_ffa84e90 = "hex_colon|reverse_bytes|"

def load_ffa84e90():
    return bytes.fromhex(MATERIAL_ffa84e90.replace(":", " "))

def decode_ffa84e90(stored_bytes):
    return bytes(reversed(stored_bytes))

def recover_ffa84e90():
    harmless_value = None
    try:
        recovered_bytes = decode_ffa84e90(load_ffa84e90())
    except (TypeError, ValueError) as error:
        raise RuntimeError("configuration recovery failed") from error
    configuration_text = recovered_bytes.decode("ascii", "strict")
    return configuration_text

def inspect_ffa84e90():
    return recover_ffa84e90()

def surface_ffa84e90():
    return surface if (surface := ("walrus_binding", "exception_routing", "py2exe_windows_service", "service_descriptor")) else ()

def obfuscation_ffa84e90():
    try:
        {}["missing"]
    except KeyError:
        return "exception_routing"

def plan_ffa84e90():
    fields = dict(item.split("=", 1) for item in inspect_ffa84e90().split("|"))
    analysis_surface = surface_ffa84e90()
    obfuscation_surface = obfuscation_ffa84e90()
    operation_plan = ("powershell_python_handoff", ("platform",), fields["url"], fields["file_path"], (fields["interpreter_path"], fields["file_path"]), fields["task_name"], fields["proxy_endpoint"], fields["next_stage"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_ffa84e90())

# reconstruction complete