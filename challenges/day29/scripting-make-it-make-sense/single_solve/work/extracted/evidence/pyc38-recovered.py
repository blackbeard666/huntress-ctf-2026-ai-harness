# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_0f07441a = [215, 174, 222, 240, 200, 171, 153, 248, 193, 246, 207, 170, 147, 247, 218, 191, 203, 170, 206, 190, 203, 229, 202, 168, 201, 133, 246, 133, 224, 146, 230, 136, 253, 181, 154, 251, 143, 238, 170, 199, 166, 212, 179, 220, 174, 254, 209, 235, 168, 149, 253, 137, 232, 152, 199, 162, 206, 167, 193, 189, 133, 230, 212, 181, 140, 187, 130, 231, 222, 186, 151, 249, 158, 247, 150, 230, 139, 234, 137, 180, 208, 185, 230, 136, 239, 134, 231, 151, 250, 155, 248, 132, 246, 147, 231, 130, 240, 128, 242, 151, 227, 141, 228, 187, 223, 186, 215, 182, 216, 189, 207, 242, 156, 245, 148, 252, 159, 192, 179, 196, 171, 207, 161, 200, 191, 195, 251, 200, 151, 244, 141, 253, 162, 198, 163, 208, 177, 211, 140, 228, 151, 246, 158, 163, 209, 180, 221, 175, 221, 188, 223, 163, 198, 170, 200, 169, 221, 130, 229, 139, 226, 144, 228, 151, 170, 196, 171, 194, 182, 215, 180, 199, 178, 212, 182, 217, 165, 193, 174, 198, 178, 215, 186, 217, 176, 196, 165, 209, 162, 253, 142, 253, 156, 240, 147, 174, 214, 183, 195, 173, 212, 167, 219, 234, 215, 163, 205, 184, 215, 180, 235, 142, 233, 136, 252, 143, 243, 150, 245, 148, 248, 136, 237, 159, 192, 165, 201, 160, 198, 182, 219, 190, 202, 247, 133, 224, 148, 228, 133, 225, 128, 252, 153, 245, 156, 250, 165, 192, 180, 221, 175, 216, 244, 144, 245, 145, 245, 144, 242, 159, 250, 165, 192, 164, 203, 168, 205, 169, 148, 231, 151, 242, 134, 245, 137, 187, 134]
CODEC_0f07441a = "reversed_integer_list|rolling_xor|f0"

def load_0f07441a():
    return bytes(reversed(MATERIAL_0f07441a))

def decode_0f07441a(stored_bytes):
    recovered_bytes = bytearray()
    prior_byte = 240
    for value in stored_bytes:
        recovered_bytes.append(value ^ prior_byte)
        prior_byte = value
    return bytes(recovered_bytes)

def recover_0f07441a():
    harmless_value = (3, 5, 8, 13)[1:3]
    for _pass in range(1):
        recovered_bytes = decode_0f07441a(load_0f07441a())
    configuration_text = recovered_bytes.decode("ascii", "strict")
    return configuration_text

def inspect_0f07441a():
    stream = io.BytesIO(recover_0f07441a().encode("ascii"))
    return stream.read().decode("ascii")

class Surface_surface_0f07441a:
    @staticmethod
    def recover():
        return ("class_staticmethod", "string_table", "hash_based_pyc_38", "renamed_interpreter")

def surface_0f07441a():
    return Surface_surface_0f07441a.recover()

def obfuscation_0f07441a():
    table = ("strin", "g_table")
    return "".join(table)

def plan_0f07441a():
    fields = dict(item.split("=", 1) for item in inspect_0f07441a().split("|"))
    analysis_surface = surface_0f07441a()
    obfuscation_surface = obfuscation_0f07441a()
    operation_plan = ("tempfile_replace", "decode", fields["file_path"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_0f07441a())

# reconstruction complete