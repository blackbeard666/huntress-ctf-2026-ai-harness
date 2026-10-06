#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_a0106f95 = "76:3d:32:7c:73:74:65:70:73:3d:73:65:6c:65:63:74:5f:66:69:78:74:75:72:65:5f:66:69:6c:65:73:2c:74:72:61:6e:73:66:6f:72:6d:5f:63:6f:70:79:2c:77:72:69:74:65:5f:72:65:63:6f:76:65:72:79:5f:6e:6f:74:65:7c:61:64:61:70:74:65:72:3d:6f:73:5f:77:61:6c:6b:5f:63:6f:70:79:5f:70:6c:61:6e:7c:73:74:61:67:65:5f:63:6f:75:6e:74:3d:31:7c:73:79:6e:74:61:78:3d:64:65:63:6f:72:61:74:6f:72:5f:77:72:61:70:70:65:72:7c:6f:62:66:75:73:63:61:74:69:6f:6e:3d:62:79:74:65:73:5f:74:72:61:6e:73:6c:61:74:69:6f:6e:7c:63:61:72:72:69:65:72:3d:63:78:5f:66:72:65:65:7a:65:5f:65:78:65:63:75:74:61:62:6c:65:7c:77:69:6e:64:6f:77:73:5f:63:68:61:69:6e:3d:73:63:68:65:64:75:6c:65:64:5f:74:61:73:6b:5f:64:65:73:63:72:69:70:74:6f:72:7c:63:61:6d:70:61:69:67:6e:5f:69:64:3d:63:61:6d:70:61:69:67:6e:2d:37:38:66:65:31:63:38:32:30:65:7c:65:78:74:65:6e:73:69:6f:6e:3d:2e:37:38:66:65:31:63:38:32:30:65:2e:6c:6f:63:6b:65:64:7c:6e:6f:74:65:5f:6e:61:6d:65:3d:52:45:43:4f:56:45:52:2d:37:38:66:65:31:63:38:32:30:65:2e:74:78:74:7c:74:61:72:67:65:74:5f:72:6f:6f:74:3d:43:3a:2f:48:75:6e:74:72:65:73:73:4c:61:62:2f:37:38:66:65:31:63:38:32:30:65"
CODEC_a0106f95 = "hex_colon|identity|"

def load_a0106f95():
    return bytes.fromhex(MATERIAL_a0106f95.replace(":", " "))

def decode_a0106f95(stored_bytes):
    return bytes(stored_bytes)

def recover_a0106f95():
    harmless_value = 19 * 7 - 133
    decoder_function = decode_a0106f95
    recovered_bytes = decoder_function(load_a0106f95())
    configuration_text = recovered_bytes.decode("ascii", "strict")
    return configuration_text

def inspect_a0106f95():
    stream = io.BytesIO(recover_a0106f95().encode("ascii"))
    return stream.read().decode("ascii")

def decorate_surface_a0106f95(function):
    def wrapped():
        return tuple(function())
    return wrapped

@decorate_surface_a0106f95
def surface_a0106f95():
    return ("decorator_wrapper", "bytes_translation", "cx_freeze_executable", "scheduled_task_descriptor")

def obfuscation_a0106f95():
    return bytes((98, 121, 116, 101, 115, 95, 116, 114, 97, 110, 115, 108, 97, 116, 105, 111, 110)).decode("ascii")

def plan_a0106f95():
    fields = dict(item.split("=", 1) for item in inspect_a0106f95().split("|"))
    analysis_surface = surface_a0106f95()
    obfuscation_surface = obfuscation_a0106f95()
    operation_plan = ("os_walk_copy_plan", fields["target_root"], fields["extension"], fields["note_name"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_a0106f95())
