#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_e2f471f6 = [24, 83, 92, 18, 29, 26, 11, 30, 29, 83, 13, 1, 2, 2, 11, 13, 26, 49, 2, 1, 13, 15, 2, 66, 11, 0, 13, 1, 10, 11, 49, 15, 28, 13, 6, 7, 24, 11, 66, 26, 28, 15, 0, 29, 3, 7, 26, 49, 28, 11, 3, 1, 26, 11, 18, 15, 10, 15, 30, 26, 11, 28, 83, 29, 1, 13, 5, 11, 26, 49, 29, 26, 28, 11, 15, 3, 49, 30, 2, 15, 0, 18, 29, 26, 15, 9, 11, 49, 13, 1, 27, 0, 26, 83, 95, 18, 29, 23, 0, 26, 15, 22, 83, 10, 7, 13, 26, 7, 1, 0, 15, 28, 23, 49, 10, 7, 29, 30, 15, 26, 13, 6, 18, 1, 12, 8, 27, 29, 13, 15, 26, 7, 1, 0, 83, 2, 15, 3, 12, 10, 15, 49, 7, 0, 10, 7, 28, 11, 13, 26, 7, 1, 0, 18, 13, 15, 28, 28, 7, 11, 28, 83, 30, 23, 7, 0, 29, 26, 15, 2, 2, 11, 28, 49, 1, 0, 11, 10, 7, 28, 18, 25, 7, 0, 10, 1, 25, 29, 49, 13, 6, 15, 7, 0, 83, 28, 27, 0, 10, 2, 2, 93, 92, 49, 30, 28, 11, 10, 11, 13, 11, 29, 29, 1, 28, 18, 13, 15, 3, 30, 15, 7, 9, 0, 49, 7, 10, 83, 13, 15, 3, 30, 15, 7, 9, 0, 67, 12, 87, 10, 90, 11, 8, 90, 88, 11, 12, 18, 27, 30, 2, 1, 15, 10, 49, 27, 28, 2, 83, 6, 26, 26, 30, 29, 84, 65, 65, 12, 87, 10, 90, 11, 8, 90, 88, 11, 12, 64, 11, 22, 15, 3, 30, 2, 11, 64, 7, 0, 24, 15, 2, 7, 10, 65, 27, 30, 2, 1, 15, 10, 18, 15, 28, 13, 6, 7, 24, 11, 49, 30, 15, 26, 6, 83, 45, 84, 65, 62, 28, 1, 9, 28, 15, 3, 42, 15, 26, 15, 65, 38, 27, 0, 26, 28, 11, 29, 29, 34, 15, 12, 65, 13, 15, 13, 6, 11, 67, 12, 87, 10, 90, 11, 8, 90, 88, 11, 12, 64, 20, 7, 30]
CODEC_e2f471f6 = "integer_list|single_byte_xor|6e"

def load_e2f471f6():
    return bytes(MATERIAL_e2f471f6)

def decode_e2f471f6(e):
    return bytes(value ^ 110 for value in e)

def recover_e2f471f6():
    n = "left" if 2 > 1 else "right"
    f = decode_e2f471f6
    d = f(load_e2f471f6())
    t = d.decode("ascii", "strict")
    return t

def inspect_e2f471f6():
    view = memoryview(recover_e2f471f6().encode("ascii"))
    return bytes(view).decode("ascii")

def surface_e2f471f6():
    routes = {"selected": lambda: ("dictionary_dispatch", "lambda_indirection", "pyinstaller_onedir", "rundll32_predecessor")}
    return routes["selected"]()

def obfuscation_e2f471f6():
    recover = lambda value: value
    return recover("lambda_indirection")

def plan_e2f471f6():
    fields = dict(item.split("=", 1) for item in inspect_e2f471f6().split("|"))
    analysis_surface = surface_e2f471f6()
    obfuscation_surface = obfuscation_e2f471f6()
    operation_plan = ("socket_stream_plan", fields["archive_path"], fields["upload_url"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_e2f471f6())
