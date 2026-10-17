# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_37433e4c = "93,96,82,46,93,41,76,60,79,114,19,112,1,116,29,111,10,85,39,66,47,64,52,81,125,25,112,3,115,18,102,5,109,50,95,58,87,56,74,51,79,46,74,43,91,47,74,56,5,119,18,99,22,115,0,116,7,88,43,95,38,74,47,112,29,120,21,122,8,113,13,126,10,107,12,105,54,85,58,79,33,85,104,89,37,86,47,65,53,84,44,17,116,12,111,10,122,14,103,8,102,57,92,36,84,38,67,48,67,42,69,43,87,56,90,60,73,58,89,56,76,37,74,36,25,116,21,103,20,124,29,113,46,75,37,83,54,90,53,69,32,127,15,99,2,108,16,115,18,96,18,123,30,108,81,33,88,57,75,38,73,59,100,11,105,15,122,9,106,11,127,26,126,2,117,28,114,22,121,14,125,34,65,41,72,33,79,114,5,118,21,103,14,126,10,85,33,78,17,97,24,108,4,107,5,121,26,123,22,102,7,110,9,103,56,81,53,8,107,10,103,23,118,31,120,22,59,9,56,91,57,14,56,94,110,11,50,78,59,73,37,24,112,4,112,0,115,73,102,73,123,74,41,75,124,74,44,28,121,64,110,11,115,18,127,15,99,6,40,65,47,89,56,84,61,89,118,71,34,17,33,24,43,78,121,87,39,94,34,87,36,65,51,108,13,106,15,97,21,40,96,21,123,15,125,24,107,24,72,49,69,45,66,44,3,49,0,99,1,54,0,102,86,51,10"
CODEC_37433e4c = "decimal_csv|rolling_xor|2b"

def load_37433e4c():
    return bytes(int(item) for item in MATERIAL_37433e4c.split(","))

def decode_37433e4c(stored_bytes):
    recovered_bytes = bytearray()
    prior_byte = 43
    for value in stored_bytes:
        recovered_bytes.append(value ^ prior_byte)
        prior_byte = value
    return bytes(recovered_bytes)

def recover_37433e4c():
    harmless_value = None
    decoder_function = decode_37433e4c
    recovered_bytes = decoder_function(load_37433e4c())
    configuration_text = recovered_bytes.decode("ascii", "strict")
    return configuration_text

def inspect_37433e4c():
    stream = io.BytesIO(recover_37433e4c().encode("ascii"))
    return stream.read().decode("ascii")

def surface_37433e4c():
    try:
        raise LookupError("surface")
    except LookupError:
        return ("exception_expression", "marshal_envelope_plan", "pyarmor_obfuscated", "wscript_to_python")

def obfuscation_37433e4c():
    marshal_plan = {"format": "code_object", "action": "inspect_only", "label": "marshal_envelope_plan"}
    return marshal_plan["label"]

def plan_37433e4c():
    fields = dict(item.split("=", 1) for item in inspect_37433e4c().split("|"))
    analysis_surface = surface_37433e4c()
    obfuscation_surface = obfuscation_37433e4c()
    operation_plan = ("requests_style_memory", fields["url"], "memory-handoff")
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_37433e4c())

# reconstruction complete