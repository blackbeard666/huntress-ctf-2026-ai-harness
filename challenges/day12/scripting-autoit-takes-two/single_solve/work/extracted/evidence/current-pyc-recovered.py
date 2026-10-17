#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_bfef09a4 = "763d327c73746570733d6c6f636174655f6c6f63616c2c64697370617463685f70726f636573737c616461707465723d72656e616d65645f696e7465727072657465725f617267767c73746167655f636f756e743d317c73796e7461783d636c6f737572655f666163746f72797c6f62667573636174696f6e3d6368725f6a6f696e7c636172726965723d686173685f62617365645f7079635f63757272656e747c77696e646f77735f636861696e3d707974686f6e775f68696464656e5f636f6e736f6c657c63616d706169676e5f69643d63616d706169676e2d346331666366353361327c66696c655f706174683d433a2f50726f6772616d446174612f48756e74726573734c61622f2e7570646174652d346331666366353361322e7079"

CODEC_bfef09a4 = "hex_literal|identity|"



def load_bfef09a4():

    return bytes.fromhex(MATERIAL_bfef09a4)



def decode_bfef09a4(v_a19c):

    return bytes(v_a19c)



def recover_bfef09a4():

    v_d41a = ":".join(("north", "south"))

    v_f602 = decode_bfef09a4

    v_b27e = v_f602(load_bfef09a4())

    v_c304 = v_b27e.decode("ascii", "strict")

    return v_c304



def inspect_bfef09a4():

    stream = io.BytesIO(recover_bfef09a4().encode("ascii"))

    return stream.read().decode("ascii")



def surface_bfef09a4():

    values = ("closure_factory", "chr_join", "hash_based_pyc_current", "pythonw_hidden_console")

    def inner():

        return values

    return inner()



def obfuscation_bfef09a4():

    return "".join(chr(value) for value in (99, 104, 114, 95, 106, 111, 105, 110))



def plan_bfef09a4():

    fields = dict(item.split("=", 1) for item in inspect_bfef09a4().split("|"))

    analysis_surface = surface_bfef09a4()

    obfuscation_surface = obfuscation_bfef09a4()

    operation_plan = ("renamed_interpreter_argv", ("python3", fields["file_path"]))

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_bfef09a4())

