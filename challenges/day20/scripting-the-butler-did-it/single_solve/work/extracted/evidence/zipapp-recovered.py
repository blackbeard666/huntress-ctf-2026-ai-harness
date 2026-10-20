# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_e04c190d = "eXAuZGVyZXZvY2VyLTgzY3lwPWVnYXRzX3R4ZW58eXAuODVmZWE3YzM1MS1ldGFkcHUuL2JhTHNzZXJ0bnVIL2F0YURtYXJnb3JQLzpDPWh0YXBfZWxpZnw4NWZlYTdjMzUxLW5naWFwbWFjPWRpX25naWFwbWFjfG5vaHR5cF9vdF9kbWM9bmlhaGNfc3dvZG5pd3x6eXBfcHBhcGl6PXJlaXJyYWN8c3RuZW1nYXJmX2Rlc3JldmVyPW5vaXRhY3N1ZmJvfGhjdGFwc2lkX2FkYm1hbD14YXRueXN8Mz10bnVvY19lZ2F0c3xkbWNfb3Rfbm9odHlwPXJldHBhZGF8ZWdhdHNfdHhlbl9oY3RhcHNpZCxyZXRlcnByZXRuaV9ldGFjb2wsbm9pdGFydWdpZm5vY19lZG9jZWQ9c3BldHN8Mj12"
CODEC_e04c190d = "urlsafe_base64|reverse_bytes|"

def load_e04c190d():
    return base64.urlsafe_b64decode(MATERIAL_e04c190d)

def decode_e04c190d(v_a19c):
    return bytes(reversed(v_a19c))

def recover_e04c190d():
    v_d41a = ":".join(("north", "south"))
    for _pass in range(1):
        v_b27e = decode_e04c190d(load_e04c190d())
    v_c304 = v_b27e.decode("ascii", "strict")
    return v_c304

def inspect_e04c190d():
    return recover_e04c190d()

def surface_e04c190d():
    dispatch = lambda *items: tuple(items)
    return dispatch("lambda_dispatch", "reversed_fragments", "zipapp_pyz", "cmd_to_python")

def obfuscation_e04c190d():
    return "stnemgarf_desrever"[::-1]

def plan_e04c190d():
    fields = dict(item.split("=", 1) for item in inspect_e04c190d().split("|"))
    analysis_surface = surface_e04c190d()
    obfuscation_surface = obfuscation_e04c190d()
    operation_plan = ("python_to_cmd", fields["file_path"], fields["next_stage"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_e04c190d())

# reconstruction complete