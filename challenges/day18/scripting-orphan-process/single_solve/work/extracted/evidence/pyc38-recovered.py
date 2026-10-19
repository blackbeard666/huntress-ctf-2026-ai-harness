#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_4582fba1 = ("+Y8Pyoj7103FxuvXXtmf6u1Y25nq1lnTn6PFT9+P6u1b35fqzlzSmv/GWMTG5t9N2Yn73lTUpP3XTtmO/dFY6Yz920nTh/z"

    "GXNGe0NFSw5X7jwzKiPbcSdeDstFR14j87U7CmvvbXtue+9pS0ofg0FvDiOzTSd+U4Y9Owonm3Frpj+7QUdOH7NNPxJLqwA"

    "DemvzaYtSa/NdZ6Yv20WKFw/PFVNif4MVO6Zjn01TYxv3XU9eW6tZi35X710/GierGWMSH7NNQxprm1VPpkuuPXteW/9NU0"

    "ZWii1yOzLiACIGYus5b35fq7U3Xj+ePfozU38BS0Ynu33nXj+6ddcOV+8BYxYjD01+Z1frCWdeP6p8E18O4hQ+DzOyHE8aC")

CODEC_4582fba1 = "base64_chunks|repeating_key_xor|8f,b2,3d,b6,fb"



def load_4582fba1():

    return base64.b64decode(MATERIAL_4582fba1)



def decode_4582fba1(item1):

    key_bytes = (143, 178, 61, 182, 251,)

    return bytes(value ^ key_bytes[index % len(key_bytes)] for index, value in enumerate(item1))



def recover_4582fba1():

    item4 = ":".join(("north", "south"))

    _pass = 0

    while _pass < 1:

        item2 = decode_4582fba1(load_4582fba1())

        _pass += 1

    item3 = item2.decode("ascii", "strict")

    return item3



def inspect_4582fba1():

    return recover_4582fba1()



class Surface_surface_4582fba1:

    @staticmethod

    def recover():

        return ("class_staticmethod", "string_table", "hash_based_pyc_38", "renamed_interpreter")



def surface_4582fba1():

    return Surface_surface_4582fba1.recover()



def obfuscation_4582fba1():

    table = ("strin", "g_table")

    return "".join(table)



def plan_4582fba1():

    fields = dict(item.split("=", 1) for item in inspect_4582fba1().split("|"))

    analysis_surface = surface_4582fba1()

    obfuscation_surface = obfuscation_4582fba1()

    operation_plan = ("importlib_resource_write", "decode", fields["file_path"])

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_4582fba1())

