# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_d0447bbd = [145, 232, 152, 182, 134, 183, 134, 224, 210, 235, 138, 179, 209, 230, 203, 174, 218, 187, 223, 175, 218, 244, 219, 185, 216, 148, 231, 148, 241, 131, 247, 153, 236, 164, 139, 234, 158, 255, 187, 214, 183, 197, 162, 205, 191, 239, 192, 250, 185, 132, 236, 152, 249, 137, 214, 179, 223, 182, 208, 172, 156, 173, 156, 250, 200, 241, 144, 169, 203, 252, 209, 191, 216, 177, 208, 160, 205, 172, 207, 242, 150, 255, 160, 206, 169, 192, 161, 209, 188, 221, 190, 194, 176, 213, 161, 196, 182, 198, 180, 209, 165, 203, 162, 253, 153, 252, 145, 240, 158, 251, 137, 180, 218, 179, 210, 186, 217, 134, 245, 130, 237, 137, 231, 142, 249, 133, 189, 142, 209, 178, 203, 187, 228, 128, 229, 150, 247, 149, 202, 162, 209, 176, 216, 229, 151, 242, 155, 233, 155, 250, 153, 229, 128, 236, 142, 239, 155, 196, 163, 205, 164, 214, 162, 209, 236, 130, 237, 132, 240, 145, 242, 129, 244, 146, 240, 159, 227, 135, 232, 128, 244, 145, 252, 159, 246, 130, 227, 151, 228, 187, 200, 187, 218, 182, 213, 232, 144, 241, 133, 235, 146, 225, 157, 172, 145, 229, 139, 254, 145, 242, 173, 200, 175, 206, 186, 201, 181, 198, 163, 215, 174, 204, 147, 246, 130, 235, 153, 238, 177, 217, 173, 204, 188, 129, 243, 150, 226, 146, 243, 151, 246, 138, 239, 131, 234, 140, 211, 182, 194, 171, 217, 174, 130, 230, 131, 231, 131, 230, 132, 233, 140, 211, 182, 210, 189, 222, 187, 223, 226, 145, 225, 132, 240, 131, 255, 205, 240]
CODEC_d0447bbd = "reversed_integer_list|rolling_xor|86"

def load_d0447bbd():
    return bytes(reversed(MATERIAL_d0447bbd))

def decode_d0447bbd(EnCoDeD_Bytes):
    DeCoDeD_Bytes = bytearray()
    PrEvIoUs = 134
    for value in EnCoDeD_Bytes:
        DeCoDeD_Bytes.append(value ^ PrEvIoUs)
        PrEvIoUs = value
    return bytes(DeCoDeD_Bytes)

def recover_d0447bbd():
    NeUtRaL = 19 * 7 - 133
    for _pass in range(1):
        DeCoDeD_Bytes = decode_d0447bbd(load_d0447bbd())
    DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")
    return DeScRiPtOr_Text

def inspect_d0447bbd():
    stream = io.BytesIO(recover_d0447bbd().encode("ascii"))
    return stream.read().decode("ascii")

class Surface_surface_d0447bbd:
    @staticmethod
    def recover():
        return ("class_staticmethod", "string_table", "hash_based_pyc_38", "renamed_interpreter")

def surface_d0447bbd():
    return Surface_surface_d0447bbd.recover()

def obfuscation_d0447bbd():
    table = ("strin", "g_table")
    return "".join(table)

def plan_d0447bbd():
    fields = dict(item.split("=", 1) for item in inspect_d0447bbd().split("|"))
    analysis_surface = surface_d0447bbd()
    obfuscation_surface = obfuscation_d0447bbd()
    operation_plan = ("path_write_bytes", "decode", fields["file_path"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_d0447bbd())

# reconstruction complete