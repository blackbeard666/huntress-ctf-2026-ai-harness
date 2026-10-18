#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_96121679 = "763d327c73746570733d636f6c6c6563745f6c6f63616c2c656e636f64655f617263686976652c7472616e736d69745f72656d6f74657c616461707465723d736f636b65745f73747265616d5f706c616e7c73746167655f636f756e743d317c73796e7461783d64696374696f6e6172795f64697370617463687c6f62667573636174696f6e3d6c616d6264615f696e646972656374696f6e7c636172726965723d7079696e7374616c6c65725f6f6e656469727c77696e646f77735f636861696e3d72756e646c6c33325f7072656465636573736f727c63616d706169676e5f69643d63616d706169676e2d333964393366376362347c75706c6f61645f75726c3d68747470733a2f2f333964393366376362342e6578616d706c652e696e76616c69642f75706c6f61647c617263686976655f706174683d433a2f50726f6772616d446174612f48756e74726573734c61622f63616368652d333964393366376362342e7a6970"

CODEC_96121679 = "hex_literal|identity|"



def load_96121679():

    return bytes.fromhex(MATERIAL_96121679)



def decode_96121679(stored_bytes):

    return bytes(stored_bytes)



def recover_96121679():

    harmless_value = None

    decoder_function = decode_96121679

    recovered_bytes = decoder_function(load_96121679())

    configuration_text = recovered_bytes.decode("ascii", "strict")

    return configuration_text



def inspect_96121679():

    view = memoryview(recover_96121679().encode("ascii"))

    return bytes(view).decode("ascii")



def surface_96121679():

    routes = {"selected": lambda: ("dictionary_dispatch", "lambda_indirection", "pyinstaller_onedir", "rundll32_predecessor")}

    return routes["selected"]()



def obfuscation_96121679():

    recover = lambda value: value

    return recover("lambda_indirection")



def plan_96121679():

    fields = dict(item.split("=", 1) for item in inspect_96121679().split("|"))

    analysis_surface = surface_96121679()

    obfuscation_surface = obfuscation_96121679()

    operation_plan = ("socket_stream_plan", fields["archive_path"], fields["upload_url"])

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_96121679())

