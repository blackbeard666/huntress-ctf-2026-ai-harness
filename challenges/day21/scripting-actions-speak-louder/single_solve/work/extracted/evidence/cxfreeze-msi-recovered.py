# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_23a9dbef = "dj0yfHN0ZXBzPWRlY29kZV9lbWJlZGRlZCx3cml0ZV9maWxlfGFkYXB0ZXI9b3Blbl9iaW5hcnlfd3JpdGV8c3RhZ2VfY291bnQ9MXxzeW50YXg9aXRlcmF0b3JfcHJvdG9jb2x8b2JmdXNjYXRpb249cmVmbGVjdGl2ZV9uYW1lX3BsYW58Y2Fycmllcj1jeF9mcmVlemVfbXNpfHdpbmRvd3NfY2hhaW49cnVuX2tleV9kZXNjcmlwdG9yfGNhbXBhaWduX2lkPWNhbXBhaWduLTExZTdmMTMwOWN8ZmlsZV9wYXRoPUM6L1Byb2dyYW1EYXRhL0h1bnRyZXNzTGFiLy51cGRhdGUtMTFlN2YxMzA5Yy5weQ=="
CODEC_23a9dbef = "urlsafe_base64|identity|"

def load_23a9dbef():
    return base64.urlsafe_b64decode(MATERIAL_23a9dbef)

def decode_23a9dbef(stored_bytes):
    return bytes(stored_bytes)

def recover_23a9dbef():
    harmless_value = (3, 5, 8, 13)[1:3]
    decode_state = "decode"
    while decode_state != "done":
        if decode_state == "decode":
            recovered_bytes = decode_23a9dbef(load_23a9dbef())
            decode_state = "done"
    configuration_text = recovered_bytes.decode("ascii", "strict")
    return configuration_text

def inspect_23a9dbef():
    view = memoryview(recover_23a9dbef().encode("ascii"))
    return bytes(view).decode("ascii")

def surface_23a9dbef():
    iterator = iter(("iterator_protocol", "reflective_name_plan", "cx_freeze_msi", "run_key_descriptor"))
    return tuple(iterator)

def obfuscation_23a9dbef():
    reflection_plan = ("__import__", "getattr", "reflective_name_plan")
    return reflection_plan[-1]

def plan_23a9dbef():
    fields = dict(item.split("=", 1) for item in inspect_23a9dbef().split("|"))
    analysis_surface = surface_23a9dbef()
    obfuscation_surface = obfuscation_23a9dbef()
    operation_plan = ("open_binary_write", "decode", fields["file_path"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_23a9dbef())

# reconstruction complete