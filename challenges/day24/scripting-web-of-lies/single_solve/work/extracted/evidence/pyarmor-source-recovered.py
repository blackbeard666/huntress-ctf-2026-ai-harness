#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_d6a53cf4 = [95, 96, 53, 95, 51, 53, 46, 55, 47, 55, 45, 108, 109, 102, 114, 119, 78, 113, 113, 99, 112, 114, 108, 115, 70, 59, 114, 108, 99, 101, 95, 93, 112, 99, 113, 115, 122, 119, 110, 44, 53, 52, 53, 52, 99, 52, 51, 97, 45, 98, 103, 106, 95, 116, 108, 103, 44, 99, 106, 110, 107, 95, 118, 99, 44, 95, 96, 53, 95, 51, 53, 46, 55, 47, 55, 45, 45, 56, 113, 110, 114, 114, 102, 59, 106, 112, 115, 122, 95, 96, 53, 95, 51, 53, 46, 55, 47, 55, 43, 108, 101, 103, 95, 110, 107, 95, 97, 59, 98, 103, 93, 108, 101, 103, 95, 110, 107, 95, 97, 122, 108, 109, 102, 114, 119, 110, 93, 109, 114, 93, 114, 110, 103, 112, 97, 113, 117, 59, 108, 103, 95, 102, 97, 93, 113, 117, 109, 98, 108, 103, 117, 122, 98, 99, 114, 95, 97, 113, 115, 100, 96, 109, 93, 112, 109, 107, 112, 95, 119, 110, 59, 112, 99, 103, 112, 112, 95, 97, 122, 108, 95, 106, 110, 93, 99, 110, 109, 106, 99, 116, 108, 99, 93, 106, 95, 102, 113, 112, 95, 107, 59, 108, 109, 103, 114, 95, 97, 113, 115, 100, 96, 109, 122, 108, 109, 103, 113, 113, 99, 112, 110, 118, 99, 93, 108, 109, 103, 114, 110, 99, 97, 118, 99, 59, 118, 95, 114, 108, 119, 113, 122, 47, 59, 114, 108, 115, 109, 97, 93, 99, 101, 95, 114, 113, 122, 119, 112, 109, 107, 99, 107, 93, 96, 103, 106, 106, 112, 115, 59, 112, 99, 114, 110, 95, 98, 95, 122, 119, 112, 109, 107, 99, 107, 93, 102, 97, 114, 95, 110, 113, 103, 98, 42, 99, 114, 109, 107, 99, 112, 93, 99, 112, 103, 115, 111, 97, 95, 59, 113, 110, 99, 114, 113, 122, 48, 59, 116]
CODEC_d6a53cf4 = "reversed_integer_list|subtract_modulo_256|02"

def load_d6a53cf4():
    return bytes(reversed(MATERIAL_d6a53cf4))

def decode_d6a53cf4(EnCoDeD_Bytes):
    return bytes((value + 2) % 256 for value in EnCoDeD_Bytes)

def recover_d6a53cf4():
    NeUtRaL = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")
    try:
        DeCoDeD_Bytes = decode_d6a53cf4(load_d6a53cf4())
    except (TypeError, ValueError) as error:
        raise RuntimeError("configuration recovery failed") from error
    DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")
    return DeScRiPtOr_Text

def inspect_d6a53cf4():
    view = memoryview(recover_d6a53cf4().encode("ascii"))
    return bytes(view).decode("ascii")

def surface_d6a53cf4():
    try:
        raise LookupError("surface")
    except LookupError:
        return ("exception_expression", "marshal_envelope_plan", "pyarmor_obfuscated", "wscript_to_python")

def obfuscation_d6a53cf4():
    marshal_plan = {"format": "code_object", "action": "inspect_only", "label": "marshal_envelope_plan"}
    return marshal_plan["label"]

def plan_d6a53cf4():
    fields = dict(item.split("=", 1) for item in inspect_d6a53cf4().split("|"))
    analysis_surface = surface_d6a53cf4()
    obfuscation_surface = obfuscation_d6a53cf4()
    operation_plan = ("urllib_memory", fields["url"], "memory-handoff")
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_d6a53cf4())
