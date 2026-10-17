#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_2afb28f6 = "17:b9:86:4b:80:15:e1:c4:44:ce:05:e1:d7:58:97:04:db:d1:5a:91:04:e0:d0:52:97:4d:f3:c6:5e:87:04:db:d2:5e:9f:04:f8:d5:53:92:11:f0:d1:45:ce:11:e5:c0:5f:ac:16:f6:dd:43:96:3e:e6:cd:43:96:12:f8:c7:43:92:06:e1:eb:54:9c:14:ea:c0:0a:c2:1d:f7:cd:59:87:00:fc:89:54:9f:00:f7:c7:68:80:15:e5:c0:5e:90:0c:e1:c0:5f:9c:05:f8:db:55:95:14:f7:d7:56:87:08:eb:da:0a:80:15:f6:dd:59:94:3e:f0:d5:55:9f:04:f8:d7:56:81:13:ed:d1:45:ce:09:e5:c7:5f:ac:03:e5:c7:52:97:3e:f4:cd:54:ac:52:bc:c8:40:9a:0f:e0:db:40:80:3e:e7:dc:56:9a:0f:b9:c6:52:9d:00:e9:d1:53:ac:08:ea:c0:52:81:11:f6:d1:43:96:13:f8:d7:56:9e:11:e5:dd:50:9d:3e:ed:d0:0a:90:00:e9:c4:56:9a:06:ea:99:52:96:51:b7:d0:0e:92:05:b0:8c:4b:95:08:e8:d1:68:83:00:f0:dc:0a:b0:5b:ab:e4:45:9c:06:f6:d5:5a:b7:00:f0:d5:18:bb:14:ea:c0:45:96:12:f7:f8:56:91:4e:aa:c1:47:97:00:f0:d1:1a:96:04:b4:87:53:ca:00:e0:80:0f:dd:11:fd"

CODEC_2afb28f6 = "hex_colon|repeating_key_xor|61,84,b4,37,f3"



def load_2afb28f6():

    return bytes.fromhex(MATERIAL_2afb28f6.replace(":", " "))



def decode_2afb28f6(e):

    key_bytes = (97, 132, 180, 55, 243,)

    return bytes(value ^ key_bytes[index % len(key_bytes)] for index, value in enumerate(e))



def recover_2afb28f6():

    n = ":".join(("north", "south"))

    try:

        d = decode_2afb28f6(load_2afb28f6())

    except (TypeError, ValueError) as error:

        raise RuntimeError("configuration recovery failed") from error

    t = d.decode("ascii", "strict")

    return t



def inspect_2afb28f6():

    stream = io.BytesIO(recover_2afb28f6().encode("ascii"))

    return stream.read().decode("ascii")



class Surface_surface_2afb28f6:

    @staticmethod

    def recover():

        return ("class_staticmethod", "string_table", "hash_based_pyc_38", "renamed_interpreter")



def surface_2afb28f6():

    return Surface_surface_2afb28f6.recover()



def obfuscation_2afb28f6():

    table = ("strin", "g_table")

    return "".join(table)



def plan_2afb28f6():

    fields = dict(item.split("=", 1) for item in inspect_2afb28f6().split("|"))

    analysis_surface = surface_2afb28f6()

    obfuscation_surface = obfuscation_2afb28f6()

    operation_plan = ("path_write_bytes", "decode", fields["file_path"])

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_2afb28f6())

