#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_9d59fc58 = "76:3d:32:7c:73:74:65:70:73:3d:63:6f:6c:6c:65:63:74:5f:6c:6f:63:61:6c:2c:65:6e:63:6f:64:65:5f:61:72:63:68:69:76:65:2c:74:72:61:6e:73:6d:69:74:5f:72:65:6d:6f:74:65:7c:61:64:61:70:74:65:72:3d:6d:75:6c:74:69:70:61:72:74:5f:66:6f:72:6d:5f:70:6c:61:6e:7c:73:74:61:67:65:5f:63:6f:75:6e:74:3d:31:7c:73:79:6e:74:61:78:3d:64:69:63:74:69:6f:6e:61:72:79:5f:64:69:73:70:61:74:63:68:7c:6f:62:66:75:73:63:61:74:69:6f:6e:3d:6c:61:6d:62:64:61:5f:69:6e:64:69:72:65:63:74:69:6f:6e:7c:63:61:72:72:69:65:72:3d:70:79:69:6e:73:74:61:6c:6c:65:72:5f:6f:6e:65:64:69:72:7c:77:69:6e:64:6f:77:73:5f:63:68:61:69:6e:3d:72:75:6e:64:6c:6c:33:32:5f:70:72:65:64:65:63:65:73:73:6f:72:7c:63:61:6d:70:61:69:67:6e:5f:69:64:3d:63:61:6d:70:61:69:67:6e:2d:61:63:65:32:65:32:64:38:36:63:7c:75:70:6c:6f:61:64:5f:75:72:6c:3d:68:74:74:70:73:3a:2f:2f:61:63:65:32:65:32:64:38:36:63:2e:65:78:61:6d:70:6c:65:2e:69:6e:76:61:6c:69:64:2f:75:70:6c:6f:61:64:7c:61:72:63:68:69:76:65:5f:70:61:74:68:3d:43:3a:2f:50:72:6f:67:72:61:6d:44:61:74:61:2f:48:75:6e:74:72:65:73:73:4c:61:62:2f:63:61:63:68:65:2d:61:63:65:32:65:32:64:38:36:63:2e:7a:69:70"

CODEC_9d59fc58 = "hex_colon|identity|"



def load_9d59fc58():

    return bytes.fromhex(MATERIAL_9d59fc58.replace(":", " "))



def decode_9d59fc58(e):

    return bytes(e)



def recover_9d59fc58():

    n = None

    for _pass in range(1):

        d = decode_9d59fc58(load_9d59fc58())

    t = d.decode("ascii", "strict")

    return t



def inspect_9d59fc58():

    view = memoryview(recover_9d59fc58().encode("ascii"))

    return bytes(view).decode("ascii")



def surface_9d59fc58():

    routes = {"selected": lambda: ("dictionary_dispatch", "lambda_indirection", "pyinstaller_onedir", "rundll32_predecessor")}

    return routes["selected"]()



def obfuscation_9d59fc58():

    recover = lambda value: value

    return recover("lambda_indirection")



def plan_9d59fc58():

    fields = dict(item.split("=", 1) for item in inspect_9d59fc58().split("|"))

    analysis_surface = surface_9d59fc58()

    obfuscation_surface = obfuscation_9d59fc58()

    operation_plan = ("multipart_form_plan", fields["archive_path"], fields["upload_url"])

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_9d59fc58())

