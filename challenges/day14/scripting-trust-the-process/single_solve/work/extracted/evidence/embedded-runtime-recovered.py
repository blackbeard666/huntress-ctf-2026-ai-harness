#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_1ed555cf = [221, 164, 212, 250, 158, 251, 137, 236, 154, 245, 150, 243, 129, 172, 222, 187, 215, 187, 218, 174, 221, 179, 218, 163, 211, 254, 140, 227, 142, 252, 157, 228, 148, 169, 204, 171, 202, 190, 205, 146, 230, 158, 251, 149, 233, 144, 224, 206, 251, 153, 168, 206, 250, 201, 254, 200, 173, 201, 228, 129, 245, 148, 240, 128, 245, 219, 244, 150, 247, 187, 200, 187, 222, 172, 216, 182, 195, 139, 164, 197, 177, 208, 148, 249, 152, 234, 141, 226, 144, 192, 239, 213, 150, 171, 195, 183, 214, 166, 249, 156, 240, 153, 255, 131, 182, 212, 229, 131, 183, 132, 179, 133, 224, 132, 169, 199, 160, 201, 168, 216, 181, 212, 183, 138, 238, 135, 216, 182, 209, 184, 217, 169, 196, 165, 198, 186, 200, 173, 217, 188, 206, 190, 204, 169, 221, 179, 218, 133, 225, 132, 233, 136, 230, 131, 241, 204, 162, 203, 170, 194, 161, 254, 141, 250, 149, 241, 159, 246, 129, 253, 152, 245, 156, 232, 134, 243, 129, 222, 176, 223, 183, 195, 186, 202, 149, 240, 156, 254, 159, 251, 159, 250, 152, 245, 144, 173, 223, 186, 211, 161, 211, 178, 209, 173, 195, 162, 206, 190, 225, 132, 244, 155, 247, 146, 228, 138, 239, 176, 220, 189, 213, 166, 212, 181, 216, 229, 139, 228, 141, 249, 152, 251, 136, 253, 155, 249, 150, 234, 142, 225, 137, 253, 152, 245, 150, 255, 139, 234, 158, 237, 178, 193, 178, 211, 191, 220, 225, 153, 248, 140, 226, 155, 232, 148, 167, 154, 238, 128, 245, 154, 249, 166, 195, 164, 197, 177, 194, 190, 202, 186, 211, 161, 194, 177, 198, 153, 246, 130, 221, 179, 220, 180, 192, 185, 201, 244, 134, 227, 151, 231, 134, 226, 131, 255, 154, 253, 156, 232, 155, 196, 176, 200, 173, 195, 156, 244, 151, 227, 130, 242, 129, 232, 140, 160, 210, 183, 195, 166, 212, 164, 214, 179, 199, 169, 192, 159, 250, 142, 239, 140, 227, 143, 163, 205, 162, 203, 191, 222, 172, 217, 190, 215, 177, 223, 176, 211, 140, 233, 141, 226, 129, 228, 128, 189, 206, 190, 219, 175, 220, 160, 146, 175]

CODEC_1ed555cf = "reversed_integer_list|rolling_xor|d9"



def load_1ed555cf():

    return bytes(reversed(MATERIAL_1ed555cf))



def decode_1ed555cf(item1):

    item2 = bytearray()

    item5 = 217

    for value in item1:

        item2.append(value ^ item5)

        item5 = value

    return bytes(item2)



def recover_1ed555cf():

    item4 = 19 * 7 - 133

    item6 = decode_1ed555cf

    item2 = item6(load_1ed555cf())

    item3 = item2.decode("ascii", "strict")

    return item3



def inspect_1ed555cf():

    view = memoryview(recover_1ed555cf().encode("ascii"))

    return bytes(view).decode("ascii")



class Surface_surface_1ed555cf:

    @staticmethod

    def recover():

        return ("class_staticmethod", "marshal_envelope_plan", "embeddable_python_runtime", "renamed_interpreter")



def surface_1ed555cf():

    return Surface_surface_1ed555cf.recover()



def obfuscation_1ed555cf():

    marshal_plan = {"format": "code_object", "action": "inspect_only", "label": "marshal_envelope_plan"}

    return marshal_plan["label"]



def plan_1ed555cf():

    fields = dict(item.split("=", 1) for item in inspect_1ed555cf().split("|"))

    analysis_surface = surface_1ed555cf()

    obfuscation_surface = obfuscation_1ed555cf()

    operation_plan = ("python_to_wscript", fields["file_path"], fields["next_stage"])

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_1ed555cf())

