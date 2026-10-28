#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_94033e3e = "763d327c73746570733d616371756972655f72656d6f74652c77726974655f66696c657c616461707465723d75726c6c69625f746f5f706174687c73746167655f636f756e743d317c73796e7461783d67656e657261746f725f706970656c696e657c6f62667573636174696f6e3d66737472696e675f667261676d656e74737c636172726965723d7079696e7374616c6c65725f6f6e6566696c657c77696e646f77735f636861696e3d6d736874615f746f5f707974686f6e7c63616d706169676e5f69643d63616d706169676e2d623164373561653161367c75726c3d68747470733a2f2f623164373561653161362e6578616d706c652e696e76616c69642f31643832613239352e70797c757365725f6167656e743d48756e7472657373507974686f6e2f623164373561653161367c66696c655f706174683d433a2f50726f6772616d446174612f48756e74726573734c61622f2e7570646174652d623164373561653161362e7079"

CODEC_94033e3e = "hex_literal|identity|"



def load_94033e3e():

    return bytes.fromhex(MATERIAL_94033e3e)



def decode_94033e3e(item1):

    return bytes(item1)



def recover_94033e3e():

    item4 = "left" if 2 > 1 else "right"

    _pass = 0

    while _pass < 1:

        item2 = decode_94033e3e(load_94033e3e())

        _pass += 1

    item3 = item2.decode("ascii", "strict")

    return item3



def inspect_94033e3e():

    view = memoryview(recover_94033e3e().encode("ascii"))

    return bytes(view).decode("ascii")



def surface_94033e3e():

    stream = (item for item in ("generator_pipeline", "fstring_fragments", "pyinstaller_onefile", "mshta_to_python"))

    return tuple(stream)



def obfuscation_94033e3e():

    left, right = "fstrin", "g_fragments"

    return f"{left}{right}"



def plan_94033e3e():

    fields = dict(item.split("=", 1) for item in inspect_94033e3e().split("|"))

    analysis_surface = surface_94033e3e()

    obfuscation_surface = obfuscation_94033e3e()

    operation_plan = ("urllib_to_path", fields["url"], fields["file_path"])

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_94033e3e())

