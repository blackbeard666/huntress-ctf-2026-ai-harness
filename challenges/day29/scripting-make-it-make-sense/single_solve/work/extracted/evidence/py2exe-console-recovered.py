#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_b8b3b1c5 = [108, 51, 40, 114, 105, 106, 91, 102, 105, 51, 98, 101, 89, 87, 106, 91, 85, 98, 101, 89, 87, 98, 34, 90, 95, 105, 102, 87, 106, 89, 94, 85, 102, 104, 101, 89, 91, 105, 105, 114, 87, 90, 87, 102, 106, 91, 104, 51, 105, 107, 88, 102, 104, 101, 89, 91, 105, 105, 85, 98, 95, 105, 106, 114, 105, 106, 87, 93, 91, 85, 89, 101, 107, 100, 106, 51, 39, 114, 105, 111, 100, 106, 87, 110, 51, 99, 87, 106, 89, 94, 85, 89, 87, 105, 91, 114, 101, 88, 92, 107, 105, 89, 87, 106, 95, 101, 100, 51, 89, 98, 101, 105, 107, 104, 91, 85, 89, 91, 98, 98, 105, 114, 89, 87, 104, 104, 95, 91, 104, 51, 102, 111, 40, 91, 110, 91, 85, 89, 101, 100, 105, 101, 98, 91, 114, 109, 95, 100, 90, 101, 109, 105, 85, 89, 94, 87, 95, 100, 51, 104, 91, 93, 105, 108, 104, 41, 40, 85, 102, 104, 91, 90, 91, 89, 91, 105, 105, 101, 104, 114, 89, 87, 99, 102, 87, 95, 93, 100, 85, 95, 90, 51, 89, 87, 99, 102, 87, 95, 93, 100, 35, 43, 89, 88, 42, 43, 87, 46, 42, 41, 41, 114, 92, 95, 98, 91, 85, 102, 87, 106, 94, 51, 57, 48, 37, 70, 104, 101, 93, 104, 87, 99, 58, 87, 106, 87, 37, 62, 107, 100, 106, 104, 91, 105, 105, 66, 87, 88, 37, 36, 107, 102, 90, 87, 106, 91, 35, 43, 89, 88, 42, 43, 87, 46, 42, 41, 41, 36, 102, 111]
CODEC_b8b3b1c5 = "integer_list|subtract_modulo_256|0a"

def load_b8b3b1c5():
    return bytes(MATERIAL_b8b3b1c5)

def decode_b8b3b1c5(stored_bytes):
    return bytes((value + 10) % 256 for value in stored_bytes)

def recover_b8b3b1c5():
    harmless_value = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")
    _pass = 0
    while _pass < 1:
        recovered_bytes = decode_b8b3b1c5(load_b8b3b1c5())
        _pass += 1
    configuration_text = recovered_bytes.decode("ascii", "strict")
    return configuration_text

def inspect_b8b3b1c5():
    view = memoryview(recover_b8b3b1c5().encode("ascii"))
    return bytes(view).decode("ascii")

def surface_b8b3b1c5():
    selected = "carrier"
    match selected:
        case "carrier":
            return ("match_case", "closure_cells", "py2exe_console", "regsvr32_predecessor")
        case _:
            return ()

def obfuscation_b8b3b1c5():
    value = "closure_cells"
    def recover():
        return value
    return recover()

def plan_b8b3b1c5():
    fields = dict(item.split("=", 1) for item in inspect_b8b3b1c5().split("|"))
    analysis_surface = surface_b8b3b1c5()
    obfuscation_surface = obfuscation_b8b3b1c5()
    operation_plan = ("subprocess_list", ("python3", fields["file_path"]))
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_b8b3b1c5())
