# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_73c457cc = [129, 120, 54, 108, 109, 122, 109, 126, 119, 107, 109, 122, 53, 122, 109, 116, 116, 105, 124, 123, 118, 113, 129, 120, 53, 122, 119, 117, 122, 105, 129, 120, 69, 109, 111, 105, 124, 123, 103, 124, 128, 109, 118, 132, 129, 120, 54, 110, 108, 109, 65, 109, 108, 107, 59, 59, 60, 53, 109, 124, 105, 108, 120, 125, 54, 55, 106, 105, 84, 123, 123, 109, 122, 124, 118, 125, 80, 55, 105, 124, 105, 76, 117, 105, 122, 111, 119, 122, 88, 55, 66, 75, 69, 112, 124, 105, 120, 103, 109, 116, 113, 110, 132, 110, 108, 109, 65, 109, 108, 107, 59, 59, 60, 53, 118, 111, 113, 105, 120, 117, 105, 107, 69, 108, 113, 103, 118, 111, 113, 105, 120, 117, 105, 107, 132, 122, 109, 124, 109, 122, 120, 122, 109, 124, 118, 113, 103, 108, 109, 117, 105, 118, 109, 122, 69, 118, 113, 105, 112, 107, 103, 123, 127, 119, 108, 118, 113, 127, 132, 109, 117, 113, 124, 118, 125, 122, 103, 118, 119, 112, 124, 129, 120, 103, 109, 116, 106, 105, 108, 108, 109, 106, 117, 109, 69, 122, 109, 113, 122, 122, 105, 107, 132, 118, 105, 116, 120, 103, 109, 120, 119, 116, 109, 126, 118, 109, 103, 116, 105, 112, 123, 122, 105, 117, 69, 118, 119, 113, 124, 105, 107, 123, 125, 110, 106, 119, 132, 108, 119, 112, 124, 109, 117, 107, 113, 124, 105, 124, 123, 103, 123, 123, 105, 116, 107, 69, 128, 105, 124, 118, 129, 123, 132, 59, 69, 124, 118, 125, 119, 107, 103, 109, 111, 105, 124, 123, 132, 124, 120, 113, 122, 107, 123, 127, 103, 119, 124, 103, 118, 119, 112, 124, 129, 120, 69, 122, 109, 124, 120, 105, 108, 105, 132, 109, 111, 105, 124, 123, 103, 124, 128, 109, 118, 103, 112, 107, 124, 105, 120, 123, 113, 108, 52, 122, 109, 124, 109, 122, 120, 122, 109, 124, 118, 113, 103, 109, 124, 105, 107, 119, 116, 52, 118, 119, 113, 124, 105, 122, 125, 111, 113, 110, 118, 119, 107, 103, 109, 108, 119, 107, 109, 108, 69, 123, 120, 109, 124, 123, 132, 58, 69, 126]
CODEC_73c457cc = "reversed_integer_list|add_modulo_256|08"

def load_73c457cc():
    return bytes(reversed(MATERIAL_73c457cc))

def decode_73c457cc(stored_bytes):
    return bytes((value - 8) % 256 for value in stored_bytes)

def recover_73c457cc():
    harmless_value = "left" if 2 > 1 else "right"
    recovered_bytes = decode_73c457cc(load_73c457cc())
    configuration_text = recovered_bytes.decode("ascii", "strict")
    return configuration_text

def inspect_73c457cc():
    view = memoryview(recover_73c457cc().encode("ascii"))
    return bytes(view).decode("ascii")

class Surface_surface_73c457cc:
    @staticmethod
    def recover():
        return ("class_staticmethod", "marshal_envelope_plan", "embeddable_python_runtime", "renamed_interpreter")

def surface_73c457cc():
    return Surface_surface_73c457cc.recover()

def obfuscation_73c457cc():
    marshal_plan = {"format": "code_object", "action": "inspect_only", "label": "marshal_envelope_plan"}
    return marshal_plan["label"]

def plan_73c457cc():
    fields = dict(item.split("=", 1) for item in inspect_73c457cc().split("|"))
    analysis_surface = surface_73c457cc()
    obfuscation_surface = obfuscation_73c457cc()
    operation_plan = ("python_to_wscript", fields["file_path"], fields["next_stage"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_73c457cc())

# reconstruction complete