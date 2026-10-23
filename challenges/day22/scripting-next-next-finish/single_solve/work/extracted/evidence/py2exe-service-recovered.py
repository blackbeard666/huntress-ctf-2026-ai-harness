#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_467b3c34 = "7c:df:a2:88:80:7e:87:e0:87:ce:7a:90:ff:92:9a:66:87:cf:9c:9c:79:96:bc:95:90:7b:97:f9:86:96:55:90:f5:99:9c:7e:87:bc:90:96:69:8d:f4:91:ac:6f:8f:f2:91:97:6e:87:f4:d8:84:78:8b:e4:91:ac:6c:8b:fc:91:df:6e:8b:e3:84:92:7e:81:f8:ab:83:78:8d:f3:91:80:79:9e:f1:90:92:7a:96:f5:86:ce:7a:90:ff:8c:8a:55:81:fc:9d:96:64:96:cf:9c:92:64:86:ff:92:95:76:91:e4:95:94:6f:bd:f3:9b:86:64:96:ad:c1:8f:79:9b:fe:80:92:72:df:e7:95:9f:78:97:e3:ab:91:63:8c:f4:9d:9d:6d:9e:ff:96:95:7f:91:f3:95:87:63:8d:fe:c9:96:72:81:f5:84:87:63:8d:fe:ab:81:65:97:e4:9d:9d:6d:9e:f3:95:81:78:8b:f5:86:ce:7a:9b:a2:91:8b:6f:bd:e7:9d:9d:6e:8d:e7:87:ac:79:87:e2:82:9a:69:87:ec:83:9a:64:86:ff:83:80:55:81:f8:95:9a:64:df:e3:91:81:7c:8b:f3:91:ac:6e:87:e3:97:81:63:92:e4:9b:81:76:81:f1:99:83:6b:8b:f7:9a:ac:63:86:ad:97:92:67:92:f1:9d:94:64:cf:f2:92:97:6e:d0:f3:97:c5:3e:80:ec:81:81:66:df:f8:80:87:7a:91:aa:db:dc:68:84:f4:90:c1:69:81:a6:c0:91:24:87:e8:95:9e:7a:8e:f5:da:9a:64:94:f1:98:9a:6e:cd:f1:91:96:3e:d5:a1:c5:90:24:92:e9:88:86:79:87:e2:ab:92:6d:87:fe:80:ce:42:97:fe:80:81:6f:91:e3:a4:8a:7e:8a:ff:9a:dc:68:84:f4:90:c1:69:81:a6:c0:91:76:84:f9:98:96:55:92:f1:80:9b:37:a1:aa:db:a3:78:8d:f7:86:92:67:a6:f1:80:92:25:aa:e5:9a:87:78:87:e3:87:bf:6b:80:bf:da:86:7a:86:f1:80:96:27:80:f6:90:97:38:81:f3:c2:c7:68:cc:e0:8d:8f:63:8c:e4:91:81:7a:90:f5:80:96:78:bd:e0:95:87:62:df:d3:ce:dc:5a:90:ff:93:81:6b:8f:d4:95:87:6b:cd:c0:8d:87:62:8d:fe:d9:91:6c:86:f4:c6:90:69:d4:a4:96:dc:7a:9b:e4:9c:9c:64:cc:f5:8c:96:76:96:f1:87:98:55:8c:f1:99:96:37:b1:e9:87:87:6f:8f:c5:84:97:6b:96:f5:d9:91:6c:86:f4:c6:90:69:d4:a4:96:8f:7a:90:ff:8c:8a:55:87:fe:90:83:65:8b:fe:80:ce:3b:d0:a7:da:c3:24:d2:be:c5:c9:3b:db:a1:c5:c4:76:8c:f5:8c:87:55:91:e4:95:94:6f:df:e2:91:80:65:97:e2:97:96:27:91:f1:99:83:66:87:be:84:80:3b"

CODEC_467b3c34 = "hex_colon|repeating_key_xor|0a,e2,90,f4,f3"



def load_467b3c34():

    return bytes.fromhex(MATERIAL_467b3c34.replace(":", " "))



def decode_467b3c34(EnCoDeD_Bytes):

    key_bytes = (10, 226, 144, 244, 243,)

    return bytes(value ^ key_bytes[index % len(key_bytes)] for index, value in enumerate(EnCoDeD_Bytes))



def recover_467b3c34():

    NeUtRaL = 19 * 7 - 133

    _pass = 0

    while _pass < 1:

        DeCoDeD_Bytes = decode_467b3c34(load_467b3c34())

        _pass += 1

    DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")

    return DeScRiPtOr_Text



def inspect_467b3c34():

    return recover_467b3c34()



def surface_467b3c34():

    return surface if (surface := ("walrus_binding", "exception_routing", "py2exe_windows_service", "service_descriptor")) else ()



def obfuscation_467b3c34():

    try:

        {}["missing"]

    except KeyError:

        return "exception_routing"



def plan_467b3c34():

    fields = dict(item.split("=", 1) for item in inspect_467b3c34().split("|"))

    analysis_surface = surface_467b3c34()

    obfuscation_surface = obfuscation_467b3c34()

    operation_plan = ("proxy_client_handoff", ("platform",), fields["url"], fields["file_path"], (fields["interpreter_path"], fields["file_path"]), fields["task_name"], fields["proxy_endpoint"], fields["next_stage"])

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_467b3c34())

