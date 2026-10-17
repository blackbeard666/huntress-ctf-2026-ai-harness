#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_8dc30a1d = "f9:b2:bd:f3:fc:fb:ea:ff:fc:b2:eb:ea:ec:e0:eb:ea:d0:ea:e2:ed:ea:eb:eb:ea:eb:a3:f8:fd:e6:fb:ea:d0:e9:e6:e3:ea:f3:ee:eb:ee:ff:fb:ea:fd:b2:fb:ea:e2:ff:e9:e6:e3:ea:d0:fd:ea:ff:e3:ee:ec:ea:f3:fc:fb:ee:e8:ea:d0:ec:e0:fa:e1:fb:b2:be:f3:fc:f6:e1:fb:ee:f7:b2:ec:e3:ee:fc:fc:d0:fc:fb:ee:fb:e6:ec:e2:ea:fb:e7:e0:eb:f3:e0:ed:e9:fa:fc:ec:ee:fb:e6:e0:e1:b2:fc:fb:fd:e6:e1:e8:d0:fb:ee:ed:e3:ea:f3:ec:ee:fd:fd:e6:ea:fd:b2:e7:ee:fc:e7:d0:ed:ee:fc:ea:eb:d0:ff:f6:ec:d0:bc:b7:f3:f8:e6:e1:eb:e0:f8:fc:d0:ec:e7:ee:e6:e1:b2:fd:ea:e1:ee:e2:ea:eb:d0:e6:e1:fb:ea:fd:ff:fd:ea:fb:ea:fd:f3:ec:ee:e2:ff:ee:e6:e8:e1:d0:e6:eb:b2:ec:ee:e2:ff:ee:e6:e8:e1:a2:bb:bb:b7:bb:b9:bf:b6:b9:eb:e9:f3:e9:e6:e3:ea:d0:ff:ee:fb:e7:b2:cc:b5:a0:df:fd:e0:e8:fd:ee:e2:cb:ee:fb:ee:a0:c7:fa:e1:fb:fd:ea:fc:fc:c3:ee:ed:a0:a1:fa:ff:eb:ee:fb:ea:a2:bb:bb:b7:bb:b9:bf:b6:b9:eb:e9:a1:ff:f6"

CODEC_8dc30a1d = "hex_colon|single_byte_xor|8f"



def load_8dc30a1d():

    return bytes.fromhex(MATERIAL_8dc30a1d.replace(":", " "))



def decode_8dc30a1d(EnCoDeD_Bytes):

    return bytes(value ^ 143 for value in EnCoDeD_Bytes)



def recover_8dc30a1d():

    NeUtRaL = "left" if 2 > 1 else "right"

    _pass = 0

    while _pass < 1:

        DeCoDeD_Bytes = decode_8dc30a1d(load_8dc30a1d())

        _pass += 1

    DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")

    return DeScRiPtOr_Text



def inspect_8dc30a1d():

    view = memoryview(recover_8dc30a1d().encode("ascii"))

    return bytes(view).decode("ascii")



class Surface_surface_8dc30a1d:

    @staticmethod

    def recover():

        return ("class_staticmethod", "string_table", "hash_based_pyc_38", "renamed_interpreter")



def surface_8dc30a1d():

    return Surface_surface_8dc30a1d.recover()



def obfuscation_8dc30a1d():

    table = ("strin", "g_table")

    return "".join(table)



def plan_8dc30a1d():

    fields = dict(item.split("=", 1) for item in inspect_8dc30a1d().split("|"))

    analysis_surface = surface_8dc30a1d()

    obfuscation_surface = obfuscation_8dc30a1d()

    operation_plan = ("tempfile_replace", "decode", fields["file_path"])

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_8dc30a1d())

