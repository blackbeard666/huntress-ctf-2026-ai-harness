#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_4bccc079 = [197, 252, 152, 175, 202, 243, 196, 246, 196, 162, 150, 187, 207, 188, 211, 187, 134, 226, 139, 212, 160, 211, 188, 212, 168, 145, 245, 194, 167, 158, 169, 155, 169, 207, 251, 214, 184, 223, 182, 215, 167, 202, 171, 200, 245, 145, 248, 167, 201, 174, 199, 166, 214, 187, 218, 185, 197, 160, 216, 189, 226, 140, 227, 139, 255, 134, 246, 169, 221, 190, 219, 169, 192, 164, 153, 247, 158, 255, 151, 244, 171, 216, 175, 192, 164, 202, 163, 212, 168, 205, 174, 220, 169, 198, 181, 234, 157, 252, 142, 179, 193, 164, 205, 191, 205, 172, 207, 179, 202, 166, 200, 167, 248, 149, 231, 136, 238, 157, 243, 146, 224, 148, 169, 199, 168, 193, 181, 212, 183, 196, 177, 215, 181, 218, 166, 213, 187, 212, 189, 201, 170, 196, 177, 215, 136, 230, 143, 238, 130, 242, 207, 183, 214, 162, 204, 181, 198, 186, 139, 182, 194, 172, 217, 182, 213, 138, 239, 136, 233, 157, 238, 146, 235, 147, 252, 142, 254, 161, 198, 168, 193, 177, 193, 160, 205, 240, 130, 231, 147, 227, 130, 230, 135, 251, 149, 250, 147, 231, 134, 244, 129, 230, 143, 233, 135, 232, 139, 212, 186, 200, 189, 201, 172, 222, 242, 156, 243, 154, 238, 143, 253, 136, 239, 134, 224, 142, 225, 130, 221, 184, 220, 179, 208, 181, 209, 236, 159, 239, 138, 254, 141, 241, 195, 254]

CODEC_4bccc079 = "reversed_integer_list|rolling_xor|88"



def load_4bccc079():

    return bytes(reversed(MATERIAL_4bccc079))



def decode_4bccc079(EnCoDeD_Bytes):

    DeCoDeD_Bytes = bytearray()

    PrEvIoUs = 136

    for value in EnCoDeD_Bytes:

        DeCoDeD_Bytes.append(value ^ PrEvIoUs)

        PrEvIoUs = value

    return bytes(DeCoDeD_Bytes)



def recover_4bccc079():

    NeUtRaL = ":".join(("north", "south"))

    DeCoDeD_Bytes = decode_4bccc079(load_4bccc079())

    DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")

    return DeScRiPtOr_Text



def inspect_4bccc079():

    return recover_4bccc079()



def surface_4bccc079():

    return ("plain_functions", "transform_only", "raw_source", "direct_python_exe")



def obfuscation_4bccc079():

    return "transform_only"



def plan_4bccc079():

    fields = dict(item.split("=", 1) for item in inspect_4bccc079().split("|"))

    analysis_surface = surface_4bccc079()

    obfuscation_surface = obfuscation_4bccc079()

    operation_plan = ("report", fields.get("host_id", ""))

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_4bccc079())

