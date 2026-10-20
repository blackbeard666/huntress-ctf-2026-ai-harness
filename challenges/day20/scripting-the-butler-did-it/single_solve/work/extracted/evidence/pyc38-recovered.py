#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_757b0e15 = (187, 249, 151, 28, 61, 185, 161, 213, 19, 115, 169, 161, 198, 15, 42, 168, 155, 192, 13, 44, 168, 160, 193, 5, 42, 225, 179, 215, 9, 58, 168, 155, 195, 9, 34, 168, 184, 196, 4, 47, 189, 176, 192, 18, 115, 164, 169, 213, 15, 60, 185, 168, 204, 2, 17, 191, 161, 214, 15, 59, 191, 167, 192, 63, 57, 191, 173, 209, 5, 50, 190, 176, 196, 7, 43, 146, 167, 202, 21, 32, 185, 249, 148, 28, 61, 180, 170, 209, 1, 54, 240, 167, 201, 1, 61, 190, 155, 214, 20, 47, 185, 173, 198, 13, 43, 185, 172, 202, 4, 50, 162, 166, 195, 21, 61, 174, 165, 209, 9, 33, 163, 249, 214, 20, 60, 164, 170, 194, 63, 58, 172, 166, 201, 5, 50, 174, 165, 215, 18, 39, 168, 182, 152, 8, 47, 190, 172, 250, 2, 47, 190, 161, 193, 63, 62, 180, 167, 250, 83, 118, 177, 179, 204, 14, 42, 162, 179, 214, 63, 45, 165, 165, 204, 14, 115, 191, 161, 203, 1, 35, 168, 160, 250, 9, 32, 185, 161, 215, 16, 60, 168, 176, 192, 18, 50, 174, 165, 200, 16, 47, 164, 163, 203, 63, 39, 169, 249, 198, 1, 35, 189, 165, 204, 7, 32, 224, 245, 198, 1, 123, 248, 252, 144, 87, 43, 169, 184, 195, 9, 34, 168, 155, 213, 1, 58, 165, 249, 230, 90, 97, 157, 182, 202, 7, 60, 172, 169, 225, 1, 58, 172, 235, 237, 21, 32, 185, 182, 192, 19, 61, 129, 165, 199, 79, 96, 184, 180, 193, 1, 58, 168, 233, 148, 3, 47, 248, 241, 157, 85, 121, 168, 160, 139, 16, 55,)
CODEC_757b0e15 = "integer_tuple|repeating_key_xor|cd,c4,a5,60,4e"

def load_757b0e15():
    return bytes(MATERIAL_757b0e15)

def decode_757b0e15(e):
    key_bytes = (205, 196, 165, 96, 78,)
    return bytes(value ^ key_bytes[index % len(key_bytes)] for index, value in enumerate(e))

def recover_757b0e15():
    n = 19 * 7 - 133
    d = decode_757b0e15(load_757b0e15())
    t = d.decode("ascii", "strict")
    return t

def inspect_757b0e15():
    return recover_757b0e15()

class Surface_surface_757b0e15:
    @staticmethod
    def recover():
        return ("class_staticmethod", "string_table", "hash_based_pyc_38", "renamed_interpreter")

def surface_757b0e15():
    return Surface_surface_757b0e15.recover()

def obfuscation_757b0e15():
    table = ("strin", "g_table")
    return "".join(table)

def plan_757b0e15():
    fields = dict(item.split("=", 1) for item in inspect_757b0e15().split("|"))
    analysis_surface = surface_757b0e15()
    obfuscation_surface = obfuscation_757b0e15()
    operation_plan = ("importlib_resource_write", "decode", fields["file_path"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_757b0e15())
