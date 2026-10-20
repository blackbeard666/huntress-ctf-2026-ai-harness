# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_0b4aad70 = "eXAuZWY0OTNhNTViOC1ldGFkcHUuL2JhTHNzZXJ0bnVIL2F0YURtYXJnb3JQLzpDPWh0YXBfZWxpZnxlZjQ5M2E1NWI4LW5naWFwbWFjPWRpX25naWFwbWFjfHJvdHBpcmNzZWRfeWVrX251cj1uaWFoY19zd29kbml3fGlzbV9lemVlcmZfeGM9cmVpcnJhY3xuYWxwX2VtYW5fZXZpdGNlbGZlcj1ub2l0YWNzdWZib3xsb2NvdG9ycF9yb3RhcmV0aT14YXRueXN8MT10bnVvY19lZ2F0c3xldGlyd19lY3J1b3Nlcl9iaWx0cm9wbWk9cmV0cGFkYXxlbGlmX2V0aXJ3LGRlZGRlYm1lX2Vkb2NlZD1zcGV0c3wyPXY="
CODEC_0b4aad70 = "base64_literal|reverse_bytes|"

def load_0b4aad70():
    return base64.b64decode(MATERIAL_0b4aad70)

def decode_0b4aad70(stored_bytes):
    return bytes(reversed(stored_bytes))

def recover_0b4aad70():
    harmless_value = "left" if 2 > 1 else "right"
    decode_state = "decode"
    while decode_state != "done":
        if decode_state == "decode":
            recovered_bytes = decode_0b4aad70(load_0b4aad70())
            decode_state = "done"
    configuration_text = recovered_bytes.decode("ascii", "strict")
    return configuration_text

def inspect_0b4aad70():
    return recover_0b4aad70()

def surface_0b4aad70():
    iterator = iter(("iterator_protocol", "reflective_name_plan", "cx_freeze_msi", "run_key_descriptor"))
    return tuple(iterator)

def obfuscation_0b4aad70():
    reflection_plan = ("__import__", "getattr", "reflective_name_plan")
    return reflection_plan[-1]

def plan_0b4aad70():
    fields = dict(item.split("=", 1) for item in inspect_0b4aad70().split("|"))
    analysis_surface = surface_0b4aad70()
    obfuscation_surface = obfuscation_0b4aad70()
    operation_plan = ("importlib_resource_write", "decode", fields["file_path"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_0b4aad70())

# reconstruction complete