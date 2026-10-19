#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_17d89e23 = "70:69:7a:2e:39:30:31:35:39:39:39:37:36:30:2d:65:68:63:61:63:2f:62:61:4c:73:73:65:72:74:6e:75:48:2f:61:74:61:44:6d:61:72:67:6f:72:50:2f:3a:43:3d:68:74:61:70:5f:65:76:69:68:63:72:61:7c:64:61:6f:6c:70:75:2f:64:69:6c:61:76:6e:69:2e:65:6c:70:6d:61:78:65:2e:39:30:31:35:39:39:39:37:36:30:2f:2f:3a:73:70:74:74:68:3d:6c:72:75:5f:64:61:6f:6c:70:75:7c:39:30:31:35:39:39:39:37:36:30:2d:6e:67:69:61:70:6d:61:63:3d:64:69:5f:6e:67:69:61:70:6d:61:63:7c:72:6f:73:73:65:63:65:64:65:72:70:5f:32:33:6c:6c:64:6e:75:72:3d:6e:69:61:68:63:5f:73:77:6f:64:6e:69:77:7c:72:69:64:65:6e:6f:5f:72:65:6c:6c:61:74:73:6e:69:79:70:3d:72:65:69:72:72:61:63:7c:6e:6f:69:74:63:65:72:69:64:6e:69:5f:61:64:62:6d:61:6c:3d:6e:6f:69:74:61:63:73:75:66:62:6f:7c:68:63:74:61:70:73:69:64:5f:79:72:61:6e:6f:69:74:63:69:64:3d:78:61:74:6e:79:73:7c:31:3d:74:6e:75:6f:63:5f:65:67:61:74:73:7c:6e:61:6c:70:5f:6d:61:65:72:74:73:5f:74:65:6b:63:6f:73:3d:72:65:74:70:61:64:61:7c:65:74:6f:6d:65:72:5f:74:69:6d:73:6e:61:72:74:2c:65:76:69:68:63:72:61:5f:65:64:6f:63:6e:65:2c:6c:61:63:6f:6c:5f:74:63:65:6c:6c:6f:63:3d:73:70:65:74:73:7c:32:3d:76"

CODEC_17d89e23 = "hex_colon|reverse_bytes|"



def load_17d89e23():

    return bytes.fromhex(MATERIAL_17d89e23.replace(":", " "))



def decode_17d89e23(EnCoDeD_Bytes):

    return bytes(reversed(EnCoDeD_Bytes))



def recover_17d89e23():

    NeUtRaL = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")

    DeCoDe_Target = decode_17d89e23

    DeCoDeD_Bytes = DeCoDe_Target(load_17d89e23())

    DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")

    return DeScRiPtOr_Text



def inspect_17d89e23():

    return recover_17d89e23()



def surface_17d89e23():

    routes = {"selected": lambda: ("dictionary_dispatch", "lambda_indirection", "pyinstaller_onedir", "rundll32_predecessor")}

    return routes["selected"]()



def obfuscation_17d89e23():

    recover = lambda value: value

    return recover("lambda_indirection")



def plan_17d89e23():

    fields = dict(item.split("=", 1) for item in inspect_17d89e23().split("|"))

    analysis_surface = surface_17d89e23()

    obfuscation_surface = obfuscation_17d89e23()

    operation_plan = ("socket_stream_plan", fields["archive_path"], fields["upload_url"])

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_17d89e23())

