#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_1b26d921 = ("M0FGMTI2Q0M0MzJERkM4Ni1ZUFNQPWRpX2Zmb2RuYWh8dGFiLmhjdGFwc2lkLWxhY29sPWVnYXRzX3R4ZW58NjgxMjE6MS4wLjAuNzIxPXRuaW9wZG5lX3l4b3JwfGM1YzY0MGFjNGEtZXRhZHBVbWV0c3lTPWVtYW5fa3NhdHxleGUubm9odHlwL2M1YzY0MGFjNGEtbm9od"
    "HlQL2F0YURtYXJnb3JQLzpDPWh0YXBfcmV0ZXJwcmV0bml8eXAuYzVjNjQwYWM0YS1ldGFkcHUuL2JhTHNzZXJ0bnVIL2F0YURtYXJnb3JQLzpDPWh0YXBfZWxpZnxjNWM2NDBhYzRhL25vaHR5UHNzZXJ0bnVIPXRuZWdhX3Jlc3V8eXAuZDEwYzk0MTgvZGlsYXZuaS5lbH"
    "BtYXhlLmM1YzY0MGFjNGEvLzpzcHR0aD1scnV8YzVjNjQwYWM0YS1uZ2lhcG1hYz1kaV9uZ2lhcG1hY3xub2h0eXBfb3RfbGxlaHNyZXdvcD1uaWFoY19zd29kbml3fHJlbGxhdHNuaXlwX3JvbXJheXA9cmVpcnJhY3xuYWxwX2VtYW5fZXZpdGNlbGZlcj1ub2l0YWNzdWZ"
    "ib3xoY3RhcHNpZF95cmFub2l0Y2lkPXhhdG55c3w1PXRudW9jX2VnYXRzfGZmb2RuYWhfbm9odHlwX2RtYz1yZXRwYWRhfHNzZWNvcnBfaGN0YXBzaWQsZWxpZl9ldGlydyxkZWRkZWJtZV9lZG9jZWQsZXRvbWVyX2VyaXVxY2EsdHNvaF9lbGlmb3JwPXNwZXRzfDI9dg==")
CODEC_1b26d921 = "base64_chunks|reverse_bytes|"

def load_1b26d921():
    return base64.b64decode(MATERIAL_1b26d921)

def decode_1b26d921(EnCoDeD_Bytes):
    return bytes(reversed(EnCoDeD_Bytes))

def recover_1b26d921():
    NeUtRaL = (3, 5, 8, 13)[1:3]
    try:
        DeCoDeD_Bytes = decode_1b26d921(load_1b26d921())
    except (TypeError, ValueError) as error:
        raise RuntimeError("configuration recovery failed") from error
    DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")
    return DeScRiPtOr_Text

def inspect_1b26d921():
    view = memoryview(recover_1b26d921().encode("ascii"))
    return bytes(view).decode("ascii")

def surface_1b26d921():
    routes = {"selected": lambda: ("dictionary_dispatch", "reflective_name_plan", "pyarmor_pyinstaller", "powershell_to_python")}
    return routes["selected"]()

def obfuscation_1b26d921():
    reflection_plan = ("__import__", "getattr", "reflective_name_plan")
    return reflection_plan[-1]

def plan_1b26d921():
    fields = dict(item.split("=", 1) for item in inspect_1b26d921().split("|"))
    analysis_surface = surface_1b26d921()
    obfuscation_surface = obfuscation_1b26d921()
    operation_plan = ("cmd_python_handoff", ("platform",), fields["url"], fields["file_path"], (fields["interpreter_path"], fields["file_path"]), fields["task_name"], fields["proxy_endpoint"], fields["next_stage"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_1b26d921())
