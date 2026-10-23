#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_8e39701a = (121, 112, 46, 55, 49, 49, 49, 53, 53, 49, 99, 98, 48, 45, 101, 116, 97, 100, 112, 117, 46, 47, 98, 97, 76, 115, 115, 101, 114, 116, 110, 117, 72, 47, 97, 116, 97, 68, 109, 97, 114, 103, 111, 114, 80, 47, 58, 67, 61, 104, 116, 97, 112, 95, 101, 108, 105, 102, 124, 55, 49, 49, 49, 53, 53, 49, 99, 98, 48, 45, 110, 103, 105, 97, 112, 109, 97, 99, 61, 100, 105, 95, 110, 103, 105, 97, 112, 109, 97, 99, 124, 101, 108, 111, 115, 110, 111, 99, 95, 110, 101, 100, 100, 105, 104, 95, 119, 110, 111, 104, 116, 121, 112, 61, 110, 105, 97, 104, 99, 95, 115, 119, 111, 100, 110, 105, 119, 124, 116, 110, 101, 114, 114, 117, 99, 95, 99, 121, 112, 95, 100, 101, 115, 97, 98, 95, 104, 115, 97, 104, 61, 114, 101, 105, 114, 114, 97, 99, 124, 110, 105, 111, 106, 95, 114, 104, 99, 61, 110, 111, 105, 116, 97, 99, 115, 117, 102, 98, 111, 124, 121, 114, 111, 116, 99, 97, 102, 95, 101, 114, 117, 115, 111, 108, 99, 61, 120, 97, 116, 110, 121, 115, 124, 49, 61, 116, 110, 117, 111, 99, 95, 101, 103, 97, 116, 115, 124, 118, 103, 114, 97, 95, 114, 101, 116, 101, 114, 112, 114, 101, 116, 110, 105, 61, 114, 101, 116, 112, 97, 100, 97, 124, 115, 115, 101, 99, 111, 114, 112, 95, 104, 99, 116, 97, 112, 115, 105, 100, 44, 108, 97, 99, 111, 108, 95, 101, 116, 97, 99, 111, 108, 61, 115, 112, 101, 116, 115, 124, 50, 61, 118,)
CODEC_8e39701a = "integer_tuple|reverse_bytes|"

def load_8e39701a():
    return bytes(MATERIAL_8e39701a)

def decode_8e39701a(v_a19c):
    return bytes(reversed(v_a19c))

def recover_8e39701a():
    v_d41a = (3, 5, 8, 13)[1:3]
    try:
        v_b27e = decode_8e39701a(load_8e39701a())
    except (TypeError, ValueError) as error:
        raise RuntimeError("configuration recovery failed") from error
    v_c304 = v_b27e.decode("ascii", "strict")
    return v_c304

def inspect_8e39701a():
    return recover_8e39701a()

def surface_8e39701a():
    values = ("closure_factory", "chr_join", "hash_based_pyc_current", "pythonw_hidden_console")
    def inner():
        return values
    return inner()

def obfuscation_8e39701a():
    return "".join(chr(value) for value in (99, 104, 114, 95, 106, 111, 105, 110))

def plan_8e39701a():
    fields = dict(item.split("=", 1) for item in inspect_8e39701a().split("|"))
    analysis_surface = surface_8e39701a()
    obfuscation_surface = obfuscation_8e39701a()
    operation_plan = ("interpreter_argv", ("python3", fields["file_path"]))
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_8e39701a())
