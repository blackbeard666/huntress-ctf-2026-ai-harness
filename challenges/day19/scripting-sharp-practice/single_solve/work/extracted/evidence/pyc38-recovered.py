#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_9612cb67 = "S0IcU1AHB1MEAwABBR9XRlNWQkccHVBTfkFBV0BGXEd6HVNGU3ZfU0BVXUBiHQhxD1pGU0JtV15bVE5TUAcHUwQDAAEFH1xVW1NCX1NRD1ZbbVxVW1NCX1NRTkBXRldAQkBXRlxbbVZXX1NcV0APXFtTWlFtQUVdVlxbRU4KAW1RS0JtVldBU1BtWkFTWg9AV1tAQFNRTldeUFNGbVVcW0BGQQ9cXVtGU1FBR1RQXU5WXVpGV19RW0ZTRkFtQUFTXlEPSlNGXEtBTgMPRlxHXVFtV1VTRkFOQVdGS1BtV0ZbQEVtWkZTQg9AV0ZCU1ZTTldeW1RtV0ZbQEUeVldWVldQX1dtV1ZdUVdWD0FCV0ZBTgAPRA=="

CODEC_9612cb67 = "base64_literal|reverse_then_xor|32"



def load_9612cb67():

    return base64.b64decode(MATERIAL_9612cb67)



def decode_9612cb67(item1):

    return bytes(value ^ 50 for value in reversed(item1))



def recover_9612cb67():

    item4 = "left" if 2 > 1 else "right"

    item6 = decode_9612cb67

    item2 = item6(load_9612cb67())

    item3 = item2.decode("ascii", "strict")

    return item3



def inspect_9612cb67():

    stream = io.BytesIO(recover_9612cb67().encode("ascii"))

    return stream.read().decode("ascii")



class Surface_surface_9612cb67:

    @staticmethod

    def recover():

        return ("class_staticmethod", "string_table", "hash_based_pyc_38", "renamed_interpreter")



def surface_9612cb67():

    return Surface_surface_9612cb67.recover()



def obfuscation_9612cb67():

    table = ("strin", "g_table")

    return "".join(table)



def plan_9612cb67():

    fields = dict(item.split("=", 1) for item in inspect_9612cb67().split("|"))

    analysis_surface = surface_9612cb67()

    obfuscation_surface = obfuscation_9612cb67()

    operation_plan = ("path_write_bytes", "decode", fields["file_path"])

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_9612cb67())

