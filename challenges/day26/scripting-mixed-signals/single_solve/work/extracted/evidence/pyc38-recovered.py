#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_0312d830 = "60271c665d5e4f5a5d274e4f4d594e4f494f574c4f4e4e4f4e16615c535e4f495053564f664b4e4b5a5e4f5c2753575a595c5e56534c495c4f5d595f5c4d4f49615c535e4f665d5e4b514f494d595f585e271b665d63585e4b62274d564b5d5d495d5e4b5e534d574f5e52594e66594c505f5d4d4b5e535958275d5e5c535851495e4b4c564f664d4b5c5c534f5c27524b5d52494c4b5d4f4e495a634d491d22666153584e59615d494d524b5358275c4f584b574f4e4953585e4f5c5a5c4f5e4f5c664d4b575a4b53515849534e274d4b575a4b535158174b1e211b214c1e1e201a665053564f495a4b5e52272d24193a5c59515c4b572e4b5e4b19325f585e5c4f5d5d364b4c19185f5a4e4b5e4f174b1e211b214c1e1e201a185a63"
CODEC_0312d830 = "hex_literal|subtract_modulo_256|16"

def load_0312d830():
    return bytes.fromhex(MATERIAL_0312d830)

def decode_0312d830(e):
    return bytes((value + 22) % 256 for value in e)

def recover_0312d830():
    n = "left" if 2 > 1 else "right"
    try:
        d = decode_0312d830(load_0312d830())
    except (TypeError, ValueError) as error:
        raise RuntimeError("configuration recovery failed") from error
    t = d.decode("ascii", "strict")
    return t

def inspect_0312d830():
    view = memoryview(recover_0312d830().encode("ascii"))
    return bytes(view).decode("ascii")

class Surface_surface_0312d830:
    @staticmethod
    def recover():
        return ("class_staticmethod", "string_table", "hash_based_pyc_38", "renamed_interpreter")

def surface_0312d830():
    return Surface_surface_0312d830.recover()

def obfuscation_0312d830():
    table = ("strin", "g_table")
    return "".join(table)

def plan_0312d830():
    fields = dict(item.split("=", 1) for item in inspect_0312d830().split("|"))
    analysis_surface = surface_0312d830()
    obfuscation_surface = obfuscation_0312d830()
    operation_plan = ("importlib_resource_write", "decode", fields["file_path"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_0312d830())
