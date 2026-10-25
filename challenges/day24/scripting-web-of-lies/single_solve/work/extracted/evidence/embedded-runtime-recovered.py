#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_8a52dce5 = "ZCsgamFiU15hK1JTUV1SU01RXVxUV1VjYE9iV11cGlpdUU9iU01XXGJTYF5gU2JTYBpSV2FeT2JRVk1cU2ZiTWFiT1VTak9ST15iU2ArXmdiVl1cTWJdTV5dZVNgYVZTWlpqYWJPVVNNUV1jXGIrIWphZ1xiT2YrUVpPYWFNYWJPYldRW1NiVl1Sal1QVGNhUU9iV11cK1tPYGFWT1pNU1xkU1pdXlNNXlpPXGpRT2BgV1NgK1NbUFNSUk9QWlNNXmdiVl1cTWBjXGJXW1NqZVdcUl1lYU1RVk9XXCtgU1xPW1NSTVdcYlNgXmBTYlNgalFPW15PV1VcTVdSK1FPW15PV1VcGyNQUR4jIiJTJFBqVFdaU01eT2JWKzEoHT5gXVVgT1syT2JPHTZjXGJgU2FhOk9QHRxjXlJPYlMbI1BRHiMiIlMkUBxeZ2pcU2ZiTWFiT1VTK15nT2BbXWAbXmdXXGFiT1paU2AbYFNRXWRTYFNSHF5n"
CODEC_8a52dce5 = "base64_literal|subtract_modulo_256|12"

def load_8a52dce5():
    return base64.b64decode(MATERIAL_8a52dce5)

def decode_8a52dce5(EnCoDeD_Bytes):
    return bytes((value + 18) % 256 for value in EnCoDeD_Bytes)

def recover_8a52dce5():
    NeUtRaL = (3, 5, 8, 13)[1:3]
    for _pass in range(1):
        DeCoDeD_Bytes = decode_8a52dce5(load_8a52dce5())
    DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")
    return DeScRiPtOr_Text

def inspect_8a52dce5():
    return recover_8a52dce5()

class Surface_surface_8a52dce5:
    @staticmethod
    def recover():
        return ("class_staticmethod", "marshal_envelope_plan", "embeddable_python_runtime", "renamed_interpreter")

def surface_8a52dce5():
    return Surface_surface_8a52dce5.recover()

def obfuscation_8a52dce5():
    marshal_plan = {"format": "code_object", "action": "inspect_only", "label": "marshal_envelope_plan"}
    return marshal_plan["label"]

def plan_8a52dce5():
    fields = dict(item.split("=", 1) for item in inspect_8a52dce5().split("|"))
    analysis_surface = surface_8a52dce5()
    obfuscation_surface = obfuscation_8a52dce5()
    operation_plan = ("python_to_powershell", fields["file_path"], fields["next_stage"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_8a52dce5())
