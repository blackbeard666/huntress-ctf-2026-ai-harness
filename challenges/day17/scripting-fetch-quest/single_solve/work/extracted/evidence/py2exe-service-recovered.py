#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_df3ca245 = "84:4b:40:8a:81:82:73:7e:81:4b:7e:80:7d:74:77:7a:73:6d:76:7d:81:82:3a:6f:71:7f:83:77:80:73:6d:80:73:7b:7d:82:73:3a:72:73:71:7d:72:73:6d:73:7b:70:73:72:72:73:72:3a:85:80:77:82:73:6d:74:77:7a:73:3a:72:77:81:7e:6f:82:71:76:6d:7e:80:7d:71:73:81:81:8a:6f:72:6f:7e:82:73:80:4b:7e:80:7d:86:87:6d:71:7a:77:73:7c:82:6d:76:6f:7c:72:7d:74:74:8a:81:82:6f:75:73:6d:71:7d:83:7c:82:4b:43:8a:81:87:7c:82:6f:86:4b:85:6f:7a:80:83:81:6d:70:77:7c:72:77:7c:75:8a:7d:70:74:83:81:71:6f:82:77:7d:7c:4b:73:86:71:73:7e:82:77:7d:7c:6d:80:7d:83:82:77:7c:75:8a:71:6f:80:80:77:73:80:4b:7e:87:40:73:86:73:6d:85:77:7c:72:7d:85:81:6d:81:73:80:84:77:71:73:8a:85:77:7c:72:7d:85:81:6d:71:76:6f:77:7c:4b:81:73:80:84:77:71:73:6d:72:73:81:71:80:77:7e:82:7d:80:8a:71:6f:7b:7e:6f:77:75:7c:6d:77:72:4b:71:6f:7b:7e:6f:77:75:7c:3b:70:41:42:40:3f:46:3f:43:46:45:8a:83:80:7a:4b:76:82:82:7e:81:48:3d:3d:70:41:42:40:3f:46:3f:43:46:45:3c:73:86:6f:7b:7e:7a:73:3c:77:7c:84:6f:7a:77:72:3d:46:70:40:43:74:74:3f:72:3c:7e:87:8a:83:81:73:80:6d:6f:75:73:7c:82:4b:56:83:7c:82:80:73:81:81:5e:87:82:76:7d:7c:3d:70:41:42:40:3f:46:3f:43:46:45:8a:74:77:7a:73:6d:7e:6f:82:76:4b:51:48:3d:5e:80:7d:75:80:6f:7b:52:6f:82:6f:3d:56:83:7c:82:80:73:81:81:5a:6f:70:3d:3c:83:7e:72:6f:82:73:3b:70:41:42:40:3f:46:3f:43:46:45:3c:7e:87:8a:77:7c:82:73:80:7e:80:73:82:73:80:6d:7e:6f:82:76:4b:51:48:3d:5e:80:7d:75:80:6f:7b:52:6f:82:6f:3d:5e:87:82:76:7d:7c:3b:70:41:42:40:3f:46:3f:43:46:45:3d:7e:87:82:76:7d:7c:3c:73:86:73:8a:82:6f:81:79:6d:7c:6f:7b:73:4b:61:87:81:82:73:7b:63:7e:72:6f:82:73:3b:70:41:42:40:3f:46:3f:43:46:45:8a:7e:80:7d:86:87:6d:73:7c:72:7e:7d:77:7c:82:4b:3f:40:45:3c:3e:3c:3e:3c:3f:48:3f:43:46:47:3e:8a:7c:73:86:82:6d:81:82:6f:75:73:4b:80:73:81:7d:83:80:71:73:3b:81:6f:7b:7e:7a:73:3c:7e:81:3f"

CODEC_df3ca245 = "hex_colon|add_modulo_256|0e"



def load_df3ca245():

    return bytes.fromhex(MATERIAL_df3ca245.replace(":", " "))



def decode_df3ca245(item1):

    return bytes((value - 14) % 256 for value in item1)



def recover_df3ca245():

    item4 = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")

    item2 = decode_df3ca245(load_df3ca245())

    item3 = item2.decode("ascii", "strict")

    return item3



def inspect_df3ca245():

    return recover_df3ca245()



def surface_df3ca245():

    return surface if (surface := ("walrus_binding", "exception_routing", "py2exe_windows_service", "service_descriptor")) else ()



def obfuscation_df3ca245():

    try:

        {}["missing"]

    except KeyError:

        return "exception_routing"



def plan_df3ca245():

    fields = dict(item.split("=", 1) for item in inspect_df3ca245().split("|"))

    analysis_surface = surface_df3ca245()

    obfuscation_surface = obfuscation_df3ca245()

    operation_plan = ("proxy_client_handoff", ("platform",), fields["url"], fields["file_path"], (fields["interpreter_path"], fields["file_path"]), fields["task_name"], fields["proxy_endpoint"], fields["next_stage"])

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_df3ca245())

