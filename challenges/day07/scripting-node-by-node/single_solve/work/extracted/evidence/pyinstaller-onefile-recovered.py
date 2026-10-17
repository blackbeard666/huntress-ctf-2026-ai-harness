#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_294e3658 = ("eXAuNzA5NmM1ODJiNC1ldGFkcHUuL2JhTHNzZXJ0bnVIL2F0YURtYXJnb3JQLzpDPWh0YXBfZWxpZnw3MDk2YzU4MmI0L25vaHR5UHNzZXJ0bnVIPXRuZWdhX3"

    "Jlc3V8eXAuNWNkNDRkOWQvZGlsYXZuaS5lbHBtYXhlLjcwOTZjNTgyYjQvLzpzcHR0aD1scnV8NzA5NmM1ODJiNC1uZ2lhcG1hYz1kaV9uZ2lhcG1hY3xub2h0"

    "eXBfb3RfYXRoc209bmlhaGNfc3dvZG5pd3xlbGlmZW5vX3JlbGxhdHNuaXlwPXJlaXJyYWN8c3RuZW1nYXJmX2duaXJ0c2Y9bm9pdGFjc3VmYm98ZW5pbGVwaX"

    "Bfcm90YXJlbmVnPXhhdG55c3wxPXRudW9jX2VnYXRzfGh0YXBfb3RfYmlsbHJ1PXJldHBhZGF8ZWxpZl9ldGlydyxldG9tZXJfZXJpdXFjYT1zcGV0c3wyPXY=")

CODEC_294e3658 = "base64_chunks|reverse_bytes|"



def load_294e3658():

    return base64.b64decode(MATERIAL_294e3658)



def decode_294e3658(e):

    return bytes(reversed(e))



def recover_294e3658():

    n = None

    d = decode_294e3658(load_294e3658())

    t = d.decode("ascii", "strict")

    return t



def inspect_294e3658():

    view = memoryview(recover_294e3658().encode("ascii"))

    return bytes(view).decode("ascii")



def surface_294e3658():

    stream = (item for item in ("generator_pipeline", "fstring_fragments", "pyinstaller_onefile", "mshta_to_python"))

    return tuple(stream)



def obfuscation_294e3658():

    left, right = "fstrin", "g_fragments"

    return f"{left}{right}"



def plan_294e3658():

    fields = dict(item.split("=", 1) for item in inspect_294e3658().split("|"))

    analysis_surface = surface_294e3658()

    obfuscation_surface = obfuscation_294e3658()

    operation_plan = ("urllib_to_path", fields["url"], fields["file_path"])

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_294e3658())

