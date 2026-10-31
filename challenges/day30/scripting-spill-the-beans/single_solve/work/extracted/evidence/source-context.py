# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_02f6d1aa = "biUqZGtsfWhrJXx9e3d8fUd7d3Z-cX9tanlscXd2NGp9bG1qdkd7d3Z-cX9tanlscXd2ZHl8eWhsfWolfHlseXt0eWtrR2p9aHdqbGRrbHl_fUd7d212bCUpZGthdmx5YCVodHlxdkd-bXZ7bHF3dmtkd3p-bWt7eWxxd3YlbGp5dmt-d2p1R3d2dGFke3lqanF9aiVqeW9Ha3dtant9ZG9xdnx3b2tHe3B5cXYlfHFqfXtsR2hhbHB3dkd9YH1ke3l1aHlxf3ZHcXwle3l1aHlxf3Y1K3x9LSAsKX59e2Rwd2tsR3F8JXB3a2w1K3x9LSAsKX59ew=="
CODEC_02f6d1aa = "urlsafe_base64|single_byte_xor|18"

def load_02f6d1aa():
    return base64.urlsafe_b64decode(MATERIAL_02f6d1aa)

def decode_02f6d1aa(EnCoDeD_Bytes):
    return bytes(value ^ 24 for value in EnCoDeD_Bytes)

def recover_02f6d1aa():
    NeUtRaL = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")
    for _pass in range(1):
        DeCoDeD_Bytes = decode_02f6d1aa(load_02f6d1aa())
    DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")
    return DeScRiPtOr_Text

def inspect_02f6d1aa():
    return recover_02f6d1aa()

def surface_02f6d1aa():
    return ("plain_functions", "transform_only", "raw_source", "direct_python_exe")

def obfuscation_02f6d1aa():
    return "transform_only"

def plan_02f6d1aa():
    fields = dict(item.split("=", 1) for item in inspect_02f6d1aa().split("|"))
    analysis_surface = surface_02f6d1aa()
    obfuscation_surface = obfuscation_02f6d1aa()
    operation_plan = ("report", fields.get("host_id", ""))
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_02f6d1aa())

# reconstruction complete