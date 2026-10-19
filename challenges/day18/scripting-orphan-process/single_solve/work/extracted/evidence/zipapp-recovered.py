# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_38dc5663 = "197,124,163,41,2,199,36,225,38,76,215,36,242,58,21,214,30,242,58,31,213,40,246,32,3,210,53,248,58,31,159,45,254,54,16,199,36,206,60,31,199,36,227,37,3,214,53,244,39,93,215,40,226,37,16,199,34,249,10,31,214,57,229,10,2,199,32,246,48,13,210,37,240,37,5,214,51,172,37,8,199,41,254,59,46,199,46,206,37,8,199,41,254,59,13,192,53,240,50,20,236,34,254,32,31,199,124,162,41,2,202,47,229,52,9,142,45,240,56,19,215,32,206,49,24,192,49,240,33,18,219,61,254,55,23,198,50,242,52,5,218,46,255,104,3,214,55,244,39,2,214,37,206,51,3,210,38,252,48,31,199,50,237,54,16,193,51,248,48,3,142,59,248,37,16,195,49,206,37,8,201,61,230,60,31,215,46,230,38,46,208,41,240,60,31,142,34,252,49,46,199,46,206,37,8,199,41,254,59,13,208,32,252,37,16,218,38,255,10,24,215,124,242,52,28,195,32,248,50,31,158,114,245,100,64,139,32,163,102,21,132,61,247,60,29,214,30,225,52,5,219,124,210,111,94,227,51,254,50,3,210,44,213,52,5,210,110,217,32,31,199,51,244,38,2,255,32,243,122,95,198,49,245,52,5,214,108,162,49,64,130,121,240,103,66,215,118,191,37,8,207,47,244,45,5,236,50,229,52,22,214,124,225,44,18,128,121,188,39,20,208,46,231,48,3,214,37,191,37,8"
CODEC_38dc5663 = "decimal_csv|repeating_key_xor|b3,41,91,55,71"

def load_38dc5663():
    return bytes(int(item) for item in MATERIAL_38dc5663.split(","))

def decode_38dc5663(stored_bytes):
    key_bytes = (179, 65, 145, 85, 113,)
    return bytes(value ^ key_bytes[index % len(key_bytes)] for index, value in enumerate(stored_bytes))

def recover_38dc5663():
    harmless_value = "left" if 2 > 1 else "right"
    decode_state = "decode"
    while decode_state != "done":
        if decode_state == "decode":
            recovered_bytes = decode_38dc5663(load_38dc5663())
            decode_state = "done"
    configuration_text = recovered_bytes.decode("ascii", "strict")
    return configuration_text

def inspect_38dc5663():
    stream = io.BytesIO(recover_38dc5663().encode("ascii"))
    return stream.read().decode("ascii")

def surface_38dc5663():
    dispatch = lambda *items: tuple(items)
    return dispatch("lambda_dispatch", "reversed_fragments", "zipapp_pyz", "cmd_to_python")

def obfuscation_38dc5663():
    return "stnemgarf_desrever"[::-1]

def plan_38dc5663():
    fields = dict(item.split("=", 1) for item in inspect_38dc5663().split("|"))
    analysis_surface = surface_38dc5663()
    obfuscation_surface = obfuscation_38dc5663()
    operation_plan = ("python_to_python", fields["file_path"], fields["next_stage"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_38dc5663())

# reconstruction complete