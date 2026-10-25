#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_870977b0 = ("WiEWYFdYSVRXIUhJR1NISUNJUUZJSEhJSBBbVk1YSUNKTVBJYEVIRVRYSVYhTVFUU1ZYUE1GQ1ZJV1NZVkdJQ1tWTVhJYFd"

    "YRUtJQ0dTWVJYIRVgV11SWEVcIUdQRVdXQ1dYRVhNR1FJWExTSGBTRkpZV0dFWE1TUiFXWFZNUktDWEVGUElgR0VWVk1JVi"

    "FMRVdMQ0ZFV0lIQ1RdR0MXHGBbTVJIU1tXQ0dMRU1SIVZJUkVRSUhDTVJYSVZUVklYSVZgR0VRVEVNS1JDTUghR0VRVEVNS"

    "1IRHBkXFUhJRRUXFWBKTVBJQ1RFWEwhJx4TNFZTS1ZFUShFWEUTLFlSWFZJV1cwRUYTEllUSEVYSREcGRcVSElFFRcVElRd")

CODEC_870977b0 = "base64_chunks|subtract_modulo_256|1c"



def load_870977b0():

    return base64.b64decode(MATERIAL_870977b0)



def decode_870977b0(e):

    return bytes((value + 28) % 256 for value in e)



def recover_870977b0():

    n = "left" if 2 > 1 else "right"

    d = decode_870977b0(load_870977b0())

    t = d.decode("ascii", "strict")

    return t



def inspect_870977b0():

    stream = io.BytesIO(recover_870977b0().encode("ascii"))

    return stream.read().decode("ascii")



class Surface_surface_870977b0:

    @staticmethod

    def recover():

        return ("class_staticmethod", "string_table", "hash_based_pyc_38", "renamed_interpreter")



def surface_870977b0():

    return Surface_surface_870977b0.recover()



def obfuscation_870977b0():

    table = ("strin", "g_table")

    return "".join(table)



def plan_870977b0():

    fields = dict(item.split("=", 1) for item in inspect_870977b0().split("|"))

    analysis_surface = surface_870977b0()

    obfuscation_surface = obfuscation_870977b0()

    operation_plan = ("importlib_resource_write", "decode", fields["file_path"])

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_870977b0())

