#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_2929c3e6 = "79:70:2e:63:63:63:32:66:64:63:34:62:64:2d:65:74:61:64:70:75:2e:2f:62:61:4c:73:73:65:72:74:6e:75:48:2f:61:74:61:44:6d:61:72:67:6f:72:50:2f:3a:43:3d:68:74:61:70:5f:65:6c:69:66:7c:63:63:63:32:66:64:63:34:62:64:2d:6e:67:69:61:70:6d:61:63:3d:64:69:5f:6e:67:69:61:70:6d:61:63:7c:72:6f:74:70:69:72:63:73:65:64:5f:79:65:6b:5f:6e:75:72:3d:6e:69:61:68:63:5f:73:77:6f:64:6e:69:77:7c:69:73:6d:5f:65:7a:65:65:72:66:5f:78:63:3d:72:65:69:72:72:61:63:7c:6e:61:6c:70:5f:65:6d:61:6e:5f:65:76:69:74:63:65:6c:66:65:72:3d:6e:6f:69:74:61:63:73:75:66:62:6f:7c:6c:6f:63:6f:74:6f:72:70:5f:72:6f:74:61:72:65:74:69:3d:78:61:74:6e:79:73:7c:31:3d:74:6e:75:6f:63:5f:65:67:61:74:73:7c:65:74:69:72:77:5f:65:63:72:75:6f:73:65:72:5f:62:69:6c:74:72:6f:70:6d:69:3d:72:65:74:70:61:64:61:7c:65:6c:69:66:5f:65:74:69:72:77:2c:64:65:64:64:65:62:6d:65:5f:65:64:6f:63:65:64:3d:73:70:65:74:73:7c:32:3d:76"

CODEC_2929c3e6 = "hex_colon|reverse_bytes|"



def load_2929c3e6():

    return bytes.fromhex(MATERIAL_2929c3e6.replace(":", " "))



def decode_2929c3e6(item1):

    return bytes(reversed(item1))



def recover_2929c3e6():

    item4 = ":".join(("north", "south"))

    for _pass in range(1):

        item2 = decode_2929c3e6(load_2929c3e6())

    item3 = item2.decode("ascii", "strict")

    return item3



def inspect_2929c3e6():

    view = memoryview(recover_2929c3e6().encode("ascii"))

    return bytes(view).decode("ascii")



def surface_2929c3e6():

    iterator = iter(("iterator_protocol", "reflective_name_plan", "cx_freeze_msi", "run_key_descriptor"))

    return tuple(iterator)



def obfuscation_2929c3e6():

    reflection_plan = ("__import__", "getattr", "reflective_name_plan")

    return reflection_plan[-1]



def plan_2929c3e6():

    fields = dict(item.split("=", 1) for item in inspect_2929c3e6().split("|"))

    analysis_surface = surface_2929c3e6()

    obfuscation_surface = obfuscation_2929c3e6()

    operation_plan = ("importlib_resource_write", "decode", fields["file_path"])

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_2929c3e6())

