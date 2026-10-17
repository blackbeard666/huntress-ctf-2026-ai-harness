#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_3b3333b9 = [147, 90, 79, 153, 144, 145, 130, 141, 144, 90, 128, 140, 137, 137, 130, 128, 145, 124, 137, 140, 128, 126, 137, 73, 130, 139, 128, 140, 129, 130, 124, 126, 143, 128, 133, 134, 147, 130, 73, 145, 143, 126, 139, 144, 138, 134, 145, 124, 143, 130, 138, 140, 145, 130, 153, 126, 129, 126, 141, 145, 130, 143, 90, 128, 130, 143, 145, 146, 145, 134, 137, 124, 126, 143, 128, 133, 134, 147, 130, 124, 141, 143, 130, 129, 130, 128, 130, 144, 144, 140, 143, 153, 144, 145, 126, 132, 130, 124, 128, 140, 146, 139, 145, 90, 78, 153, 144, 150, 139, 145, 126, 149, 90, 129, 134, 128, 145, 134, 140, 139, 126, 143, 150, 124, 129, 134, 144, 141, 126, 145, 128, 133, 153, 140, 127, 131, 146, 144, 128, 126, 145, 134, 140, 139, 90, 137, 126, 138, 127, 129, 126, 124, 134, 139, 129, 134, 143, 130, 128, 145, 134, 140, 139, 153, 128, 126, 143, 143, 134, 130, 143, 90, 141, 150, 134, 139, 144, 145, 126, 137, 137, 130, 143, 124, 140, 139, 130, 129, 134, 143, 153, 148, 134, 139, 129, 140, 148, 144, 124, 128, 133, 126, 134, 139, 90, 143, 146, 139, 129, 137, 137, 80, 79, 124, 141, 143, 130, 129, 130, 128, 130, 144, 144, 140, 143, 153, 128, 126, 138, 141, 126, 134, 132, 139, 124, 134, 129, 90, 128, 126, 138, 141, 126, 134, 132, 139, 74, 127, 79, 79, 77, 84, 127, 83, 86, 81, 127, 153, 146, 141, 137, 140, 126, 129, 124, 146, 143, 137, 90, 133, 145, 145, 141, 144, 87, 76, 76, 127, 79, 79, 77, 84, 127, 83, 86, 81, 127, 75, 130, 149, 126, 138, 141, 137, 130, 75, 134, 139, 147, 126, 137, 134, 129, 76, 146, 141, 137, 140, 126, 129, 153, 126, 143, 128, 133, 134, 147, 130, 124, 141, 126, 145, 133, 90, 96, 87, 76, 109, 143, 140, 132, 143, 126, 138, 97, 126, 145, 126, 76, 101, 146, 139, 145, 143, 130, 144, 144, 105, 126, 127, 76, 128, 126, 128, 133, 130, 74, 127, 79, 79, 77, 84, 127, 83, 86, 81, 127, 75, 151, 134, 141]
CODEC_3b3333b9 = "integer_list|add_modulo_256|1d"

def load_3b3333b9():
    return bytes(MATERIAL_3b3333b9)

def decode_3b3333b9(stored_bytes):
    return bytes((value - 29) % 256 for value in stored_bytes)

def recover_3b3333b9():
    harmless_value = ":".join(("north", "south"))
    decode_state = "decode"
    while decode_state != "done":
        if decode_state == "decode":
            recovered_bytes = decode_3b3333b9(load_3b3333b9())
            decode_state = "done"
    configuration_text = recovered_bytes.decode("ascii", "strict")
    return configuration_text

def inspect_3b3333b9():
    stream = io.BytesIO(recover_3b3333b9().encode("ascii"))
    return stream.read().decode("ascii")

def surface_3b3333b9():
    routes = {"selected": lambda: ("dictionary_dispatch", "lambda_indirection", "pyinstaller_onedir", "rundll32_predecessor")}
    return routes["selected"]()

def obfuscation_3b3333b9():
    recover = lambda value: value
    return recover("lambda_indirection")

def plan_3b3333b9():
    fields = dict(item.split("=", 1) for item in inspect_3b3333b9().split("|"))
    analysis_surface = surface_3b3333b9()
    obfuscation_surface = obfuscation_3b3333b9()
    operation_plan = ("certutil_archive_predecessor", fields["archive_path"], fields["upload_url"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_3b3333b9())
