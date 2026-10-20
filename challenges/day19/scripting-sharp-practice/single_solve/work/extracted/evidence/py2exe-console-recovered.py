# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_230e7b22 = "eXAuOTI2Y2ExODM3Ny1ldGFkcHUuL2JhTHNzZXJ0bnVIL2F0YURtYXJnb3JQLzpDPWh0YXBfZWxpZnw5MjZjYTE4Mzc3LW5naWFwbWFjPWRpX25naWFwbWFjfHJvc3NlY2VkZXJwXzIzcnZzZ2VyPW5pYWhjX3N3b2RuaXd8ZWxvc25vY19leGUyeXA9cmVpcnJhY3xzbGxlY19lcnVzb2xjPW5vaXRhY3N1ZmJvfGVzYWNfaGN0YW09eGF0bnlzfDE9dG51b2NfZWdhdHN8cm90cGlyY3NlZF95cG51cj1yZXRwYWRhfHNzZWNvcnBfaGN0YXBzaWQsbGFjb2xfZXRhY29sPXNwZXRzfDI9dg=="
CODEC_230e7b22 = "urlsafe_base64|reverse_bytes|"

def load_230e7b22():
    return base64.urlsafe_b64decode(MATERIAL_230e7b22)

def decode_230e7b22(stored_bytes):
    return bytes(reversed(stored_bytes))

def recover_230e7b22():
    harmless_value = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")
    recovered_bytes = decode_230e7b22(load_230e7b22())
    configuration_text = recovered_bytes.decode("ascii", "strict")
    return configuration_text

def inspect_230e7b22():
    return recover_230e7b22()

def surface_230e7b22():
    selected = "carrier"
    match selected:
        case "carrier":
            return ("match_case", "closure_cells", "py2exe_console", "regsvr32_predecessor")
        case _:
            return ()

def obfuscation_230e7b22():
    value = "closure_cells"
    def recover():
        return value
    return recover()

def plan_230e7b22():
    fields = dict(item.split("=", 1) for item in inspect_230e7b22().split("|"))
    analysis_surface = surface_230e7b22()
    obfuscation_surface = obfuscation_230e7b22()
    operation_plan = ("runpy_descriptor", ("python3", fields["file_path"]))
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_230e7b22())

# reconstruction complete