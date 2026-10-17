#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_d2534936 = [118, 61, 50, 124, 115, 116, 101, 112, 115, 61, 108, 111, 99, 97, 116, 101, 95, 108, 111, 99, 97, 108, 44, 100, 105, 115, 112, 97, 116, 99, 104, 95, 112, 114, 111, 99, 101, 115, 115, 124, 97, 100, 97, 112, 116, 101, 114, 61, 112, 121, 116, 104, 111, 110, 119, 95, 97, 114, 103, 118, 124, 115, 116, 97, 103, 101, 95, 99, 111, 117, 110, 116, 61, 49, 124, 115, 121, 110, 116, 97, 120, 61, 99, 108, 111, 115, 117, 114, 101, 95, 102, 97, 99, 116, 111, 114, 121, 124, 111, 98, 102, 117, 115, 99, 97, 116, 105, 111, 110, 61, 99, 104, 114, 95, 106, 111, 105, 110, 124, 99, 97, 114, 114, 105, 101, 114, 61, 104, 97, 115, 104, 95, 98, 97, 115, 101, 100, 95, 112, 121, 99, 95, 99, 117, 114, 114, 101, 110, 116, 124, 119, 105, 110, 100, 111, 119, 115, 95, 99, 104, 97, 105, 110, 61, 112, 121, 116, 104, 111, 110, 119, 95, 104, 105, 100, 100, 101, 110, 95, 99, 111, 110, 115, 111, 108, 101, 124, 99, 97, 109, 112, 97, 105, 103, 110, 95, 105, 100, 61, 99, 97, 109, 112, 97, 105, 103, 110, 45, 102, 51, 49, 51, 57, 54, 50, 102, 56, 53, 124, 102, 105, 108, 101, 95, 112, 97, 116, 104, 61, 67, 58, 47, 80, 114, 111, 103, 114, 97, 109, 68, 97, 116, 97, 47, 72, 117, 110, 116, 114, 101, 115, 115, 76, 97, 98, 47, 46, 117, 112, 100, 97, 116, 101, 45, 102, 51, 49, 51, 57, 54, 50, 102, 56, 53, 46, 112, 121]

CODEC_d2534936 = "reversed_integer_list|reverse_bytes|"



def load_d2534936():

    return bytes(reversed(MATERIAL_d2534936))



def decode_d2534936(EnCoDeD_Bytes):

    return bytes(reversed(EnCoDeD_Bytes))



def recover_d2534936():

    NeUtRaL = ":".join(("north", "south"))

    DeCoDeD_Bytes = decode_d2534936(load_d2534936())

    DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")

    return DeScRiPtOr_Text



def inspect_d2534936():

    stream = io.BytesIO(recover_d2534936().encode("ascii"))

    return stream.read().decode("ascii")



def surface_d2534936():

    values = ("closure_factory", "chr_join", "hash_based_pyc_current", "pythonw_hidden_console")

    def inner():

        return values

    return inner()



def obfuscation_d2534936():

    return "".join(chr(value) for value in (99, 104, 114, 95, 106, 111, 105, 110))



def plan_d2534936():

    fields = dict(item.split("=", 1) for item in inspect_d2534936().split("|"))

    analysis_surface = surface_d2534936()

    obfuscation_surface = obfuscation_d2534936()

    operation_plan = ("pythonw_argv", ("python3", fields["file_path"]))

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_d2534936())

