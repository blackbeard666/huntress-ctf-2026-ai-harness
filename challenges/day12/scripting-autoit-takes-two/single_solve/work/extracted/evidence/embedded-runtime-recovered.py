#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_6662ab5a = ("PQAyTj1JLFwvEnYTcB97HkEiTSNFLEs+TC1ZMF8xHXEefRxoDVI7VSFENkY0USVAMh56E2AQcQVmDlE/WiJWCXoObwhtEXAUdQVxFGZbK1ImTiFPEGQLVCRLPFkrW"
    "DBVOVUpWi5PKE0ScR5rBXFMfwNwCWcTcgo3VDhZKlkGdQFgFH0ecxZiCmUBfRJwFmMQcxJmD2AOM14/TT5WN1sEYQ95HHAfbwpVJUkoRjpZOEo4UTRGex5zEXQQdB"
    "V3G34hUShcNFs1ahhtA3cecxZqHXQafhFmFUopQSBJJxpoDWMCbwpuMVg2QidVJVcyRiNRLU4vQjJTOl0zbAVhXD9eM0MiSyxCbwtqU2BSYVRiVDZKLEUpTBNjAnY"
    "eI2BadSVXOF8tTCFlBHARPnYDbRlrDn0OQiNBbkA1RSFANFF8GHlAc0FyR3FHJQt7An4QdQ15JlUhQCdCfw92F2UIZxU4SDFYNkUxUDxQNUdqGH0ecQdiEHURP082")
CODEC_6662ab5a = "base64_chunks|rolling_xor|4b"

def load_6662ab5a():
    return base64.b64decode(MATERIAL_6662ab5a)

def decode_6662ab5a(stored_bytes):
    recovered_bytes = bytearray()
    prior_byte = 75
    for value in stored_bytes:
        recovered_bytes.append(value ^ prior_byte)
        prior_byte = value
    return bytes(recovered_bytes)

def recover_6662ab5a():
    harmless_value = (3, 5, 8, 13)[1:3]
    recovered_bytes = decode_6662ab5a(load_6662ab5a())
    configuration_text = recovered_bytes.decode("ascii", "strict")
    return configuration_text

def inspect_6662ab5a():
    view = memoryview(recover_6662ab5a().encode("ascii"))
    return bytes(view).decode("ascii")

class Surface_surface_6662ab5a:
    @staticmethod
    def recover():
        return ("class_staticmethod", "marshal_envelope_plan", "embeddable_python_runtime", "renamed_interpreter")

def surface_6662ab5a():
    return Surface_surface_6662ab5a.recover()

def obfuscation_6662ab5a():
    marshal_plan = {"format": "code_object", "action": "inspect_only", "label": "marshal_envelope_plan"}
    return marshal_plan["label"]

def plan_6662ab5a():
    fields = dict(item.split("=", 1) for item in inspect_6662ab5a().split("|"))
    analysis_surface = surface_6662ab5a()
    obfuscation_surface = obfuscation_6662ab5a()
    operation_plan = ("python_to_powershell", fields["file_path"], fields["next_stage"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_6662ab5a())
