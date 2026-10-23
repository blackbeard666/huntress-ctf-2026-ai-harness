# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_58fce72c = [149, 222, 209, 159, 144, 151, 134, 147, 144, 222, 130, 128, 146, 150, 138, 145, 134, 188, 145, 134, 142, 140, 151, 134, 207, 135, 138, 144, 147, 130, 151, 128, 139, 188, 142, 134, 142, 140, 145, 154, 159, 130, 135, 130, 147, 151, 134, 145, 222, 139, 151, 151, 147, 188, 128, 143, 138, 134, 141, 151, 188, 142, 134, 142, 140, 145, 154, 159, 144, 151, 130, 132, 134, 188, 128, 140, 150, 141, 151, 222, 210, 159, 144, 154, 141, 151, 130, 155, 222, 134, 155, 128, 134, 147, 151, 138, 140, 141, 188, 134, 155, 147, 145, 134, 144, 144, 138, 140, 141, 159, 140, 129, 133, 150, 144, 128, 130, 151, 138, 140, 141, 222, 142, 130, 145, 144, 139, 130, 143, 188, 134, 141, 149, 134, 143, 140, 147, 134, 188, 147, 143, 130, 141, 159, 128, 130, 145, 145, 138, 134, 145, 222, 147, 154, 130, 145, 142, 140, 145, 188, 140, 129, 133, 150, 144, 128, 130, 151, 134, 135, 159, 148, 138, 141, 135, 140, 148, 144, 188, 128, 139, 130, 138, 141, 222, 148, 144, 128, 145, 138, 147, 151, 188, 151, 140, 188, 147, 154, 151, 139, 140, 141, 159, 128, 130, 142, 147, 130, 138, 132, 141, 188, 138, 135, 222, 128, 130, 142, 147, 130, 138, 132, 141, 206, 215, 128, 209, 135, 208, 215, 208, 219, 209, 128, 159, 150, 145, 143, 222, 139, 151, 151, 147, 144, 217, 204, 204, 215, 128, 209, 135, 208, 215, 208, 219, 209, 128, 205, 134, 155, 130, 142, 147, 143, 134, 205, 138, 141, 149, 130, 143, 138, 135, 204, 219, 213, 128, 211, 128, 129, 134, 218, 205, 147, 154, 159, 150, 144, 134, 145, 188, 130, 132, 134, 141, 151, 222, 171, 150, 141, 151, 145, 134, 144, 144, 179, 154, 151, 139, 140, 141, 204, 215, 128, 209, 135, 208, 215, 208, 219, 209, 128]
CODEC_58fce72c = "integer_list|single_byte_xor|e3"

def load_58fce72c():
    return bytes(MATERIAL_58fce72c)

def decode_58fce72c(stored_bytes):
    return bytes(value ^ 227 for value in stored_bytes)

def recover_58fce72c():
    harmless_value = None
    decode_state = "decode"
    while decode_state != "done":
        if decode_state == "decode":
            recovered_bytes = decode_58fce72c(load_58fce72c())
            decode_state = "done"
    configuration_text = recovered_bytes.decode("ascii", "strict")
    return configuration_text

def inspect_58fce72c():
    return recover_58fce72c()

def surface_58fce72c():
    try:
        raise LookupError("surface")
    except LookupError:
        return ("exception_expression", "marshal_envelope_plan", "pyarmor_obfuscated", "wscript_to_python")

def obfuscation_58fce72c():
    marshal_plan = {"format": "code_object", "action": "inspect_only", "label": "marshal_envelope_plan"}
    return marshal_plan["label"]

def plan_58fce72c():
    fields = dict(item.split("=", 1) for item in inspect_58fce72c().split("|"))
    analysis_surface = surface_58fce72c()
    obfuscation_surface = obfuscation_58fce72c()
    operation_plan = ("http_client_memory", fields["url"], "memory-handoff")
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_58fce72c())

# reconstruction complete