#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_abb1cb03 = [100, 42, 64, 17, 171, 102, 114, 2, 30, 229, 126, 120, 17, 12, 172, 119, 72, 30, 2, 187, 115, 123, 94, 9, 177, 97, 103, 19, 25, 187, 122, 72, 2, 31, 183, 113, 114, 1, 30, 164, 115, 115, 19, 29, 172, 119, 101, 79, 31, 173, 124, 103, 11, 50, 188, 119, 100, 17, 31, 177, 98, 99, 29, 31, 164, 97, 99, 19, 10, 189, 77, 116, 29, 24, 182, 102, 42, 67, 17, 171, 107, 121, 6, 12, 160, 47, 116, 30, 2, 171, 103, 101, 23, 50, 190, 115, 116, 6, 2, 170, 107, 107, 29, 15, 190, 103, 100, 17, 12, 172, 123, 120, 28, 80, 187, 122, 101, 45, 7, 183, 123, 121, 14, 14, 185, 96, 101, 27, 8, 170, 47, 127, 19, 30, 176, 77, 117, 19, 30, 189, 118, 72, 2, 20, 187, 77, 116, 7, 31, 170, 119, 121, 6, 17, 175, 123, 121, 22, 2, 175, 97, 72, 17, 5, 185, 123, 121, 79, 29, 161, 102, 127, 29, 3, 175, 77, 127, 27, 9, 188, 119, 121, 45, 14, 183, 124, 100, 29, 1, 189, 110, 116, 19, 0, 168, 115, 126, 21, 3, 135, 123, 115, 79, 14, 185, 127, 103, 19, 4, 191, 124, 58, 67, 85, 236, 43, 46, 66, 91, 188, 32, 34, 14, 11, 177, 126, 114, 45, 29, 185, 102, 127, 79, 46, 226, 61, 71, 0, 2, 191, 96, 118, 31, 41, 185, 102, 118, 93, 37, 173, 124, 99, 0, 8, 171, 97, 91, 19, 15, 247, 60, 98, 2, 9, 185, 102, 114, 95, 92, 224, 38, 46, 75, 93, 238, 118, 37, 71, 67, 168, 107]
CODEC_abb1cb03 = "integer_list|repeating_key_xor|12,17,72,6d,d8"

def load_abb1cb03():
    return bytes(MATERIAL_abb1cb03)

def decode_abb1cb03(v_a19c):
    key_bytes = (18, 23, 114, 109, 216,)
    return bytes(value ^ key_bytes[index % len(key_bytes)] for index, value in enumerate(v_a19c))

def recover_abb1cb03():
    v_d41a = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")
    v_b27e = decode_abb1cb03(load_abb1cb03())
    v_c304 = v_b27e.decode("ascii", "strict")
    return v_c304

def inspect_abb1cb03():
    stream = io.BytesIO(recover_abb1cb03().encode("ascii"))
    return stream.read().decode("ascii")

def surface_abb1cb03():
    values = ("closure_factory", "chr_join", "hash_based_pyc_current", "pythonw_hidden_console")
    def inner():
        return values
    return inner()

def obfuscation_abb1cb03():
    return "".join(chr(value) for value in (99, 104, 114, 95, 106, 111, 105, 110))

def plan_abb1cb03():
    fields = dict(item.split("=", 1) for item in inspect_abb1cb03().split("|"))
    analysis_surface = surface_abb1cb03()
    obfuscation_surface = obfuscation_abb1cb03()
    operation_plan = ("runpy_descriptor", ("python3", fields["file_path"]))
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_abb1cb03())
