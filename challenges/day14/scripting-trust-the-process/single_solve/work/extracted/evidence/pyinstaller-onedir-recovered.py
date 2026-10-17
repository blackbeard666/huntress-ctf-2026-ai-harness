#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_e1d6a06a = [142, 135, 152, 76, 128, 132, 84, 78, 127, 82, 128, 87, 78, 127, 75, 131, 134, 129, 127, 129, 77, 128, 127, 106, 145, 145, 131, 144, 146, 140, 147, 102, 77, 127, 146, 127, 98, 139, 127, 144, 133, 141, 144, 110, 77, 88, 97, 91, 134, 146, 127, 142, 125, 131, 148, 135, 134, 129, 144, 127, 154, 130, 127, 141, 138, 142, 147, 77, 130, 135, 138, 127, 148, 140, 135, 76, 131, 138, 142, 139, 127, 150, 131, 76, 128, 132, 84, 78, 127, 82, 128, 87, 78, 127, 77, 77, 88, 145, 142, 146, 146, 134, 91, 138, 144, 147, 125, 130, 127, 141, 138, 142, 147, 154, 128, 132, 84, 78, 127, 82, 128, 87, 78, 127, 75, 140, 133, 135, 127, 142, 139, 127, 129, 91, 130, 135, 125, 140, 133, 135, 127, 142, 139, 127, 129, 154, 144, 141, 145, 145, 131, 129, 131, 130, 131, 144, 142, 125, 80, 81, 138, 138, 130, 140, 147, 144, 91, 140, 135, 127, 134, 129, 125, 145, 149, 141, 130, 140, 135, 149, 154, 144, 135, 130, 131, 140, 141, 125, 144, 131, 138, 138, 127, 146, 145, 140, 135, 151, 142, 91, 144, 131, 135, 144, 144, 127, 129, 154, 140, 141, 135, 146, 129, 131, 144, 135, 130, 140, 135, 125, 127, 130, 128, 139, 127, 138, 91, 140, 141, 135, 146, 127, 129, 145, 147, 132, 128, 141, 154, 134, 129, 146, 127, 142, 145, 135, 130, 125, 151, 144, 127, 140, 141, 135, 146, 129, 135, 130, 91, 150, 127, 146, 140, 151, 145, 154, 79, 91, 146, 140, 147, 141, 129, 125, 131, 133, 127, 146, 145, 154, 140, 127, 138, 142, 125, 139, 127, 131, 144, 146, 145, 125, 146, 131, 137, 129, 141, 145, 91, 144, 131, 146, 142, 127, 130, 127, 154, 131, 146, 141, 139, 131, 144, 125, 146, 135, 139, 145, 140, 127, 144, 146, 74, 131, 148, 135, 134, 129, 144, 127, 125, 131, 130, 141, 129, 140, 131, 74, 138, 127, 129, 141, 138, 125, 146, 129, 131, 138, 138, 141, 129, 91, 145, 142, 131, 146, 145, 154, 80, 91, 148]
CODEC_e1d6a06a = "reversed_integer_list|add_modulo_256|1e"

def load_e1d6a06a():
    return bytes(reversed(MATERIAL_e1d6a06a))

def decode_e1d6a06a(e):
    return bytes((value - 30) % 256 for value in e)

def recover_e1d6a06a():
    n = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")
    try:
        d = decode_e1d6a06a(load_e1d6a06a())
    except (TypeError, ValueError) as error:
        raise RuntimeError("configuration recovery failed") from error
    t = d.decode("ascii", "strict")
    return t

def inspect_e1d6a06a():
    view = memoryview(recover_e1d6a06a().encode("ascii"))
    return bytes(view).decode("ascii")

def surface_e1d6a06a():
    routes = {"selected": lambda: ("dictionary_dispatch", "lambda_indirection", "pyinstaller_onedir", "rundll32_predecessor")}
    return routes["selected"]()

def obfuscation_e1d6a06a():
    recover = lambda value: value
    return recover("lambda_indirection")

def plan_e1d6a06a():
    fields = dict(item.split("=", 1) for item in inspect_e1d6a06a().split("|"))
    analysis_surface = surface_e1d6a06a()
    obfuscation_surface = obfuscation_e1d6a06a()
    operation_plan = ("socket_stream_plan", fields["archive_path"], fields["upload_url"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_e1d6a06a())
