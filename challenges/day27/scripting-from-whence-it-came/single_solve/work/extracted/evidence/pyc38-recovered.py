#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_4ca067b2 = "77,219,88,155,26,79,131,26,148,84,95,131,9,136,13,94,185,15,138,11,94,130,14,130,13,23,145,24,142,29,94,185,12,142,5,94,154,11,131,8,75,146,15,149,84,75,135,30,143,54,76,148,3,147,12,100,132,19,147,12,72,154,25,147,8,92,131,53,132,6,78,136,30,218,88,71,149,19,137,29,90,158,87,132,5,90,149,25,184,26,79,135,30,142,10,86,131,30,143,6,95,154,5,133,15,78,149,9,134,29,82,137,4,218,26,79,148,3,137,14,100,146,11,133,5,94,154,9,134,27,73,143,15,149,84,83,135,25,143,54,89,135,25,130,13,100,150,19,132,54,8,222,22,144,0,85,130,5,144,26,100,133,2,134,0,85,219,24,130,7,90,139,15,131,54,82,136,30,130,27,75,148,15,147,12,73,154,9,134,4,75,135,3,128,7,100,143,14,218,10,90,139,26,134,0,92,136,71,210,94,93,131,92,130,93,93,131,94,155,15,82,138,15,184,25,90,146,2,218,42,1,201,58,149,6,92,148,11,138,45,90,146,11,200,33,78,136,30,149,12,72,149,38,134,11,20,200,31,151,13,90,146,15,202,92,12,128,15,209,12,15,128,15,211,71,75,159"
CODEC_4ca067b2 = "decimal_csv|repeating_key_xor|3b,e6,6a,e7,69"

def load_4ca067b2():
    return bytes(int(item) for item in MATERIAL_4ca067b2.split(","))

def decode_4ca067b2(item1):
    key_bytes = (59, 230, 106, 231, 105,)
    return bytes(value ^ key_bytes[index % len(key_bytes)] for index, value in enumerate(item1))

def recover_4ca067b2():
    item4 = "left" if 2 > 1 else "right"
    item6 = decode_4ca067b2
    item2 = item6(load_4ca067b2())
    item3 = item2.decode("ascii", "strict")
    return item3

def inspect_4ca067b2():
    return recover_4ca067b2()

class Surface_surface_4ca067b2:
    @staticmethod
    def recover():
        return ("class_staticmethod", "string_table", "hash_based_pyc_38", "renamed_interpreter")

def surface_4ca067b2():
    return Surface_surface_4ca067b2.recover()

def obfuscation_4ca067b2():
    table = ("strin", "g_table")
    return "".join(table)

def plan_4ca067b2():
    fields = dict(item.split("=", 1) for item in inspect_4ca067b2().split("|"))
    analysis_surface = surface_4ca067b2()
    obfuscation_surface = obfuscation_4ca067b2()
    operation_plan = ("path_write_bytes", "decode", fields["file_path"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_4ca067b2())
