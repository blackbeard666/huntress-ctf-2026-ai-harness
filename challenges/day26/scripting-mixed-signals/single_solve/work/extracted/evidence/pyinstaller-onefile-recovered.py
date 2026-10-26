#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_354e1b8b = [251, 198, 244, 136, 251, 143, 234, 154, 233, 212, 181, 214, 167, 210, 187, 201, 172, 243, 129, 228, 137, 230, 146, 247, 219, 172, 222, 183, 195, 166, 249, 159, 246, 154, 255, 131, 226, 134, 231, 151, 227, 134, 244, 201, 188, 206, 162, 206, 167, 197, 154, 238, 129, 222, 174, 207, 187, 211, 175, 220, 168, 201, 174, 203, 148, 247, 152, 237, 131, 247, 202, 251, 135, 244, 141, 227, 151, 246, 142, 179, 212, 177, 223, 186, 200, 169, 221, 178, 192, 159, 239, 134, 246, 147, 255, 150, 248, 157, 225, 142, 236, 138, 255, 140, 239, 142, 250, 147, 252, 146, 175, 201, 186, 206, 188, 213, 187, 220, 131, 229, 151, 246, 145, 252, 153, 247, 131, 240, 140, 239, 142, 252, 142, 231, 130, 240, 205, 189, 196, 173, 195, 176, 196, 165, 201, 165, 192, 178, 237, 130, 236, 137, 239, 134, 234, 143, 243, 132, 237, 131, 231, 136, 255, 140, 211, 176, 216, 185, 208, 190, 131, 238, 157, 245, 129, 224, 191, 203, 164, 251, 139, 242, 134, 238, 129, 239, 147, 240, 145, 252, 140, 237, 132, 227, 141, 210, 187, 223, 226, 129, 224, 141, 253, 156, 245, 146, 252, 209, 224, 217, 235, 220, 238, 218, 226, 131, 187, 137, 245, 128, 242, 158, 163, 203, 191, 203, 187, 200, 242, 221, 242, 195, 250, 200, 255, 205, 249, 193, 160, 152, 170, 132, 225, 153, 248, 149, 229, 137, 236, 194, 171, 197, 179, 210, 190, 215, 179, 156, 250, 205, 252, 157, 172, 207, 169, 204, 226, 146, 235, 151, 226, 145, 244, 134, 217, 184, 223, 186, 212, 160, 157, 213, 160, 206, 186, 200, 173, 222, 173, 253, 132, 240, 152, 247, 153, 182, 135, 190, 140, 187, 137, 189, 133, 228, 220, 238, 146, 244, 157, 241, 148, 203, 187, 218, 174, 198, 251, 184, 130, 173, 253, 143, 224, 135, 245, 148, 249, 189, 220, 168, 201, 230, 174, 219, 181, 193, 179, 214, 165, 214, 154, 251, 153, 182, 152, 237, 157, 249, 152, 236, 137, 164, 149, 172, 158, 169, 155, 175, 151, 246, 206, 252, 210, 162, 219]

CODEC_354e1b8b = "integer_list|rolling_xor|8d"



def load_354e1b8b():

    return bytes(MATERIAL_354e1b8b)



def decode_354e1b8b(e):

    d = bytearray()

    q = 141

    for value in e:

        d.append(value ^ q)

        q = value

    return bytes(d)



def recover_354e1b8b():

    n = (3, 5, 8, 13)[1:3]

    _pass = 0

    while _pass < 1:

        d = decode_354e1b8b(load_354e1b8b())

        _pass += 1

    t = d.decode("ascii", "strict")

    return t



def inspect_354e1b8b():

    view = memoryview(recover_354e1b8b().encode("ascii"))

    return bytes(view).decode("ascii")



def surface_354e1b8b():

    stream = (item for item in ("generator_pipeline", "fstring_fragments", "pyinstaller_onefile", "mshta_to_python"))

    return tuple(stream)



def obfuscation_354e1b8b():

    left, right = "fstrin", "g_fragments"

    return f"{left}{right}"



def plan_354e1b8b():

    fields = dict(item.split("=", 1) for item in inspect_354e1b8b().split("|"))

    analysis_surface = surface_354e1b8b()

    obfuscation_surface = obfuscation_354e1b8b()

    operation_plan = ("urllib_to_path", fields["url"], fields["file_path"])

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_354e1b8b())

